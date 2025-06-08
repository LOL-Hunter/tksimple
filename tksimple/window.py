import tkinter as _tk
from typing import Callable, Union
from random import randint as _randint
from time import time
from traceback import format_exc

from .event import _EventRegistry, _EventHandler
from .util import _TaskScheduler, runWatcherDec, WidgetGroup, _isinstance, _getAllChildWidgets
from .const import *
from .tkmath import Location2D, _map
from .image import TkImage, PILImage

class Tk:
    """
    The toplevel window class

    """
    def __init__(self, _master=None, group=None):
        self.setAllwaysOnTop = self.setTopmost
        self.quit = self.quitMainLoop
        self.withdraw = self.hide
        if _master is None:
            self._data = {"master": _tk.Tk(), "registry":_EventRegistry(self), "placeRelData":{"handler":None}, "destroyed":False, "hasMenu":False, "childWidgets":{},"oldWinSize":(-1, -1), "set_size":(),  "privateOldWinSize":(-1, -1), "id":"".join([str(_randint(0,9)) for _ in range(15)]), "dynamicWidgets":{}, "closeRunnable":None, "title":"", "last_size_conf_time":None}
            #configure internal onCloseEvent
            self["master"].protocol("WM_DELETE_WINDOW", self._internalOnClose)
        elif isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, Tk):
            self._data = _master._data
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + " instance not: " + str(_master.__class__.__name__))
        if group is not None: group.add(self)
    def __str__(self):
        return str(self.__class__.__name__)+"("+str(self._data)+")"
    def __getitem__(self, item):
        try:return self._data[item]
        except KeyError as e: raise KeyError("Item '"+str(item)+"' is not in dict of class '"+self["master"].__class__.__name__+"'")
    def __setitem__(self, key, value):
        self._data[key] = value
    # Task Scheduler
    def runTask(self, func)->_TaskScheduler:
        task = _TaskScheduler(self, 0, func)
        return task
    def runTaskAfter(self, func, time)->_TaskScheduler:
        task = _TaskScheduler(self, time, func)
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
        def after(e, out):
            if not e["setCanceled"]:
                self.destroy()
        self["closeRunnable"] = _EventHandler._getNewEventRunnable(self, func, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs)
        return self["closeRunnable"]
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
        if hasattr(event, "value"):
            event = event.value
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
        # self["registry"].unregisterType(event)
        raise NotImplemented()
    def unbindAllEvents(self):
        """
        Unbind all Events.

        @return:
        """
        # self["registry"].unregisterAll()
        raise NotImplemented()
    # Cursor
    def setCursor(self, c:Union[Cursor, str]):
        """
        Set cursor image from Cursor _Enum or default tkinter string.

        @note only predefined cursors are implented yet
        @param c:
        @return:
        """
        self["master"]["cursor"] = c.value if hasattr(c, "value") else c
        return self
    def hideCursor(self):
        """
        Hides the current Cursor within the Window.
        Use 'setCursor' to show the Cursor

        @return:
        """
        self["master"]["cursor"] = "none"
        return
    # Quit & Close
    def closeViaESC(self):
        """
        Destroys the window via pressing ESC-key.
        Only if the setCanceled in the 'onCloseEvent' is False!
        @return:
        """
        assert self["closeRunnable"] is not None, "Bind 'onCloseEvent' Event first!"
        self.bind(self["closeRunnable"], EventType.ESC)
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
        if self["closeRunnable"] is None:
            self.destroy()
        else:
            self["closeRunnable"]()
    def quitMainLoop(self):
        """
        Quit the Window. BUT the Window mainloop is still running.

        @return:
        """
        self["master"].quit()
    # Appearance
    def forceFocus(self):
        """
        Forces the focus to this WIndow.
        @return:
        """
        self["master"].focus_force()
        return self
    def hide(self):
        """
        Minimizees the Window.
        @return:
        """
        self["master"].withdraw()
    def show(self):
        """
        Maximizes the Window.
        @return:
        """
        self["master"].deiconify()
    def lift(self):
        """
        Lifts the Window on top of all other Windows.
        @return:
        """
        self["master"].lift()
        return self
    def destroy(self):
        """
        Destroys the Tkinter Window. Ignores the 'onCloseEvent'.

        @return:
        """
        try:
            self["destroyed"] = True
            WidgetGroup.removeFromAll(self)
            widgets = self["childWidgets"].copy().values()
            for w in widgets:
                w.destroy()
            self["master"].destroy()
            self._data.clear()
            return True

        except Exception as e:
            if WIDGET_DELETE_DEBUG or True:
                print("FAIL!", e)
                print(format_exc())
            return False
    def disable(self, b=True):
        self["master"].wm_attributes("-disabled", b)
    def overrideredirect(self, b=True):
        self["master"].overrideredirect(b)
    def centerWindowOnScreen(self, forceSetSize=False):
        """
        Centers the Window on screen

        @param forceSetSize: get the Parameters from 'setWindowSize' function and not from tkinter
        @return:
        """
        width, height = self.getWindowSize()
        if width == 1 or forceSetSize:
            if len(self["set_size"]) == 2:
                width, height = self["set_size"]
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
        self["master"].update()
    def updateIdleTasks(self):
        """
        Updates the IDLE-Tasks.

        @return:
        """
        self["master"].update_idletasks()
    # Setter
    def setFocus(self):
        """
        Sets the focus to this Window.

        @return:
        """
        self["master"].focus_set()
        return self
    def setIcon(self, icon:Union[TkImage, PILImage]):
        """
        Sets the icon in the top left corner from the Window.

        @param icon:
        @return:
        """
        self["master"].iconphoto(True, icon._get())
        return self
    def setBg(self, col:Union[Color, str]):
        """
        Set the Background Color of the Window.

        @param col: Use Color _Enum, tkinter string or hex-code.
        @return:
        """
        self["master"]["bg"] = col.value if hasattr(col, "value") else col
        return self
    def setTopmost(self, b=True):
        """
        Sets the "Always on top" attribute.

        @param b:
        @return:
        """
        self["master"].wm_attributes("-topmost", b)
    def setResizeable(self, b:bool):
        """
        Defines if the Window can be resized.

        @param b:
        @return:
        """
        self["master"].resizable(b, b)
        return self
    def setFullscreen(self, b:bool=True):
        """
        Sets the Window in Fullscreen mode.

        @param b:
        @return:
        """
        self["master"].wm_attributes("-fullscreen", b)
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
        self["master"].geometry(str(x) + str(y))
    def setCloseable(self, b:bool):
        """
        If b is True -> Window cannot be closed
        If b is False -> Window can normally close

        @param b:
        @return:
        """
        self["master"].protocol("WM_DELETE_WINDOW", b)
    def setTitle(self, title):
        """
        Sets the Window title.

        @param title:
        @return:
        """
        self["title"] = title
        self["master"].title(title)
        return self
    def setTransparent(self, color:Union[Color, str]):
        """
        Defines given color as Transparent.

        @param color:
        @return:
        """
        color = color.value if hasattr(color, "value") else color
        self["master"].wm_attributes("-transparentcolor", color)
        return self
    def setWindowSize(self, x:int, y:int, minsize=False):
        """
        Set the Windowsize. Can also set the 'minsize'.

        @param x:
        @param y:
        @param minsize:
        @return:
        """
        self["set_size"] = (x, y)
        if minsize: self.setMinSize(x, y)
        self["master"].geometry(str(x) + "x" + str(y))
    def setMaxSize(self, x, y):
        """
        Set the maximal Windowsize.

        @param x:
        @param y:
        @return:
        """
        self["master"].maxsize(x, y)
    def setMinSize(self, x, y):
        """
        Set the minimum Windowsize.

        @param x:
        @param y:
        @return:
        """
        self["master"].minsize(x, y)
    # Getter
    def getPositionOnScreen(self)->Location2D:
        return Location2D(
            self["master"].winfo_rootx(),
            self["master"].winfo_rooty()
        )
    def getMousePositionRelativeToScreen(self)->Location2D:
        """
        Returns the current mouse position relative to Screen.
        @return:
        """
        return Location2D(
            self["master"].winfo_pointerx(),
            self["master"].winfo_pointery()
        )
    def getMousePosition(self)->Location2D:
        """
        Returns the current mouse position on the TK window.
        @return:
        """
        return Location2D(self["master"].winfo_pointerx() - self["master"].winfo_rootx(), self["master"].winfo_pointery() - self["master"].winfo_rooty())
    def getWidgetFromTk(self, w):
        for widg in self._getAllChildWidgets(self):
            pass
        raise NotImplemented()
    def getWidgetFromLocation(self, loc:Location2D):
        #for widget in self._getAllChildWidgets(self):
        #    if widget._get()
        #print(*loc.get())
        #widget = self["master"].winfo_containing(*loc.get())
        #return widget
        raise NotImplemented()
    def getHeight(self):
        """
        Returns the Window height.

        @return:
        """
        return self["master"].winfo_height()
    def getWidth(self):
        """
        Returns the Window width.

        @return:
        """
        return self["master"].winfo_width()
    def getScreenSize(self):
        """
        Returns the Screen width and height as tuple.

        @return:
        """
        return self["master"].winfo_screenwidth(), self["master"].winfo_screenheight()
    def getWindowSize(self):
        """
        Returns the Window width and height as tuple.

        @return:
        """
        return self["master"].winfo_width(), self["master"].winfo_height()
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
        #for i in self["master"].winfo_children():
        #    i.destroy()
        raise NotImplemented()
    def activeWidgets(self): #@TODO: FIX!
        #for i in self["master"].winfo_children():
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
        self["master"].bell()
        return self
    def copyToClip(self, s):
        self["master"].clipboard_append(str(s))
        return self
    def clearClip(self):
        self["master"].clipboard_clear()
        return self
    def getClip(self):
        return self["master"].clipboard_get()
    def sleep(self, s):
        """
        Sleeps s seconds and updates the window in Background.
        @param s:
        @return:
        """
        temp = time()
        while True:
            if not self["destroyed"]: self.update()
            if time()-temp >= s:
                break
        return self
    # Private Implementations
    def _mainloop(self):
        """
        Private Implementations of 'mainloop' call.
        @return:
        """
        if self["destroyed"]: return
        self._finishLastTasks()
        self["master"].mainloop()
        self["destroyed"] = True
    def _updateDynamicSize(self, widget):
        """
        Private implementation of the 'updateDynamicWidgets'.
        @param widget:
        @return:
        """
        if not widget["destroyed"] and "xOffset" in widget["placeRelData"]:# and widget["id"] in list(self["dynamicWidgets"].keys()):
            #widget._get().place_forget()
            #self._get().update_idletasks()
            _data = widget["placeRelData"]
            x = _map(_data["xOffset"] + _data["xOffsetLeft"], 0, 100, 0, widget["master"].getWidth()) if _data["fixX"] is None else _data["fixX"]
            y = _map(_data["yOffset"] + _data["yOffsetUp"], 0, 100, 0, widget["master"].getHeight()) if _data["fixY"] is None else _data["fixY"]

            width = ((widget["master"].getWidth() - _map(_data["xOffset"] + _data["xOffsetRight"], 0, 100, 0, widget["master"].getWidth()) - x) - (widget._data["yScrollbar"]["thickness"] if "yScrollbar" in list(widget._data.keys()) and widget._data["yScrollbar"]["autoPlace"] else 0) if _data["fixWidth"] is None else _data["fixWidth"])
            height = ((widget["master"].getHeight() - _map(_data["yOffset"] + _data["yOffsetDown"], 0, 100, 0, widget["master"].getHeight()) - y) - (widget._data["xScrollbar"]["thickness"] if "xScrollbar" in list(widget._data.keys()) and widget._data["xScrollbar"]["autoPlace"] else 0) if _data["fixHeight"] is None else _data["fixHeight"])
            if _data["stickRight"]:
                x = widget["master"].getWidth()-width
            if _data["stickDown"]:
                y = widget["master"].getHeight()-height
            if _data["centerX"]:
                x = int(round(widget["master"].getWidth()/2 - width/2, 0))
            if _data["centerY"]:
                y = int(round(widget["master"].getHeight()/2 - height/2, 0))

            width += _data["changeWidth"]
            height += _data["changeHeight"]

            x += _data["changeX"]
            y += _data["changeY"]

            widget["widget"].place(x=x,
                                 y=y,
                                 width=width,
                                 height=height,
                                 anchor=Anchor.UP_LEFT.value)

            if _data["handler"] is not None:
                handler = _data["handler"]
                for event in widget["registry"].getCallables("[relative_update]"):
                    event["value"] = [x, y, width, height]
                handler()

            if "xScrollbar" in list(widget._data.keys()) and widget._data["xScrollbar"]["autoPlace"]:
                widget._data["xScrollbar"].place(x, y + height, width=width)

            if "yScrollbar" in list(widget._data.keys()) and widget._data["yScrollbar"]["autoPlace"]:
                widget._data["yScrollbar"].place(x + width, y, height=height)

            if _data["handler"] is not None:
                handler = _data["handler"]
                for event in widget["registry"].getCallables("[relative_update_after]"):
                    event["value"] = [x, y, width, height]
                handler()
            #widget._get().update_idletasks()
            widget["placed"] = True
    def updateDynamicWidgets(self):
        """
        Call this method to update all relative placed Widgets
        which are placed with 'placeRelative' manager.

        @return:
        """
        # OLD implementation
        #for widget in list(self["dynamicWidgets"].values())[::-1]: # place frames first
        #    if not widget["destroyed"]: self._updateDynamicSize(widget)
        #D = {}
        #print("######### WIDGETS TO PLACE REL ############")
        relevantIDs = list(self["dynamicWidgets"].keys())
        for widget in _getAllChildWidgets(self):
            if widget._getID() in relevantIDs:
                #if _isinstance(widget, "_ToolTip"): continue
                if widget.__class__.__name__ == "_ToolTip": continue

                #key = widget.__class__.__name__
                #if key in D.keys(): D[key] += 1
                #else: D[key] = 1

                if not widget["destroyed"]: self._updateDynamicSize(widget)
        #for k in D.keys(): print(f"{k}: {D[k]}")
        #print("############################################")
        return self
    def _internalOnClose(self):
        """
        internal onClose Event.
        @return:
        """
        #print("Internal Close")
        if self["closeRunnable"] is None:
            self.destroy()
        else:
            runnable = self["closeRunnable"]
            runnable()
            if not runnable.event["setCanceled"]:
                self.destroy()
    def _registerOnResize(self, widget):
        """
        Register Widgets to Auto resize.
        """
        self["dynamicWidgets"][widget["id"]] = widget
    def _unregisterOnResize(self, widget):
        if list(self["dynamicWidgets"].keys()).__contains__(widget["id"]):
            del self["dynamicWidgets"][widget["id"]]
    def _decryptWindowResize(self, args, event):
        _size = self.getWindowSize()
        if self["oldWinSize"] == _size:
            return "CANCEL"
        else:
            self["oldWinSize"] = _size
            return _size
    def _decryptNonFilteredWindowResize(self, args, event):
        return self.getWindowSize()
    def _privateDecryptWindowResize(self, args, event):
        _size = self.getWindowSize()
        if self["privateOldWinSize"] == _size:
            return "CANCEL"
        else:
            self["privateOldWinSize"] = _size
            return _size
    def _finishLastTasks(self):
        _EventHandler._registerNewEvent(self, self._customUpdateDynamicWidgetsHandler, EventType.SIZE_CONFIUGURE, args=[], priority=1, decryptValueFunc=self._privateDecryptWindowResize)
        self.updateDynamicWidgets()
    @runWatcherDec
    def _customUpdateDynamicWidgetsHandler(self, e):
        if not len(self._data): return #destroyed
        self.updateDynamicWidgets()
    def clearChildWidgets(self):
        """
        Clears the child-widgets.

        @return:
        """
        self._data["childWidgets"].clear()
    def addChildWidgets(self, *args):
        """
        Adds/Overwrites all Child widgets from this widget with new ones.

        @param args:
        @return:
        """
        for w in args:
            self._data["childWidgets"][w["id"]] = w
    def unregisterChildWidget(self, w):
        """
        Unregisters specific Child widget from this Master.

        @param w:
        @return:
        """
        del self["childWidgets"][w["id"]]
    def getID(self)->str:
        return self["id"]
    def _getTkMaster(self):
        """
        Returns the highest master (Tk/Toplevel) of this widget.

        @return:
        """
        return self
    def _get(self):
        return self["master"]
