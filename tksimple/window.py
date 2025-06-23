import tkinter as _tk
from typing import Callable, Union
from random import randint as _randint
from time import time
from traceback import format_exc

from .event import _EventRegistry, _EventHandler
from .util import _TaskScheduler, runWatcherDec, WidgetGroup, remEnum, ifIsNone
from .const import *
from .tkmath import Location2D, _map
from .image import TkImage, PILImage

class Tk:
    """
    The toplevel window class

    """
    def __init__(self, _master=None, group=None):
        self._hasTaskBar = False
        self._instanceOfMenu = False
        self._destroyed = False
        self._placed = True
        self._oldWindowSize = (-1, -1) # for filtering on resize Event
        self._privOldWindowSize = (-1, -1) # for filtering internal on resize Event
        self._internWindowSize = None  # for centering Window on Screen
        self._title = ""               # if sub widow title is not set take from main window
        self._closeRunnable = None     # internal on Close Event runnable
        
        self._eventRegistry = _EventRegistry(self)
        self._childWidgets = []

        self._master = _tk.Tk() if _master is None else _master

        self._relativePlaceData = {
            "handler": None
        }

        # configure internal onCloseEvent
        self._master.protocol("WM_DELETE_WINDOW", self._internalOnClose)
        
        if group is not None: group.add(self)
    def __str__(self):
        return str(self.__class__.__name__)+"("+str()+")"
    # Task Scheduler
    def runTask(self, func)->_TaskScheduler:
        task = _TaskScheduler(self, 0, func)
        return task
    def runTaskAfter(self, func, time_)->_TaskScheduler:
        task = _TaskScheduler(self, time_, func)
        return task
    def runIdleLoop(self, func)->_TaskScheduler:
        task = _TaskScheduler(self, 0, func, repete=True)
        return task
    def runDelayLoop(self, func, delay)->_TaskScheduler:
        task = _TaskScheduler(self, delay, func, repete=True)
        return task
    def runDynamicDelayLoop(self, delay, func)->_TaskScheduler:
        task = _TaskScheduler(self, delay, func, repete=True, dynamic=True)
        return task
    # Custom Events
    def onWindowResize(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False, filterEvent=True):
        _EventHandler._registerNewEvent(self, func, EventType.key("<Configure>"), args, priority, decryptValueFunc=(self._decryptWindowResize if filterEvent else self._decryptNonFilteredWindowResize), defaultArgs=defaultArgs, disableArgs=disableArgs)
    def onCloseEvent(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False):
        """
        This Event is triggered if the user close the window or press Alt+F4.


        @param func:
        @param args:
        @param priority:
        @param defaultArgs:
        @param disableArgs:
        @return:
        """
        self._closeRunnable = _EventHandler._getNewEventRunnable(self, func, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs)
        return self._closeRunnable
    def bind(self, func:Callable, event:Union[EventType, Key, Mouse, str], args:list=None, priority:int=0, defaultArgs=False, disableArgs=False):
        """
        Binds a specific event to the Window. Runs given function on trigger.

        @param func: function get called on trigger
        @param event: Event type: EventType _Enum or default tkinter event as string.
        @param args: Additional arguments as List.
        @param priority: If several equal events are bound, it's possible to set priorities.
        @param defaultArgs: if True the default tkinter gets passed in bound function instead of Event-instance.
        @param disableArgs: if True no args gets passed.
        @return:
        """
        if event == "CANCEL": return
        event = remEnum(event)
        if event.startswith("["):
            _EventHandler._registerNewCustomEvent(self, func, event, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs)
        else:
            _EventHandler._registerNewEvent(self, func, event, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs)
    # Event Tweaks
    def unbindEvent(self, event: Union[EventType, Key, Mouse]):
        """
        Unbinds all Events from given EventType.

        @param event:
        @return:
        """
        # self._eventRegistry.unregisterType(event)
        raise NotImplemented()
    def unbindAllEvents(self):
        """
        Unbind all Events.

        @return:
        """
        # self._eventRegistry.unregisterAll()
        raise NotImplemented()
    # Cursor
    def setCursor(self, c:Union[Cursor, str]):
        """
        Set cursor image from Cursor _Enum or default tkinter string.

        @note only predefined cursors are implemented yet
        @param c:
        @return:
        """
        self._setAttribute("cursor", remEnum(c))
        return self
    def hideCursor(self):
        """
        Hides the current Cursor within the Window.
        Use 'setCursor' to show the Cursor

        @return:
        """
        self._setAttribute("cursor", "none")
        return
    # Quit & Close
    def closeViaESC(self):
        """
        Destroys the window via pressing ESC-key.
        Only if the setCanceled in the 'onCloseEvent' is False!
        @return:
        """
        assert self._closeRunnable is not None, "Bind 'onCloseEvent' Event first!"
        self.bind(self._closeRunnable, EventType.ESC)
        return self
    def destroyViaESC(self):
        """
        Destroys the window via pressing ESC-key.
        @return:
        """
        self.bind(self.destroy, EventType.ESC)
        return self
    def close(self):
        """
        Closes the window only if it was not prevented in the 'windowCloseEvent' with the setCanceled.

        @return:
        """
        if self._closeRunnable is None:
            self.destroy()
        else:
            self._closeRunnable()
    def quitMainLoop(self):
        """
        Quit the Window. BUT the Window mainloop is still running.

        @return:
        """
        self._master.quit()
    # Appearance
    def forceFocus(self):
        """
        Forces the focus to this WIndow.
        @return:
        """
        self._master.focus_force()
        return self
    def hide(self):
        """
        Minimizees the Window.
        @return:
        """
        self._master.withdraw()
    def show(self):
        """
        Maximizes the Window.
        @return:
        """
        self._master.deiconify()
    def lift(self):
        """
        Lifts the Window on top of all other Windows.
        @return:
        """
        self._master.lift()
        return self
    def destroy(self):
        """
        Destroys the Tkinter Window. Ignores the 'onCloseEvent'.

        @return:
        """
        try:
            self._destroyed = True
            WidgetGroup.removeFromAll(self)
            for w in self._childWidgets.copy(): # TODO remove copy
                w.destroy()
            self._master.destroy()
            return True
        except Exception as e:
            if WIDGET_DELETE_DEBUG or True:
                print("FAIL!", e)
                print(format_exc())
            return False
    def setDisabled(self):
        self._master.wm_attributes("-disabled", True)
        return self
    def setEnabled(self):
        self._master.wm_attributes("-disabled", False)
        return self
    def overrideredirect(self, b:bool=True):
        self._master.overrideredirect(b)
        return self
    def centerWindowOnScreen(self, forceSetSize=False):
        """
        Centers the Window on screen

        @param forceSetSize: get the Parameters from 'setWindowSize' function and not from tkinter
        @return:
        """
        width, height = self.getWindowSize()
        if width == 1 or forceSetSize:
            if self._internWindowSize is not None:
                width, height = self._internWindowSize
            else:
                raise TKExceptions.InvalidUsageException("Run the mainloop first or specify a window size manually to center the Window!")
        swidth , sheight = self.getScreenSize()
        nwidth = int(round((swidth/2-width/2), 0))
        nheight = int(round((sheight/2-height/2), 0))
        self.setPositionOnScreen(nwidth, nheight)
        return self
    # Update
    def update(self):
        """
        Updates the Window.

        @return:
        """
        self._master.update()
        return self
    def updateIdleTasks(self):
        """
        Updates the IDLE-Tasks.

        @return:
        """
        self._master.update_idletasks()
        return self
    # Setter
    def setFocus(self):
        """
        Sets the focus to this Window.

        @return:
        """
        self._master.focus_set()
        return self
    def setIcon(self, icon:Union[TkImage, PILImage]):
        """
        Sets the icon in the top left corner from the Window.

        @param icon:
        @return:
        """
        self._master.iconphoto(True, icon._get())
        return self
    def setBg(self, col:Union[Color, str]):
        """
        Set the Background Color of the Window.

        @param col: Use Color _Enum, tkinter string or hex-code.
        @return:
        """
        self._setAttribute("bg", remEnum(col))
        return self
    def setTopmost(self, b=True):
        """
        Sets the "Always on top" attribute.

        @param b:
        @return:
        """
        self._master.wm_attributes("-topmost", b)
    def setResizeable(self, b:bool):
        """
        Defines if the Window can be resized.

        @param b:
        @return:
        """
        self._master.resizable(b, b)
        return self
    def setFullscreen(self, b:bool=True):
        """
        Sets the Window in Fullscreen mode.

        @param b:
        @return:
        """
        self._master.wm_attributes("-fullscreen", b)
    def setPositionOnScreen(self, x:Union[int, Location2D], y:Union[None, int]=None):
        """
        Set the Window position of the upper left corner on screen.


        @param x:
        @param y:
        @return:
        """
        if isinstance(x, Location2D):
            x, y = x.get()
        elif y is None:
            raise TypeError("y cannot be None!")
        if str(x).find("-") == -1: x = "+" + str(x)
        if str(y).find("-") == -1: y = "+" + str(y)
        self._master.geometry(str(x) + str(y))
    def setCloseable(self, b:bool):
        """
        If b is True -> Window cannot be closed
        If b is False -> Window can normally close

        @param b:
        @return:
        """
        self._master.protocol("WM_DELETE_WINDOW", b)
    def setTitle(self, title):
        """
        Sets the Window title.

        @param title:
        @return:
        """
        self._title = title
        self._master.title(title)
        return self
    def setTransparent(self, color:Union[Color, str]):
        """
        Defines given color as Transparent.

        @param color:
        @return:
        """
        self._master.wm_attributes("-transparentcolor", remEnum(color))
        return self
    def setWindowSize(self, x:int, y:int, minsize=False):
        """
        Set the Windowsize. Can also set the 'minsize'.

        @param x:
        @param y:
        @param minsize:
        @return:
        """
        self._internWindowSize = (x, y)
        if minsize: self.setMinSize(x, y)
        self._master.geometry(str(x) + "x" + str(y))
    def setMaxSize(self, x, y):
        """
        Set the maximal Windowsize.

        @param x:
        @param y:
        @return:
        """
        self._master.maxsize(x, y)
    def setMinSize(self, x, y):
        """
        Set the minimum Windowsize.

        @param x:
        @param y:
        @return:
        """
        self._master.minsize(x, y)
    # Getter
    def getPositionOnScreen(self)->Location2D:
        return Location2D(
            self._master.winfo_rootx(),
            self._master.winfo_rooty()
        )
    def getMousePositionRelativeToScreen(self)->Location2D:
        """
        Returns the current mouse position relative to Screen.
        @return:
        """
        return Location2D(
            self._master.winfo_pointerx(),
            self._master.winfo_pointery()
        )
    def getMousePosition(self)->Location2D:
        """
        Returns the current mouse position on the TK window.
        @return:
        """
        return Location2D(self._master.winfo_pointerx() - self._master.winfo_rootx(), self._master.winfo_pointery() - self._master.winfo_rooty())
    def getWidgetFromLocation(self, loc:Location2D):
        #for widget in self._getAllChildWidgets(self):
        #    if widget._get()
        #print(*loc.get())
        #widget = self._master.winfo_containing(*loc.get())
        #return widget
        raise NotImplemented()
    def getHeight(self):
        """
        Returns the Window height.

        @return:
        """
        return self._master.winfo_height()
    def getWidth(self):
        """
        Returns the Window width.

        @return:
        """
        return self._master.winfo_width()
    def getScreenSize(self):
        """
        Returns the Screen width and height as tuple.

        @return:
        """
        return self._master.winfo_screenwidth(), self._master.winfo_screenheight()
    def getWindowSize(self):
        """
        Returns the Window width and height as tuple.

        @return:
        """
        return self._master.winfo_width(), self._master.winfo_height()
    def getParentWindow(self):
        """
        Returns Parent Master instance. Tk, Toplevel or Dialog.
        """
        return self._getTkMaster()
    # Fix
    def clearAllWidgets(self):
        """
        Destroys all Widgets in the Window.

        @return:
        """
        #for i in self._master.winfo_children():
        #    i.destroy()
        raise NotImplemented()
    def activeWidgets(self): #@TODO: FIX!
        #for i in self._master.winfo_children():
        #    yield i
        raise NotImplemented()
    # Mainloop
    def mainloop(self):
        """
        Starts the Window mainloop.
        Call this Method after the creation of all Widgets to open/start the Window.
        All code after the mainloop is only executed if the Window is terminated.

        @return:
        """
        self._mainloop()
    # Misc
    def throwErrorSound(self):
        self._master.bell()
        return self
    def copyToClip(self, s):
        self._master.clipboard_append(str(s))
        return self
    def clearClip(self):
        self._master.clipboard_clear()
        return self
    def getClip(self):
        return self._master.clipboard_get()
    def sleep(self, s):
        """
        Sleeps s seconds and updates the window in Background.
        @param s:
        @return:
        """
        temp = time()
        while True:
            if not self._destroyed: self.update()
            if time()-temp >= s:
                break
        return self
    # Private Implementations
    def _mainloop(self):
        """
        Private Implementations of 'mainloop' call.
        @return:
        """
        if self._destroyed: return
        self._finishLastTasks()
        self._master.mainloop()
        self._destroyed = True
    def _updateDynamicSize(self, widget):
        """
        Private implementation of the 'updateDynamicWidgets'.
        @param widget:
        @return:
        """
        if not widget._destroyed and len(widget._relativePlaceData) > 1:
            _data = widget._relativePlaceData
            masterWidth = widget._master.getWidth()
            masterHeight = widget._master.getHeight()


            x = ifIsNone(_data["fixX"], _map(_data["xOffset"] + _data["xOffsetLeft"], 0, 100, 0, masterWidth))
            y = ifIsNone(_data["fixY"], _map(_data["yOffset"] + _data["yOffsetUp"], 0, 100, 0, masterHeight))

            width = _data["fixWidth"]
            if width is None:
                offset = _map(_data["xOffset"] + _data["xOffsetRight"], 0, 100, 0, masterWidth)
                width = masterWidth - offset - x
                if widget._yScrollbar is not None and widget._yScrollbar._autoPlace:
                    width -= widget._yScrollbar._thickness

            height = _data["fixHeight"]
            if height is None:
                offset = _map(_data["yOffset"] + _data["yOffsetDown"], 0, 100, 0, masterHeight)
                height = masterHeight - offset - y
                if widget._xScrollbar is not None and widget._xScrollbar._autoPlace:
                    height -= widget._xScrollbar._thickness

            #width = ((masterWidth - _map(_data["xOffset"] + _data["xOffsetRight"], 0, 100, 0, masterWidth) - x) - (widget._yScrollbar._thickness if widget._yScrollbar is not None and widget._yScrollbar._autoPlace else 0) if _data["fixWidth"] is None else _data["fixWidth"])
            #height = ((masterHeight - _map(_data["yOffset"] + _data["yOffsetDown"], 0, 100, 0, masterHeight) - y) - (widget._xScrollbar._thickness if widget._xScrollbar is not None and widget._xScrollbar._autoPlace else 0) if _data["fixHeight"] is None else _data["fixHeight"])

            if _data["stickRight"]:
                x = masterWidth-width
            if _data["stickDown"]:
                y = masterHeight-height
            if _data["centerX"] or _data["center"]:
                x = int(round(masterWidth/2 - width/2, 0))
            if _data["centerY"] or _data["center"]:
                y = int(round(masterHeight/2 - height/2, 0))

            width += _data["changeWidth"]
            height += _data["changeHeight"]

            x += _data["changeX"]
            y += _data["changeY"]

            widget._get().place(x=x,
                                y=y,
                                width=width,
                                height=height,
                                anchor=Anchor.UP_LEFT.value)

            handler = _data["handler"]
            if handler is not None:
                for event in widget._eventRegistry.getCallables("[relative_update]"):
                    event["value"] = [x, y, width, height]
                handler()

            if widget._xScrollbar is not None and widget._xScrollbar._autoPlace:
                widget._xScrollbar.place(x, y + height, width=width)

            if widget._yScrollbar is not None and widget._yScrollbar._autoPlace:
                widget._yScrollbar.place(x + width, y, height=height)

            if handler is not None:
                for event in widget._eventRegistry.getCallables("[relative_update_after]"):
                    event["value"] = [x, y, width, height]
                handler()
    def updateDynamicWidgets(self, start=None):
        """
        Call this method to update all relative placed Widgets
        which are placed with 'placeRelative' manager.

        @return:
        """
        def updateRecursive(widget):
            if not hasattr(widget, "_childWidgets"):
                self._updateDynamicSize(widget)
                return

            for w in widget._childWidgets:
                if w._destroyed: continue
                if not w._placed:
                    continue
                self._updateDynamicSize(w)
                if hasattr(w, "_childWidgets"):  # is container?
                    updateRecursive(w)
        updateRecursive(self if start is None else start)
        return self
    def _internalOnClose(self):
        """
        internal onClose Event.
        @return:
        """
        #print("Internal Close")
        if self._closeRunnable is None:
            self.destroy()
        else:
            runnable = self._closeRunnable
            runnable()
            if not runnable.event["setCanceled"]:
                self.destroy()
    def _decryptWindowResize(self, args, event):
        _size = self.getWindowSize()
        if self._oldWindowSize == _size:
            return "CANCEL"
        else:
            self._oldWindowSize = _size
            return _size
    def _decryptNonFilteredWindowResize(self, args, event):
        return self.getWindowSize()
    def _privateDecryptWindowResize(self, args, event):
        _size = self.getWindowSize()
        if self._privOldWindowSize == _size:
            return "CANCEL"
        else:
            self._privOldWindowSize = _size
            return _size
    def _finishLastTasks(self):
        _EventHandler._registerNewEvent(self, self._customUpdateDynamicWidgetsHandler, EventType.SIZE_CONFIUGURE, args=[], priority=1, decryptValueFunc=self._privateDecryptWindowResize)
        self.updateDynamicWidgets()
    def _setAttribute(self, name, value):
        if self._destroyed: return
        try:
            self._master[name] = value
        except Exception as e:
            value = repr(value)
            valType = type(value)
            value = value[0:50]+"..." if len(str(value)) > 50 else value
            raise AttributeError("Could not set Attribute of Widget "+str(type(self._master))+"!\n\tKEY: '"+str(name)+"'\n\tVALUE["+str(valType)+"]: '"+str(value)+"'\n"+str(self)+" \n\tTKError: "+str(e))
    @runWatcherDec
    def _customUpdateDynamicWidgetsHandler(self, e):
        if self._destroyed: return
        self.updateDynamicWidgets()
    def _getTkMaster(self):
        """
        Returns the highest master (Tk/Toplevel) of this widget.

        @return:
        """
        return self
    def _get(self):
        return self._master