class Toplevel(Tk):
    """
    Toplevel window.
    Pass 'Tk' for _master to Use 'Toplevel' as 'Tk-class'.
    This allows to use Toplevel as standalone and as Toplevel window above another application.
    """
    def __init__(self, _master, group=None, topMost=True):
        if isinstance(_master, Tk):
            self._data = {"master": _tk.Toplevel(), "tkMaster":_master, "registry":_EventRegistry(self), "set_size":(), "destroyed":False, "hasMenu":False, "childWidgets":{},"oldWinSize":(-1, -1), "privateOldWinSize":(-1, -1), "id":"".join([str(_randint(0,9)) for _ in range(15)]), "dynamicWidgets":{}, "title":"", "closeRunnable":None}
            _EventHandler._registerNewEvent(self, self.updateDynamicWidgets, EventType.key("<Configure>"), args=[], priority=1, decryptValueFunc=self._privateDecryptWindowResize, disableArgs=True)
            # configure internal onCloseEvent
            self["master"].protocol("WM_DELETE_WINDOW", self._internalOnClose)
        elif isinstance(_master, str) and _master == "Tk":
            self._data = {"master":_tk.Tk(), "tkMaster":_master, "placeRelData":{"handler":None}, "registry":_EventRegistry(self), "set_size":(), "destroyed":False, "hasMenu":False, "childWidgets":{},"oldWinSize":(-1, -1), "privateOldWinSize":(-1, -1),"id":"".join([str(_randint(0, 9)) for _ in range(15)]), "dynamicWidgets":{}, "title":"", "closeRunnable":None}
            _EventHandler._registerNewEvent(self, self.updateDynamicWidgets, EventType.key("<Configure>"), args=[], priority=1, decryptValueFunc=self._privateDecryptWindowResize, disableArgs=True)
            # configure internal onCloseEvent
            self["master"].protocol("WM_DELETE_WINDOW", self._internalOnClose)
        elif isinstance(_master, Toplevel):
            self._data = _master._data
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + " or Tk instance not: " + str(_master.__class__.__name__))
        super().__init__(self._data, group)
        if topMost: self.setAllwaysOnTop()
    def mainloop(self):
        """
        Mainloop in Toplevel is only used when Toplevel is configured as Tk.

        @return:
        """
        if isinstance(self["master"], _tk.Tk):
            self["master"].mainloop()
class Dialog(Toplevel):
    """
    Similar to Toplevel.
    Master of this dialog is disabled until dialog is closed.
    Dialog is topmost on default.
    """
    def __init__(self, _master, group=None, topMost=True):
        super().__init__(_master, group, topMost)
        self.hide()
        self._get().transient()
    def show(self):
        """
        Shows the dialog.

        @return:
        """
        self["master"].deiconify()
        self._get().wait_visibility()
        self._get().grab_set()
    def hide(self):
        """
        Hides the dialog.

        @return:
        """
        self._get().grab_release()
        self["master"].withdraw()