class Toplevel(Tk):
    """
    Toplevel window.
    Pass 'Tk' for _master to Use 'Toplevel' as 'Tk-class'.
    This allows to use Toplevel as standalone and as Toplevel window above another application.
    """
    def __init__(self, _master, group=None, topMost=True):

        self._tkMaster = _master

        super().__init__(
            _master=_tk.Toplevel(_master._get()),
            group=group
        )
        self._finishLastTasks()
        if topMost: self.setTopmost()
    def mainloop(self):
        """
        Mainloop in Toplevel not used!

        @return:
        """
class Dialog(Toplevel):
    """
    Similar to Toplevel.
    Master of this dialog is disabled until dialog is closed.
    Dialog is topmost on default.
    Dialog is hidden on default. (use .show())
    """
    def __init__(self, _master, group=None, topMost=True):
        super().__init__(_master, group, topMost)
        self._shown = False

        self._get().grab_release()
        self._master.withdraw()
        self._get().transient()
    def show(self, waitVisibility=True):
        """
        Shows the dialog.

        @return:
        """
        assert not self._shown, "Dialog is already Visible!"
        self._shown = True

        self._master.deiconify()
        if waitVisibility: self._get().wait_visibility()
        self._get().grab_set()
    def hide(self):
        """
        Hides the dialog.

        @return:
        """
        assert self._shown, "Dialog is already Hidden!"
        self._shown = False

        self._get().grab_release()
        self._master.withdraw()
