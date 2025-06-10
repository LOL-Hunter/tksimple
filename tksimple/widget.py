from random import randint as _randint, choice as _choice
from typing import Union, Callable, Tuple, List
import tkinter as _tk
import tkinter.ttk as _ttk
from tkinter.font import Font as _tk_Font
from time import strftime
from string import ascii_lowercase
from traceback import format_exc

from .util import _lockable, Font, _isinstance, WidgetGroup, _TaskScheduler, _IntVar, _getAllChildWidgets
from .event import _EventHandler, _EventRegistry, Event
from .const import *
from .tkmath import Location2D, Rect
from .image import PILImage, TkImage
from .window import Toplevel, Tk

class Widget:
    """
    Baseclass for all Widgets.
    """
    def __init__(self, ins, _data, group):
        self._ins = self if ins is None else ins
        self.disable = self.setDisabled
        self.enable = self.setEnabled
        self.setBackgroundColor = self.setBg
        self.setForegroundColor = self.setFg
        _data["tkMaster"] = _data["master"] if _isinstance(_data["master"], "Tk") else _data["master"]["tkMaster"]
        id = "".join([str(_randint(0,9)) for _ in range(15)])
        self._data = {**_data, **{"widgetProperties":{},"childWidgets":{}, "id":id, "placed":True, "destroyed":False, "placeRelData":{"handler":None}, "registry":_EventRegistry(self), "group":group}}
        self._data["master"]["childWidgets"][self["id"]] = self._ins
        if "init" in _data.keys():
            for key, value in zip(_data["init"].keys(), _data["init"].values()):
                if key == "func": value()
                else: self._setAttribute(name=key, value=value)
            del _data["init"]
        if group is not None:
            group.add(self._ins)
    def __getitem__(self, item):
        if not len(self._data): return
        try:return self._data[item]
        except KeyError as e: raise KeyError("Item '"+str(item)+"' is not in dict of class '"+self["widget"].__class__.__name__+"'")
    def __setitem__(self, key, value):
        self._data[key] = value
    def __str__(self):
        return str(self.__class__.__name__)+"("+str(self._data)+")"
    def __eq__(self, other):
        if not hasattr(other, "_data"): return False
        return self._data == other._data
    def __del__(self):
        #print("__DELETE__", type(self))
        if not len(self._data): return
        if self["group"] is not None:
            self["group"].remove(self._ins)
        self._data.clear()
    # Attribute Setter Methods
    @_lockable
    def setBg(self, col:Union[Color, str]):
        """
        Set the background color of this widget.

        @param col: Use Color _Enum, tkinter string or hex-code.
        @return:
        """
        self._setAttribute("bg", col.value if hasattr(col, "value") else col)
        return self
    def setFg(self, col:Union[Color, str]):
        """
        Set the text color of this widget.

        @param col: Use Color _Enum, tkinter string or hex-code.
        @return:
        """
        self._setAttribute("fg", col.value if hasattr(col, "value") else col)
        return self
    def setText(self, text):
        """
        Set the text of this widget.

        @param text:
        @return:
        """
        self._setAttribute("text", str(text))
        return self
    def setFont(self, size:Union[int, Font]=10, art=FontType.ARIAL, underline=False, bold=False, italic=False, overstrike=False):
        """
        Use this method to configure the Font.

        @param size: text size or Font-instance
        @param art: font type
        @param underline: text is underlined
        @param bold: text is bold
        @param slant: text is slant
        @param overstrike: text is overstrike
        @return:
        """
        if not isinstance(size, Font):
            _data = {'family': art.value if hasattr(art, "value") else art,
                    'size': size,                            # size
                    'weight': 'bold' if bold else 'normal',   #fett
                    'slant': 'italic' if italic else'roman',   # kusiv
                    'underline': bool(underline),            # unterstrichen
                    'overstrike': bool(overstrike)}          # durchgestrichen

            self._setAttribute("font", _tk_Font(**_data))
        else:
            self._setAttribute("font", size._get())
        return self
    def setTextOrientation(self, ori:Anchor=Anchor.LEFT):
        """
        Set the Text align.
        Default is 'Anchor.CENTER'

        @param ori:
        @return:
        """
        self._setAttribute("anchor", ori.value if hasattr(ori, "value") else ori)
        return self
    def setOrientation(self, ori:Orient):
        """
        Set the Orientation via Orient _Enum.
        Used for process bars, Scales etc.
        Possible orientations:
            'Orient.HORIZONTAL'
            'Orient.VERTICAL'

        @param ori:
        @return:
        """
        self._setAttribute("orient", ori.value if hasattr(ori, "value") else ori)
        return self
    def setStyle(self, style:Style):
        """
        Set widget style.
        Use Style _Enum to choose between styles.

        @param style:
        @return:
        """
        self._setAttribute("relief", style.value if hasattr(style, "value") else style)
        return self
    def setBorderWidth(self, bd:int):
        """
        Some Widgets can change their border size.

        @param bd:
        @return:
        """
        self._setAttribute("bd", bd)
        return self
    def setCompound(self, dir_:Direction):
        """
        Select the Compound of an image behind a text.

        example:
            'Direction.Center' -> centers an image behind a text.

        @param dir_:
        @return:
        """
        dir_ = dir_.value if hasattr(dir_, "value") else dir_
        self._setAttribute("compound", dir_)
        return self
    def setCursor(self, c:Cursor):
        """
        Set cursor image from Cursor _Enum or default tkinter string.
        This only applies while hovering over this widget.

        @note only predefined cursors are implemented yet
        @param c:
        @return:
        """
        self["widget"]["cursor"] = c.value if hasattr(c, "value") else c
        return self
    def setDisabled(self):
        """
        Disables this widget.

        @return:
        """
        self._setAttribute("state", _tk.DISABLED)
        return self
    def setEnabled(self):
        """
        Enables this widget.

        @return:
        """
        self._setAttribute("state", _tk.NORMAL)
        return self
    # Attribute Getter Methods
    def getText(self):
        """
        Returns the set text.

        @return:
        """
        return self["widget"]["text"]
    def getHeight(self):
        """
        Returns the Widget Height.
        May be only possible after using any place manager.

        @return:
        """
        self.updateIdleTasks()
        return self["widget"].winfo_height()
    def getWidth(self):
        """
        Returns the Widget Width.
        May be only possible after using any place manager.

        @return:
        """
        self.updateIdleTasks()
        return self["widget"].winfo_width()
    def getPositionRelativeToScreen(self)->Location2D:
        """
        Returns the location of this widget relative to the screen.
        """
        return Location2D(
            self["widget"].winfo_rootx(),
            self["widget"].winfo_rooty()
        )
    def setFocus(self):
        """
        Sets the focus to this Window.

        @return:
        """
        self["widget"].focus_set()
        return self
    def getPosition(self)->Location2D:
        """
        Returns the widget position.
        May be only possible after using any place manager.

        @return:
        """
        return Location2D(self["widget"].winfo_x(), self["widget"].winfo_y())
    def getPositionToMaster(self)->Location2D:
        """
        Returns the widget position relative to master window.
        May be only possible after using any place manager.

        @return:
        """
        return Location2D(self["widget"].winfo_vrootx(), self["widget"].winfo_vrooty())
    def getParentWindow(self):
        """
        Returns Parent Master instance. Tk, Toplevel or Dialog.
        """
        return self._getTkMaster()
    # Misc Methods
    def isFocus(self):
        """
        Returns a boolean if this widget is currently no focus.

        @return:
        """
        return self["widget"].focus_get() == self._get()
    def attachToolTip(self, text:str, atext:str="", group=None, waitBeforeShow=.5):
        """
        Attaches a tooltip that opens on hover over this Widget longer than 'waitBeforeShow' seconds.


        @param text: Text that will be shown in ToolTip
        @param atext: AdditionalText will be shown when shift key is pressed.
        @param group: Optional WidgetGroup instance for preset font, color etc.
        @param waitBeforeShow: Time the user have to hover over this widget to show the TooTip
        @return: ToolTip instance for further configuration
        """
        return _ToolTip(self, atext != "", waitBeforeShow=waitBeforeShow, group=group).setText(text).setAdditionalText(atext)
    def canTakeFocusByTab(self, b:bool=False):
        """
        Set if this widget can take focus by pressing tab.
        Default: True

        @param b:
        @return:
        """
        self._setAttribute("takefocus", int(b))
        return self
    # Update Methods
    def update(self):
        """
        Calls the tkinter update of this widget.

        Processes all pending Events.
        Redaws this widget.
        ...

        @return:
        """
        self["widget"].update()
        return self
    def updateIdleTasks(self):
        """
        Updates only the tkinter idle tasks.

        @return:
        """
        self["widget"].update_idletasks()
        return self
    def updateRelativePlace(self):
        """
        Updates the relative place of this widget.
        Only updates if the widget ist placed relative.

        @return:
        """
        self["tkMaster"]._updateDynamicSize(self)
        return self
    # Event Management Methods
    def bind(self, func:Callable, event:Union[EventType, Key, Mouse, str], args:list=None, priority:int=0, defaultArgs=False, disableArgs=False):
        """
        Binds a specific event to the Widget. Runs given function on trigger.

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
            _EventHandler._registerNewEvent(self._ins, func, event, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs)
        return self
    def unbind(self, event:Union[EventType, Key, Mouse]):
        """
        Unbinds all Events from given EventType.

        @param event:
        @return:
        """
        #self["registry"].unregisterType(event)
        raise NotImplemented()
    def generateEvent(self, event:Union[EventType, Key, Mouse, str]):
        """
        Triggers given event on this widget.

        @note Custom Events are not implemented yet!

        @param event:
        @return:
        """
        event = event.value if hasattr(event, "value") else event
        if event.startswith("["):
            raise NotImplemented("Trigger custom Events is not implemented yet!")
        self["widget"].event_generate(event)
    # Place Manager Methods
    def grid(self, row=0, column=0):
        """
        Default tkinter grid-manager.

        @param row:
        @param column:
        @return:
        """
        assert not self["destroyed"], "The widget has been destroyed and can no longer be placed."
        self["widget"].grid(row=row, column=column)
        return self
    def placeRelative(self, fixX:int=None, fixY:int=None, fixWidth:int=None, fixHeight:int=None, xOffset=0, yOffset=0, xOffsetLeft=0, xOffsetRight=0, yOffsetUp=0, yOffsetDown=0, stickRight=False, stickDown=False, centerY=False, centerX=False, changeX=0, changeY=0, changeWidth=0, changeHeight=0, nextTo=None, updateOnResize=True):
        """
        Scales this widgetsize relative to the Window-Size.
        This scaling happens on resize of the window.

        Can be overwritten!

        Offset:
            Offset means to configure the size of the widget percentage to the master size.
            xOffsetLeft=50 means that the widget has 50% of the master-width and is right oriented.

        @param fixX: Defines x coordinate as fixed. This is no longer autoconfigured.
        @param fixY: Defines y coordinate as fixed. This is no longer autoconfigured.
        @param fixWidth: Defines width coordinate as fixed. This is no longer autoconfigured.
        @param fixHeight: Defines height coordinate as fixed. This is no longer autoconfigured.
        @param xOffset: offset x both sides
        @param yOffset: offset y both sides
        @param xOffsetLeft: offset x left
        @param xOffsetRight: offset x right
        @param yOffsetUp: offset y up
        @param yOffsetDown: offset y down
        @param stickRight: Sets the fixpoint to the right side.
        @param stickDown: Sets the bottom to the right side.
        @param centerY: Centers the widget on Y-Axis.
        @param centerX: Centers the widget on X-Axis.
        @param changeX: Changes x coordinate after all calculations are done.
        @param changeY: Changes y coodinate after all calculations are done.
        @param changeWidth: Changes width coodinate after all calculations are done.
        @param changeHeight: Changes height coodinate after all calculations are done.
        @param nextTo: NOT IMPLEMENTED YET
        @param updateOnResize: True -> registers to update on resize (Default) | False -> update once
        @return:
        """
        assert 100 >= xOffset + xOffsetLeft >= 0 and 100 >= xOffset + xOffsetRight >= 0, "xOffset must be a int Value between 0 and 100!"
        assert 100 >= yOffset + yOffsetUp >= 0 and 100 >= yOffset + yOffsetDown >= 0, "yOffset must be a int Value between 0 and 100!"
        self._data["placeRelData"] = {"handler": self["placeRelData"]["handler"],
                                      "xOffset": xOffset,
                                      "xOffsetLeft": xOffsetLeft,
                                      "xOffsetRight": xOffsetRight,
                                      "yOffset": yOffset,
                                      "yOffsetUp": yOffsetUp,
                                      "yOffsetDown": yOffsetDown,
                                      "fixX": fixX,
                                      "fixY": fixY,
                                      "fixWidth": fixWidth,
                                      "fixHeight": fixHeight,
                                      "stickRight": stickRight,
                                      "stickDown": stickDown,
                                      "centerX": centerX,
                                      "centerY": centerY,
                                      "nextTo": nextTo,
                                      "changeX": changeX,
                                      "changeY": changeY,
                                      "changeWidth": changeWidth,
                                      "changeHeight": changeHeight}
        self["tkMaster"]._updateDynamicSize(self)
        if updateOnResize:
            self["tkMaster"]._registerOnResize(self)
        return self
    def place(self, x=None, y=None, width=None, height=None, anchor:Anchor=Anchor.UP_LEFT):
        """
        Place the widget with fix coords and width and height.
        width and height can be left out and be handled by tkinter to set is automatically.

        Can be overwritten!

        @param x: X-Coordinate relative to the anchor.
        @param y: Y-Coordinate relative to the anchor.
        @param width: width of the widget.
        @param height: height of the widget.
        @param anchor: Set the fixpoint. Default: Upper left corner.
        @return:
        """
        assert not self["destroyed"], "The widget has been destroyed and can no longer be placed."
        if x is None: x = 0
        if y is None: y = 0
        if hasattr(anchor, "value"):
            anchor = anchor.value
        if isinstance(x, Location2D):
            x, y = x.get()
        if isinstance(x, Rect):
            height = x.getHeight()
            width = x.getWidth()
            x, y = x.getLoc1().get()
        x = int(round(x, 0))
        y = int(round(y, 0))
        #self._get().place_forget()
        self["widget"].place(x=x, y=y, width=width, height=height, anchor=anchor)
        self["placed"] = True
        return self
    def placeForget(self):
        """
        Removes this widget from its master.
        Can be placed again after.

        @return:
        """
        try:
            self["widget"].place_forget()
            self["placed"] = False
        except Exception as e:
            print(format_exc())
        self["tkMaster"]._unregisterOnResize(self)
    def destroy(self):
        """
        Destroys this widget.
        The Widget instance cannot be used after destroying it!

        Can be overwritten!
        @return:
        """
        assert not self["destroyed"], f"Widget {type(self)} {self._getID()} is already destroyed!"
        self["registry"].unregisterAll()
        self["tkMaster"]._unregisterOnResize(self)
        if WIDGET_DELETE_DEBUG: print(type(self["master"]), "->", type(self))
        del self["master"]["childWidgets"][self["id"]]  # unregister as child widget from master

        WidgetGroup.removeFromAll(self)
        if not isinstance(self, _ToolTip):  # -> Ignore Widget is None
            if not self["destroyed"]: self["widget"].destroy()
        self["destroyed"] = True
        self["placed"] = False
        for w in self["childWidgets"].copy().values():
            self["tkMaster"]._unregisterOnResize(w)
            w.destroy()
        self._data.clear()
        return self
    def lift(self, widg=None):
        """
        Lifts this widget in front of all other or in front of given Widget.

        @param widg:
        @return:
        """
        if widg is not None:
            self["widget"].lift(widg._get())
        else:
            self["widget"].lift()
    # Intern Methods
    def _applyTkOption(self, **kwargs):
        """
        Apply one or more tkinter attribues to this widget.

        Instead of:
            widget["text"] = "This is a text!"
        Use:
            widget.applyTkOption(text="This is a text!", ...)

        @param kwargs:
        @return:
        """
        for k, v in zip(kwargs.keys(), kwargs.values()):
            self._setAttribute(k, v)
        return self
    def _getTkMaster(self):
        """
        Returns the highest master (Tk/Toplevel) of this widget.

        @return:
        """
        return self["tkMaster"]
    def _clearChildWidgets(self):
        """
        Clears the child-widgets.

        @return:
        """
        self._data["childWidgets"].clear()
    def _addChildWidgets(self, *args):
        """
        Adds/Overwrites all Child widgets from this widget with new ones.

        @param args:
        @return:
        """
        for w in args:
            self._data["childWidgets"][w["id"]] = w
    def _unregisterChildWidget(self, w):
        """
        Unregisters specific Child widget from this Master.

        @param w:
        @return:
        """
        del self["childWidgets"][w["id"]]
    def _setId(self, id_:str): #@TODO: why? maby error with event??
        self["id"] = str(id_)
    def _addData(self, _data:dict):
        self._data = {**self._data, **_data}
    def _getID(self)->str:
        """
        Returns this widget id.

        @return:
        """
        return self["id"]
    def _decryptEvent(self, args, event):
        pass
    def _setAttribute(self, name, value):
        if self._data["tkMaster"]["destroyed"]: return
        self["widgetProperties"][name] = value
        try:
            self["widget"][name] = value
        except Exception as e:
            value = repr(value)
            valType = type(value)
            value = value[0:50]+"..." if len(str(value)) > 50 else value
            raise AttributeError("Could not set Attribute of Widget "+str(type(self._ins))+"!\n\tKEY: '"+str(name)+"'\n\tVALUE["+str(valType)+"]: '"+str(value)+"'\n"+str(self._ins)+" \n\tTKError: "+str(e))
    def _getAllChildWidgets(self):
        return list(self["childWidgets"].values())
    def _get(self):
        return self["widget"]
class _LockableWidget(Widget):
    """
    Private implementation of tkinter's [state="disabled"].
    """
    def __init__(self, ins, _data, group):
        self._isDisabled = False
        if not hasattr(self, "_isReadOnly"):
            self._isReadOnly = False
        self._lockVal = 0
        super().__init__(ins, _data, group)

        # setReadOnly
        if self._isReadOnly:
            self.setDisabled()
            return
        self.setEnabled()
    def _setReadOnly(self, b:bool):
        self._isReadOnly = b
    def _unlock(self):
        self._lockVal += 1
        if self._lockVal > 1: return
        # enter UnLocking
        if not self._isDisabled: return
        super().setEnabled()
    def _lock(self):
        self._lockVal -= 1
        if self._lockVal != 0: return
        # leave Unlocking
        if self._isReadOnly or self._isDisabled:
            super().setDisabled()
    def setEnabled(self):
        if not self._isDisabled: return
        super().setEnabled()
        self._isDisabled = False
    def setDisabled(self):
        if self._isDisabled: return
        super().setDisabled()
        self._isDisabled = True

class _ToolTip(Widget):
    """
    Create a tooltip for a given widget.
    It shows up on hover over widget.
    """
    def __init__(self, _master, pressShiftForMoreInfo=False, waitBeforeShow=.5, group=None):
        if _isinstance(_master, "Tk") or isinstance(_master, Widget):
            self._data = {"master": _master,
                         "disableTip":False,
                         "widget":None,
                         "init": {},
                         "text":"",
                         "atext":"",
                         "wait":waitBeforeShow,
                         "wrapLength":180,
                         "task":None,
                         "tip":None,
                         "group":group,
                         "tipLabel":None}
            self["master"].bind(self._enter, "<Enter>")
            self["master"].bind(self._leave, "<Leave>")
            self["master"].bind(self._leave, "<ButtonPress>")
            if pressShiftForMoreInfo: self["master"]["tkMaster"].bind(self._more, "<KeyRelease-Shift_L>", args=["release"])
            if pressShiftForMoreInfo: self["master"]["tkMaster"].bind(self._more, "<KeyPress-Shift_L>", args=["press"])
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + ", Frame or Tk instance not: " + str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def setDisabled(self):
        self["disableTip"] = True
    def setEnabled(self):
        self["disableTip"] = False
    def setText(self, text):
        self["text"] = text
        return self
    def setAdditionalText(self, text):
        self["atext"] = text
        return self
    def _more(self, e):
        mode = e.getArgs(0)
        if self["tip"]:
            text = self["text"] if mode == "release" else self["atext"]
            self["tipLabel"].destroy()
            self["tipLabel"] = Label(self["tip"])._applyTkOption(text=text, justify='left', background="#ffffff", relief='solid', borderwidth=1, wraplength=self["wrapLength"])
            self["tipLabel"]._get().pack(ipadx=1)
    def _enter(self, e):
        self._schedule()
    def _leave(self, e):
        self._unschedule()
        self._hidetip()
    def _schedule(self):
        self._unschedule()
        self["task"] = _TaskScheduler(self["master"], self["wait"], self._show).start()
    def _unschedule(self):
        task = self["task"]
        self["task"] = None
        if task: task.cancel()
    def _show(self):
        if self["disableTip"]:
            return
        mx, my = (self["master"]._getTkMaster()._get().winfo_pointerx(), self["master"]._getTkMaster()._get().winfo_pointery())
        self._hidetip()
        self["tip"] = Toplevel(self["master"]["tkMaster"], group=self["group"])
        self["tip"].overrideredirect()
        self["tip"].setPositionOnScreen(mx, my+15)
        self["tipLabel"] = Label(self["tip"], group=self["group"])._applyTkOption(
            text=self["text"],
            justify='left',
            relief='solid',
            borderwidth=1,
            wraplength=self["wrapLength"]
        )
        self["tipLabel"]._get().pack(ipadx=1)
    def _hidetip(self):
        pin = self["tip"]
        self["tip"] = None
        if pin is not None:
            pin.destroy()
class ScrollBar(Widget):
    """
    Scrollbar Widget can be attached to some Widget using their 'attachScrollbar' method.
    """
    def __init__(self, _master, autoPlace=True, group=None):
        if _isinstance(_master, "Tk") or isinstance(_master, NotebookTab) or _isinstance(_master, "Canvas") or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master": _master, "widget": _ttk.Scrollbar(_master._get()), "autoPlace":autoPlace, "thickness":18, "init": {}}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + ", Frame or Tk instance not: " + str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def callEventOnScrollbarRelease(self):
        """
        Configures Scrollbar to call the 'onScollEvent' on scrollbar release.
        @return:
        """
        self._setAttribute("jump", 1)
    def callEventOnScroll(self):
        """
        Configures Scrollbar to call the 'onScollEvent' on scroll.
        This is the DEFAULT setting.
        @return:
        """
        self._setAttribute("jump", 0)
    def onScrollEvent(self, func, args:list = None, priority:int=0, defaultArgs=False, disableArgs=False):
        """
        Bind on scroll event. Runs given function on trigger

        @param func: function get called on trigger
        @param args: Additional arguments as List.
        @param priority: If several equal events are bound, it's possible to set priorities.
        @param defaultArgs: if True the default tkinter gets passed in bound function instead of Event-instance.
        @param disableArgs: if True no args gets passed.
        @return:
        """
        _EventHandler._registerNewCommand(self, func, args, priority, decryptValueFunc=self._decryptEvent, defaultArgs=defaultArgs, disableArgs=disableArgs)
    def setWidth(self, w:int):
        raise NotImplemented()
        self["widget"]["width"] = w
        self["thickness"] = w-10
        return self
    def set(self, a, b):
        self._get().set(a, b)
    def _decryptEvent(self, args, event):
        return None
class Frame(Widget):
    """
    Widget:
    The Frame is used to group or organize widgets.
    Frames can be places and configured as usualy.
    Once the frame is places it can be used as Master to place other widgets on and relative to the frame.
    """
    def __init__(self, _master, group=None):
        if _isinstance(_master, "Tk") or isinstance(_master, NotebookTab) or _isinstance(_master, "Canvas") or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master": _master,  "widget": _tk.Frame(_master._get())}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def __destroy(self):
        assert self["placed"], "Widget is already destroyed!"
        for id, widg in zip(self["childWidgets"].keys(), self["childWidgets"].values()):
            #EventHandler.unregisterAllEventsFormID(widg["id"])
            self["tkMaster"]._unregisterOnResize(widg)
        del self["master"]["childWidgets"][self["id"]]
        self["registry"].unregisterAll()
        self["tkMaster"]._unregisterOnResize(self)
        WidgetGroup.removeFromAll(self)
        self["widget"].destroy()
        self["destroyed"] = False
        self["placed"] = False
        for w in self["childWidgets"].copy().values():
            w.destroy()
class LabelFrame(Widget):
    """
    Widget:
    Similar the Frame widget.
    The LabelFrame has an outline.
    A name can be set using the 'setText' methods.
    """
    def __init__(self, _master, group=None):
        if _isinstance(_master, "Tk") or isinstance(_master, NotebookTab) or _isinstance(_master, "Canvas") or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master": _master,  "widget": _tk.LabelFrame(_master._get())}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def __destroy(self):
        print("test2<-----")
        assert self["placed"], f"Widget is already destroyed! (LabelFrame)"
        for id, widg in zip(self["childWidgets"].keys(), self["childWidgets"].values()):
            # EventHandler.unregisterAllEventsFormID(widg["id"])
            self["tkMaster"]._unregisterOnResize(widg)
        del self["master"]["childWidgets"][self["id"]]
        self["registry"].unregisterAll()
        self["tkMaster"]._unregisterOnResize(self)
        WidgetGroup.removeFromAll(self)
        self["widget"].destroy()
        self["destroyed"] = False
        self["placed"] = False

        for w in self["childWidgets"].copy().values():
            w.destroy()
class Label(Widget):
    """
    Widget:
    The Label widget is used to display one line text or images.
    """
    def __init__(self, _master, group=None, **kwargs):
        if _isinstance(_master, "Tk") or isinstance(_master, NotebookTab) or _isinstance(_master, "Canvas") or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master":_master,  "widget":_tk.Label(_master._get()), "init":kwargs}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+" or Tk instance not: "+str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def clear(self):
        """
        Clears the displayed Text on the Label.
        @return:
        """
        self.setText("")
        return self
    def setImage(self, img:Union[TkImage, PILImage]):
        """
        Set the image displayed on the Label.
        Use either an 'TkImage' or an 'PILImage' instance.
        @param img:
        @return:
        """
        self["widget"]._image = img._get()
        self["widget"]["image"] = self["widget"]._image
        return self
    def clearImage(self):
        """
        Clears the displayed image.
        @return:
        """
        self["widget"]["image"] = ''
        return self
class Checkbutton(Widget):
    """
    Widget:
    The Checkbutton is basicly a Label with a checkbox on the left.
    """
    def __init__(self, _master, group=None, widgetClass=_tk.Checkbutton):
        self.getValue = self.getState
        self.setValue = self.setState
        if isinstance(_master, _SubMenu):
            self._data = {"master": _master._master,  "widget": _tk.Checkbutton(_master._master._get()), "instanceOfMenu":True}
            _master._widgets.append(["checkbutton", self])
        elif _isinstance(_master, "Tk") or isinstance(_master, NotebookTab) or _isinstance(_master, "Canvas") or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            intVar = _tk.IntVar(_master._get())
            self._data = {"master":_master, "text":"", "widget":widgetClass(_master._get()), "intVar":intVar, "init":{"variable":intVar}}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def __bool__(self):
        return bool(self.getState())
    def _decryptEvent(self, args, event):
        return self.getState()
    def onSelectEvent(self, func, args:list = None, priority:int=0, defaultArgs=False, disableArgs=False):
        """
        Bind on checkbox select event to this widget. Runs given function on trigger.

        @param func: function get called on trigger
        @param args: Additional arguments as List.
        @param priority: If several equal events are bound, it's possible to set priorities.
        @param defaultArgs: if True the default tkinter gets passed in bound function instead of Event-instance.
        @param disableArgs: if True no args gets passed.
        @return:
        """
        _EventHandler._registerNewCommand(self, func, args, priority, decryptValueFunc=self._decryptEvent, defaultArgs=defaultArgs, disableArgs=disableArgs)
        return self
    def toggle(self):
        """
        Toggles the checkbox.

        Selected -> Unselected
        Unselected -> Selected
        @return:
        """
        self.setState(not self.getState())
        return self
    def setSelected(self):
        """
        Set the checkbox selected.
        @return:
        """
        self.setState(True)
        return self
    def setState(self, b:bool):
        """
        Set the checkbox selected or not using the given boolean.
        @param b:
        @return:
        """
        self["intVar"].set(bool(b))
        return self
    def getState(self)->bool:
        """
        Returns the current selection state as boolean.
        @return:
        """
        return bool(self["intVar"].get())
    def setSelectColor(self, c:Union[Color, str]):
        """
        Set the backgroundcolor of the checkbox.
        @param c:
        @return:
        """
        self._setAttribute("selectcolor", c.value if hasattr(c, "value") else c)
        return self
class CheckbuttonTTK(Checkbutton):
    def __init__(self, _master, group=None):
        super().__init__(_master, group, widgetClass=_ttk.Checkbutton)
class Radiobutton:
    """
    Widget:
    This is NOT the widget class.
    This class is only used to bind events or get the current selected radiobutton.
    Use the method 'createNewRadioButton' to create the radiobuttons.
    These can be placed and used as normal widgets.
    """
    def __init__(self, _master, group=None):
        self.getValue = self.getState
        if _isinstance(_master, "Tk") or isinstance(_master, NotebookTab) or _isinstance(_master, "Canvas") or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            intVar = _IntVar(_master)
            self._data = {"master": _master,  "widgets":[], "intVar":intVar, "eventArgs":[], "group":group}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__.__name__))
    def __getitem__(self, item):
        return self._data[item]
    def getState(self)->int:
        """
        Returns the index of selected radiobutton.
        @return:
        """
        return self._data["intVar"].get()
    def setState(self, i:int):
        """
        Set radiobutton on index 'i' selected.
        @param i:
        @return:
        """
        self._data["widgets"][i].setSelected()
        return self
    def createNewRadioButton(self, group=None):
        """
        This method creates a new Radiobutton and returns it.
        The order that the Radiobuttons are added are the related indices wich are used for events.
        The returned widget can be placed and used as normal widget.
        The passed WidgetGroup is applied to this Radiobutton.
        @param group:
        @return:
        """
        rb =_RadioButton(self._data["master"], self._data["intVar"], (group if group is not None else self["group"]))
        self._data["widgets"].append(rb)
        for i in self._data["eventArgs"]:
            _EventHandler._registerNewCommand(rb, i["func"], i["args"], i["priority"], decryptValueFunc=rb._decryptEvent, defaultArgs=i["defaultArgs"], disableArgs=i["disableArgs"])
        return rb
    def onSelectEvent(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False):
        """
        Bind on select event to this widget. Runs given function on trigger.

        @param func: function get called on trigger
        @param args: Additional arguments as List.
        @param priority: If several equal events are bound, it's possible to set priorities.
        @param defaultArgs: if True the default tkinter gets passed in bound function instead of Event-instance.
        @param disableArgs: if True no args gets passed.
        @return:
        """
        self._data["eventArgs"].append({"func":func, "args":args , "priority":priority, "defaultArgs":defaultArgs, "disableArgs":disableArgs})
        for btn in self._data["widgets"]:
            _EventHandler._registerNewCommand(btn, func, args, priority, decryptValueFunc=btn._decryptEvent, defaultArgs=defaultArgs, disableArgs=disableArgs)
        return self
class _RadioButton(Widget):
    """
    Subclass for Radiobuttons.
    Represents a single Radiobutton widget.
    """
    def __init__(self, _master, intVar, group):
        self._data = {"master": _master, "widget": _tk.Radiobutton(_master._get()), "intvar": intVar, "init": {"variable": intVar._get(), "value": intVar._add()}}
        super().__init__(self, self._data, group)
    def setSelected(self):
        """
        Set the Radiobutton selected.
        @return:
        """
        self["intvar"].set(self["widget"]["value"])
        return self
    def getValue(self)->int:
        """
        Returns the Selected Index.
        @return:
        """
        return self["intvar"].get()
    def setSelectColor(self, c:Union[Color, str]):
        """
        Set the backgroundcolor of the radiobutton.
        @param c:
        @return:
        """
        self._setAttribute("selectcolor", c.value if hasattr(c, "value") else c)
        return self
    def flash(self):
        """
        This method changes serveral times between selected color and background color.
        This can be used to indicate that the user has to click on this widget.

        @return:
        """
        self["widget"].flash()
        return self
    def _decryptEvent(self, args, event):
        return self.getText()
class Button(Widget):
    """
    Widget:
    The Button widget is clickable.
    The onclick event can be bound via the 'setCommand' method.
    """
    def __init__(self, _master, group=None, text="", canBePressedByReturn=True, fireOnlyOnce=True, fireInterval:float=0.1, firstDelay:float=0.5):
        if _isinstance(_master, "Tk") or isinstance(_master, NotebookTab) or _isinstance(_master, "Canvas") or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master":_master, "widget":_tk.Button(_master._get()), "canBePressedByReturn":canBePressedByReturn, "instanceOfMenu":False, "init":{"text":text}}
            if not fireOnlyOnce:
                self._data["init"]["repeatdelay"] = int(firstDelay * 1000)
                self._data["init"]["repeatinterval"] = int(fireInterval * 1000)
        elif isinstance(_master, _SubMenu) or isinstance(_master, ContextMenu):
            group = None # not possible!
            if isinstance(_master, ContextMenu): _master = _master["mainSubMenu"]
            self._data = {"master":_master._master, "widget":_tk.Button(_master._master._get()), "instanceOfMenu":True}
            _master._widgets.append(["command", self])
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__))
        super().__init__(self, self._data, group)
    def triggerButtonPress(self, normalRelief=True):
        """
        This method can be used to trigger the Button and its command.
        @param normalRelief: if True the pressanimation is shown otherwise only the bound function is triggered.
        @return:
        """
        if normalRelief: self.setStyle(Style.SUNKEN)
        self.update()
        trigger = self["registry"].getHandler("cmd")
        if trigger is not None: trigger()
        if normalRelief: self.setStyle(Style.RAISED)
        self.update()
    def setActiveBg(self, col:Color):
        """
        Set the active background color.
        Visible if button is pressed.

        @param col: Use Color _Enum, tkinter string or hex-code.
        @return:
        """
        self._setAttribute("activebackground", col.value if hasattr(col, "value") else col)
        return self
    def setActiveFg(self, col:Color):
        """
        Set the active foreground color.
        Visible if button is pressed.

        @param col: Use Color _Enum, tkinter string or hex-code.
        @return:
        """
        self._setAttribute("activeforeground", col.value if hasattr(col, "value") else col)
        return self
    def setStyleOnHover(self, style:Style):
        """
        Changes the Style on hover.
        Use the Style _Enum to change.
        @param style:
        @return:
        """
        self._setAttribute("overrelief", style.value if hasattr(style, "value") else style)
        return self
    def flash(self):
        """
        This method changes serveral times between selected color and background color.
        This can be used to indicate that the user has to click on this widget.

        @return:
        """
        self["widget"].flash()
        return self
    def setCommand(self, cmd:Callable, args:list=None, priority:int=0, disableArgs=False, defaultArgs=False):
        """
        Bind on click event to this widget. Runs given function on trigger.

        @param cmd: function get called on trigger
        @param args: Additional arguments as List.
        @param priority: If several equal events are bound, it's possible to set priorities.
        @param defaultArgs: if True the default tkinter gets passed in bound function instead of Event-instance.
        @param disableArgs: if True no args gets passed.
        @return:
        """
        if cmd is None: return self
        runnable = _EventHandler._registerNewCommand(self, cmd, args, priority, disableArgs=disableArgs, defaultArgs=defaultArgs, onlyGetRunnable=self["instanceOfMenu"])
        if self["instanceOfMenu"]:
            self["widgetProperties"]["command"] = runnable
        elif self["canBePressedByReturn"]:
            _EventHandler._registerNewEvent(self, cmd, EventType.key(Key.RETURN), args, priority=1, disableArgs=disableArgs, defaultArgs=defaultArgs)
        return self
    def setImage(self, img:Union[TkImage, PILImage]):
        """
        Set the image displayed on the Label.
        Use either an 'TkImage' or an 'PILImage' instance.
        @param img:
        @return:
        """
        self["widget"]._image = img._get()
        self["widget"]["image"] = self["widget"]._image
        return self
class Entry(_LockableWidget):
    """
    Widget:
    The Entry is used to ask single line text from the user.
    """
    def __init__(self, _master, group=None, readOnly=False):
        self.getValue = self.getText
        self.setValue = self.setText
        if _isinstance(_master, "Tk") or isinstance(_master, NotebookTab) or _isinstance(_master, "Canvas") or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master":_master,  "widget":_tk.Entry(_master._get())}
            self._setReadOnly(readOnly)
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def attachHorizontalScrollBar(self, sc:ScrollBar):
        """
        Used to attach a horizontal scrollbar to the Entry.
        Pass a Scrollbar instance to this method.
        @param sc:
        @return:
        """
        self["xScrollbar"] = sc
        sc["widget"]["orient"] = _tk.HORIZONTAL
        sc["widget"]["command"] = self._scrollHandler
        self["widget"]["xscrollcommand"] = sc["widget"].set
    def setCursorBlinkDelay(self, d:float):
        """
        Set the cursor blink-delay in seconds.
        @param d:
        @return:
        """
        self._setAttribute("insertofftime",  int(d * 1000))
        self._setAttribute("insertontime", int(d * 1000))
        return self
    def setCursorColor(self, c:Union[Color, str]):
        """
        Set the cursor color.
        @param c:
        @return:
        """
        self._setAttribute("insertbackground", c.value if hasattr(c, "value") else c)
        return self
    def setCursorThickness(self, i:int):
        """
        Set the cursor thickness.
        @param i:
        @return:
        """
        self._setAttribute("insertwidth", i)
        return self
    def setSelectForeGroundColor(self, c:Union[Color, str]):
        """
        Set the select foreground color.
        @param c:
        @return:
        """
        self._setAttribute("selectforeground", c.value if hasattr(c, "value") else c)
        return self
    def setSelectBackGroundColor(self, c:Union[Color, str]):
        """
        Set select background color.
        @param c:
        @return:
        """
        self._setAttribute("selectbackground", c.value if hasattr(c, "value") else c)
    def onUserInputEvent(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False):
        """
        Bind on user input event to this widget. Runs given function on trigger.

        @param func: function get called on trigger
        @param args: Additional arguments as List.
        @param priority: If several equal events are bound, it's possible to set priorities.
        @param defaultArgs: if True the default tkinter gets passed in bound function instead of Event-instance.
        @param disableArgs: if True no args gets passed.
        @return:
        """
        _EventHandler._registerNewEvent(self, func, EventType.KEY_UP, args, priority, decryptValueFunc=self._decryptEvent, defaultArgs=defaultArgs, disableArgs=disableArgs)
        return self
    def hideCharactersWith(self, i:str="*"):
        """
        Hide all characters that are inputted by the user with given char.
        The default char ('*') is set by calling this method wthout arguments.
        Used for password input.
        @param i:
        @return:
        """
        self._setAttribute("show", str(i))
        return self
    @_lockable
    def clear(self):
        """
        Clears the Entry.
        @return:
        """
        self["widget"].delete(0, _tk.END)
        return self
    @_lockable
    def setText(self, text:str):
        """
        Overwrites the text content in the Entry.
        @param text:
        @return:
        """
        self.clear()
        self["widget"].insert(0, str(text))
        return self
    @_lockable
    def addText(self, text:str, index="end"):
        """
        Adds the text at 'index', by default at the end.
        @param text:
        @param index:
        @return:
        """
        self["widget"].insert(index, str(text))
        return self
    def getText(self)->str:
        """
        Returns the text content from the Entry.
        @return:
        """
        return self["widget"].get()
    def _decryptEvent(self, args, event):
        return args
    def _scrollHandler(self, *l):
        op, howMany = l[0], l[1]
        if op == 'scroll':
            units = l[2]
            self["widget"].xview_scroll(howMany, units)
        elif op == 'moveto':
            self["widget"].xview_moveto(howMany)
class Listbox(Widget):
    """
    Widget:
    The user can select one (Default) or multiple items.
    A Scrollbar can also be added.

    """
    def __init__(self, _master, group=None):
        if _isinstance(_master, "Tk") or isinstance(_master, NotebookTab) or _isinstance(_master, "Canvas") or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master":_master,  "widget":_tk.Listbox(_master._get()), "selection_mode":"single", "init":{"selectmode":"single"}, "default_color":Color.DEFAULT}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def __len__(self):
        return self.length()
    def bindArrowKeys(self, widget=None, ifNoSelectionSelect0=True):
        """
        The arrowkeys get bound to navigate up and down via the arrowkeys.
        @param widget: bind to given widget (Default = self)
        @param ifNoSelectionSelect0: Select on arrowkeys index zero if none is selected
        @return:
        """
        def _up(e):
            if self["placed"]:
                selected = self.getSelectedIndex()
                if selected is None or selected == 0:
                    selected = -1
                    self.clearSelection()
                    if ifNoSelectionSelect0: self.setItemSelectedByIndex(0)
                else:
                    if selected > 0:
                        selected -= 1
                        self.setItemSelectedByIndex(selected)

                self.see(selected)
                self["widget"].event_generate("<<ListboxSelect>>")
        def _down(e):
            if self["placed"]:
                selected = self.getSelectedIndex()
                if selected is None:
                    selected = 0
                    if ifNoSelectionSelect0: self.setItemSelectedByIndex(0)
                else:
                    if selected < self.length():
                        selected += 1
                        self.setItemSelectedByIndex(selected)

                self.see(selected)
                self["widget"].event_generate("<<ListboxSelect>>")
        if widget is None: widget = self
        _EventHandler._registerNewEvent(widget, _down, EventType.ARROW_DOWN, [], 0)
        _EventHandler._registerNewEvent(widget, _up, EventType.ARROW_UP, [], 0)
    def see(self, index:Union[float, str]):
        """
        Adjust the position of the listbox so that the line referred to by index is visible.
        'end' for scroll to end.
        @param index:
        @return:
        """
        self["widget"].see(index)
        return self
    def setSelectForeGroundColor(self, c:Union[Color, str]):
        """
        Foregroundcolor applied if item is selected.
        @param c:
        @return:
        """
        self._setAttribute("selectforeground", c.value if hasattr(c, "value") else c)
    def setSelectBackGroundColor(self, c:Union[Color, str]):
        """
        Backgroundcolor applied if item is selected.
        @param c:
        @return:
        """
        self._setAttribute("selectbackground", c.value if hasattr(c, "value") else c)
    def attachVerticalScrollBar(self, sc:ScrollBar):
        """
        Used to attach a vertical scrollbar to the Entry.
        Pass a Scrollbar instance to this method.
        @param sc:
        @return:
        """
        self["yScrollbar"] = sc
        sc["widget"]["orient"] = _tk.VERTICAL
        sc["widget"]["command"] = self["widget"].yview
        self["widget"]["yscrollcommand"] = sc["widget"].set
        return self
    def clearSelection(self):
        """
        Clears the selection.
        @return:
        """
        self["widget"].selection_clear(0, "end")
    def setMultipleSelect(self):
        """
        Set the Listbox in 'multiselectmode'.
        The User can select more than one item.
        @return:
        """
        self._setAttribute("selectmode", "multiple")
        self["selection_mode"] = "multiple"
        return self
    def setSingleSelect(self):
        """
        Set the Listbox in 'singleselectmode'.
        The User can select only one item.
        This is the DEFAULT mode.
        @return:
        """
        self._setAttribute("selectmode", "single")
        self["selection_mode"] = "single"
        return self
    def add(self, entry:str, index="end", color:Union[Color, str]=None):
        """
        Adds an entry to the Listbox.
        For large amount of items the 'addAll' method is way faster!
        @param entry: entry content as string
        @param index: where to insert. At the end by default.
        @param color: Background color of this item.
        @return:
        """
        self["widget"].insert(index, str(entry))
        color = color if color is not None else self["default_color"]
        if len(self.getAllSlots()) != 0:
            self.setSlotBg((self.length()-1 if index=="end" else index), color)
        return self
    def addAll(self, entry:List[str], index:str="end", color:Union[Color, str]=None):
        """
        Adds a list of entrys to the Listbox.
        When adding large amounts of items this is way faster than 'add' method and a for loop.
        @param entry: entry content as string
        @param index: where to insert. At the end by default.
        @param color: Background color of this item.
        @return:
        """
        color = color if color is not None else self["default_color"]
        if entry is None: return self
        if color == Color.WHITE:
            self["widget"].insert(index, *entry)

        else:
            for i in entry:
                self["widget"].insert(index, str(i))
                if len(self.getAllSlots()) != 0:
                    self.setSlotBg(self.length()-1, color)
                self.updateIdleTasks()
        return self
    def length(self)->int:
        """
        Returns the amount of items in Listbox.
        @return:
        """
        return self["widget"].size()
    def clear(self):
        """
        Removes all items from Listbox.
        @return:
        """
        self["widget"].delete(0, _tk.END)
        return self
    def setSlotBgDefault(self, color:Union[Color, str]=Color.WHITE):
        """
        Sets the default color of new added Items.
        @param color:
        @return:
        """
        self["default_color"] = color.value if hasattr(color, "value") else color
        return self
    def setSlotBgAll(self, color:Union[Color, str]=Color.WHITE):
        """
        Set the Backgroundcolor of all slots.
        This can be slow.
        Better is to set the color while adding.
        @param color:
        @return:
        """
        for i in self.getAllSlotIndexes():
            self.setSlotBg(i, color)
        return self
    def setSlotBg(self, index:int, col: Color = Color.WHITE):
        """
        Set backgroundcolor of item a given index.
        @param index:
        @param col:
        @return:
        """
        self["widget"].itemconfig(index, bg=col.value if hasattr(col, "value") else col)
        return self
    def setItemSelectedByIndex(self, index:int, clearFirst=True):
        """
        Set an item selected by given index.
        @param index:
        @param clearFirst: clears the old selection before setting the new.
        @return:
        """
        if clearFirst: self["widget"].selection_clear(0, "end")
        self["widget"].select_set(index)
        return self
    def setItemSelectedByName(self, name:str, clearFirst=True):
        """
        Set the first item with given name selected.
        @param name:
        @param clearFirst: clears the old selection before setting the new.
        @return:
        """
        if clearFirst: self["widget"].selection_clear(0, "end")
        if name in self.getAllSlots():
            self.setItemSelectedByIndex(self.getAllSlots().index(name))
        return self
    def deleteItemByIndex(self, index:int):
        """
        Deletes an item by given index
        @param index:
        @return:
        """
        self["widget"].delete(index)
        return self
    def deleteItemByName(self, name):
        """
        Deletes the first item by given name.
        @param name:
        @return:
        """
        self.deleteItemByIndex(self.getAllSlots().index(name))
    def getIndexByName(self, name:str):
        """
        Returns the (first) index by given name.
        @param name:
        @return:
        """
        return self.getAllSlots().index(name)
    def getNameByIndex(self, index:int):
        """
        Returns the name by given index.
        @param index: 
        @return: 
        """
        return self.getAllSlots()[index]
    def getSelectedIndex(self)->Union[list, int, None]:
        """
        Returns selected index/indices.
        If selectionmode is 'single' -> returns int / None
        If selectionmode is 'multiple' -> returns list / None
        @return:
        """
        if len(self["widget"].curselection()) == 0: return None
        if self["selection_mode"] == "single":
            return int(self["widget"].curselection()[0])
        else:
            return [int(i) for i in self["widget"].curselection()]
    def getSelectedItem(self)->Union[List[str], str, None]:
        """
        Returns selected item/items.
        If selectionmode is 'single' -> returns str / None
        If selectionmode is 'multiple' -> returns list / None
        @return:
        """
        index = self.getSelectedIndex()
        if index is None: return None
        if type(index) == int:
            return self.getNameByIndex(index)
        else:
            return [self.getNameByIndex(i) for i in index]

    def getAllSlotIndexes(self)->List[int]:
        """
        Returns a list of indices for every item in Listbox.
        @return:
        """
        return [i for i in range(self.length())]
    def getAllSlots(self)->List[str]:
        """
        Returns a list containing all items.
        @return:
        """
        return [self["widget"].get(i) for i in range(self.length())]
    def onSelectEvent(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False):
        """
        Binds on select event to the Widget. Runs given function on trigger.

        @param func: function get called on trigger
        @param args: Additional arguments as List.
        @param priority: If several equal events are bound, it's possible to set priorities.
        @param defaultArgs: if True the default tkinter gets passed in bound function instead of Event-instance.
        @param disableArgs: if True no args gets passed.
        @return:
        """
        _EventHandler._registerNewEvent(self, func, EventType.LISTBOX_SELECT, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs, decryptValueFunc=self._decryptEvent)
    def _decryptEvent(self, args, event):
        try:
            w = args.widget
            if self["selection_mode"] == "single":
                return w.get(int(w.curselection()[0]))
            else:
                return [w.get(int(i)) for i in w.curselection()]
        except Exception as e:
            return "CANCEL"
class Scale(Widget):
    """
    Widget:
    Adds a Slider to set values from specified value range.
    """
    def __init__(self, _master, group=None, from_=0, to=100, orient:Orient=Orient.HORIZONTAL):
        self.setResolution = self.setSteps
        if _isinstance(_master, "Tk") or isinstance(_master, NotebookTab) or _isinstance(_master, "Canvas") or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            doubbleVar = _tk.DoubleVar(_master._get())
            self._data = {"master":_master,  "widget":_tk.Scale(_master._get()), "var":doubbleVar, "init":{"variable":doubbleVar, "from_":from_, "to":to, "orient":orient.value if hasattr(orient, "value") else orient}}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def getValue(self)->float:
        """
        Returns the selected value.
        @return:
        """
        return self["var"].get()
    def setValue(self, v:float):
        """
        Set scale value.
        @param v:
        @return:
        """
        self["var"].set(v)
        return self
    def getSlideLocation(self, value=None)->Location2D:
        """
        Returns the slider location on screen.
        @param value: if None current scale value is taken
        @return:
        """
        if value is None: value = self.getValue()
        return Location2D(self["widget"].coords(value))
    def setIntervalIndicators(self, i:float):
        """
        Set the indicator interval.
        @param i: interval
        @return:
        """
        self._setAttribute("tickinterval", i)
        return self
    def setSliderBg(self, color:Color):
        """
        Set the slider background color.
        @param color:
        @return:
        """
        self._setAttribute("troughcolor", color.value if hasattr(color, "value") else color)
        return self
    def setText(self, text:str):
        """
        Set info text above Scale.
        @param text:
        @return:
        """
        self._setAttribute("label", str(text))
    def setValueVisible(self, b:bool=True):
        """
        Set value above the scale visible or hidden.
        @param b:
        @return:
        """
        self._setAttribute("showvalue", b)
        return self
    def setSliderWidth(self, i:int=30):
        """
        Set slider Width.
        Default is 30.
        @param i:
        @return:
        """
        self._setAttribute("sliderlength", i)
        return self
    def setStyle(self, style:Style=Style.RAISED):
        """
        Set scale style.
        @param style:
        @return:
        """
        self._setAttribute("sliderrelief", style.value if hasattr(style, "value") else style)
    def setSteps(self, s:Union[int, float]=1):
        """
        Set slider steps.
        Steps s steps when clicking next to the slider.
        @param s:
        @return:
        """
        self._setAttribute("resolution", s)
        return self
    def onScroll(self, func, args:list=None, priority:int=0):
        """
        Binds on scale scroll event to the Widget. Runs given function on trigger.

        @param func: function get called on trigger
        @param args: Additional arguments as List.
        @param priority: If several equal events are bound, it's possible to set priorities.
        @return:
        """
        _EventHandler._registerNewCommand(self, func, args, priority, decryptValueFunc=self._decryptValue)
        return self
    def _decryptValue(self, a=None):
        return self.getValue()
class Progressbar(Widget):
    """
    Widget:
    Creates a Processbar to indicate process.
    """
    def __init__(self, _master, group=None, values:int=100):
        if _isinstance(_master, "Tk") or isinstance(_master, NotebookTab) or _isinstance(_master, "Canvas") or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master":_master,  "widget":_ttk.Progressbar(_master._get()), "values":values, "value":0}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def setNormalMode(self):
        """
        Set the Processbar to normal mode.
        It can fill from 0 to 100%.
        @return:
        """
        self["widget"].stop()
        self._setAttribute("mode", "determinate")
        return self
    def setAutomaticMode(self, delay=0.01):
        """
        Set the Processbar to automatic mode.
        The green Bar jumps back and forth.
        One cycle takes delay seconds.
        @param delay:
        @return:
        """
        self._setAttribute("mode", "indeterminate")
        self["widget"].start(int(delay*1000))
        return self
    def iter(self, reset=True):
        """
        A for loop can be used to 'iter' through the processbar.
        The for loop index are the steps from the Processbar.
        @param reset: if the Processbar should be set to zero before.
        @return:
        """
        if reset:
            v = self["values"]
            self.reset()
        else:
            v = self["values"] - self["value"]
        for i in range(v):
            self.addValue()
            yield i
    def setOrient(self, o:Orient):
        """
        Set the Processbar orientation using the Orient _Enum.
        Vertical or Horizontal.
        @param o:
        @return:
        """
        self._setAttribute("orient", o.value if hasattr(o, "value") else o)
        return self
    def setValues(self, val:int):
        """
        Set the max Value.
        Value range 0 to 'val'
        @param val:
        @return:
        """
        self["values"] = int(val)
    def update(self):
        """
        Updates the Processbar.
        @return:
        """
        self._setAttribute("value", int((self["value"] / self["values"]) * 100))
        super().update()
        return self
    def addValue(self, v=1):
        """
        Adds a value to the processbar.
        Default maxvalue is 100 (full Processbar).
        Can be chnged by using 'setValues' method.
        @param v:
        @return:
        """
        if self["values"] >= self["value"]+v:
            self["value"] += v
            self._setAttribute("value", int((self["value"] / self["values"]) * 100))
        return self
    def isFull(self)->bool:
        """
        Returns a boolean if the Processbar is full.
        @return:
        """
        return self["values"] <= self["value"]
    def reset(self):
        """
        Sets the bar progress to 0.
        Processbar is empty.
        @return:
        """
        self._setAttribute("value", 0)
        self["value"] = 0
        return self
    def setValue(self, v:int):
        """
        Set the Processbar percentage by value.
        Default maxvalue is 100 (full Processbar).
        Can be chnged by using 'setValues' method.
        @param v:
        @return:
        """
        if self["values"] >= v:
            self["value"] = v
            self._setAttribute("value", int((self["value"] / self["values"]) * 100))
        return self
    def setPercentage(self, p:Union[float, int]):
        """
        Set Processbar percentage,
        Format can be (float) '0.5' -> 50%
        Format can be (int) '50' -> 50%
        @param p:
        @return:
        """
        if str(p).startswith("0."):
            p *= 100
        self._setAttribute("value", p)
        self["value"] = p / 100 * self["values"]
        return self
class _ScrolledText(_tk.Text):
    """
    Private implementation of tkinter.scrolledtext.ScrolledText

    use _ttk.Scrollbar

    """
    def __init__(self, master=None, **kw):
        self.frame = _tk.Frame(master)
        self.vbar = _ttk.Scrollbar(self.frame)
        self.vbar.pack(side=_tk.RIGHT, fill=_tk.Y)

        kw.update({'yscrollcommand': self.vbar.set})
        _tk.Text.__init__(self, self.frame, **kw)
        self.pack(side=_tk.LEFT, fill=_tk.BOTH, expand=True)
        self.vbar['command'] = self.yview
        # hack by https://github.com/enthought/Python-2.7.3/blob/master/Lib/lib-tk/ScrolledText.py
        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        text_meths = vars(Text).keys()
        methods = vars(_tk.Pack).keys() | vars(_tk.Grid).keys() | vars(_tk.Place).keys()
        methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))
    def __str__(self):
        return str(self.frame)
class Text(_LockableWidget):
    """
    Widget:
    Textbox where the user can input Text.
    Can also be user to display multiline text.
    Text widget can be made read only.
    Colors and font can be changed individually.
    """
    def __init__(self, _master, group=None, readOnly=False, forceScroll=False, scrollAble=False):
        self.getContent = self.getText
        if _isinstance(_master, "Tk") or isinstance(_master, NotebookTab) or _isinstance(_master, "Canvas") or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master": _master,  "widget": _ScrolledText(_master._get()) if scrollAble else _tk.Text(_master._get()), "forceScroll":forceScroll, "tagCounter":0, "scrollable":scrollAble}
            self._setReadOnly(readOnly)
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def addLine(self, text:str, color:Union[Color, str]="black", font:Font=None):
        """
        Adds a Line of text to the Textbox widget.
        @param text:
        @param color: color of that line. Default: BLACK
        @return:
        """
        if not text.endswith("\n"): text = text+"\n"
        self.addText(text, color, font)
        return self
    def addLineWithTimeStamp(self, text:str, color:Union[Color, str]="black"):
        """
        Adds a Line of text with a timestamp to the Textbox widget.
        @param text:
        @param color:
        @return:
        """
        if not text.endswith("\n"): text = text+"\n"
        self.addText(strftime("[%H:%M:%S]: ")+text, color)
        return self
    def setStrf(self, text:str):
        """
        Clears the Text.
        View 'Text.addStrf' for further information.
        @param text:
        @return:
        """
        self.clear()
        self.addStrf(text)
        return self
    def addStrf(self, text:str):
        """
        Adds text to the Textbox.
        This text can be colored by using following color codes in the string.

        Color-Codes:
        §D: DEFAULT
        §W: WHITE
        §B: BLACK

        §r: RED
        §g: GREEN
        §b: BLUE
        §c: CYAN
        §y: YELLOW
        §m: MAGENTA

        @param text:
        @return:
        """
        #TODO add font
        #TODO add §rgb(r, g, b)
        colors = {'D':Color.DEFAULT,
                  'W':Color.WHITE,
                  'B':Color.BLACK,
                  'r':Color.RED,
                  'g':Color.GREEN,
                  'b':Color.BLUE,
                  'c':Color.CYAN,
                  'y':Color.YELLOW,
                  'm':Color.MAGENTA,
                  'o':Color.ORANGE}

        _text = text
        for i in ['§D', '§W', '§B', '§r', '§g', '§b', '§c', '§y', '§m', '§o']:
            _text = _text.replace(i, "")
        content = self.getText()
        self.addText(_text)  # text without colorsmarkers
        line = _line = content.count("\n")  # 1
        firstMarkerChar = len(content.split("\n")[-1]) + len(text.split("§")[0])  # TODO prüfen wenn text nicht mit tag beginnt
        for i, textSection in enumerate(text.split("§")[1:]):
            firstMarker = str(line) + "." + str(firstMarkerChar)
            line += textSection.count("\n")
            if _line != line:  # clear fist marker at line change
                firstMarkerChar = 0
                _line = line
            if textSection.count("\n") > 0:  # section -> mehrere zeilen
                _textSectionLastLength = len(textSection.split("\n")[-1])  # section enthält keine Farbe
            else:
                _textSectionLastLength = len(textSection.split("\n")[-1]) - 1  # section nur 1 zeile (dann farbe entfernen)
            secondMarker = str(line) + "." + str(firstMarkerChar + _textSectionLastLength)
            if textSection[0] in colors.keys():  # check if tag is a valid color
                _id = "".join([_choice(ascii_lowercase) for _ in range(30)])
                self["widget"].tag_add(_id, firstMarker, secondMarker)
                self["widget"].tag_config(_id, foreground=colors[textSection[0]].value)
            else:
                print(f"'{textSection}' has no valid color tag.")
            firstMarkerChar = int(secondMarker.split(".")[1])
    def setText(self, text:str, color:Union[Color, str]="black", font:Font=None):
        """
        Overwrites the text with 'text'.
        @param text:
        @return:
        """
        self.clear()
        self.addText(text, color, font)
        return self
    @_lockable
    def addText(self, text:str, color:Union[Color, str]="black", font:Font=None):
        """
        Adds text to the Text box.
        Can be colored. Default: BLACK
        @param text:
        @param color:
        @param font:
        @return:
        """
        color = color.value if hasattr(color, "value") else color
        self["tagCounter"]+=1
        content = self.getText()
        self["widget"].insert("end", str(text))
        if color != "black" or font is not None:
            line = content.count("\n")
            firstMarkerChar = len(content.split("\n")[-2])

            contentAfter = self.getText()

            secline = contentAfter.count("\n")
            secMarkerChar = len(contentAfter.split("\n")[-2])

            self["widget"].tag_add(str(self["tagCounter"]),
                                   str(line) + "." + str(firstMarkerChar),
                                   str(secline) + "." + str(secMarkerChar)
                                   )
            self["widget"].tag_config(str(self["tagCounter"]), foreground=color, font=None if font is None else font._get())
        if self["forceScroll"]:
            self["widget"].see("end")
        self["tagCounter"]+=text.count("\n")
        return self
    def getText(self)->str:
        """
        Returns Text content.
        @return:
        """
        return self["widget"].get(0.0, "end")
    def scrollDown(self):
        """
        Scrolls all the way down.
        Redundant to: 'Text.see("end")'
        @return:
        """
        self["widget"].see("end")
        return self
    @_lockable
    def clear(self):
        """
        Clears the Textbox.
        @return:
        """
        self["widget"].delete(0.0, _tk.END)
        for i in self["widget"].tag_names():
            self["widget"].tag_delete(i)
        self["tagCounter"] = 0
        return self
    def getSelectedText(self)->Union[str, None]:
        """
        Returns the selected text.
        Returns None if no text is selected.
        @return:
        """
        try:
            return self["widget"].get("sel.first", "sel.last")
        except _tk.TclError:
            return None
    def onUserInputEvent(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False):
        """
        Binds on user input event to the widget. Runs given function on trigger.

        @param func: function get called on trigger
        @param args: Additional arguments as List.
        @param priority: If several equal events are bound, it's possible to set priorities.
        @param defaultArgs: if True the default tkinter gets passed in bound function instead of Event-instance.
        @param disableArgs: if True no args gets passed.
        @return:
        """
        _EventHandler._registerNewEvent(self, func, EventType.KEY_UP, args, priority, decryptValueFunc=self._decryptEvent, defaultArgs=defaultArgs, disableArgs=disableArgs)
        #_EventHandler.registerNewValidateCommand(self, func, [], "all", decryptValueFunc=self._decryptEvent, defaultArgs=defaultArgs, disableArgs=disableArgs)
        return self
    def setSelectForeGroundColor(self, c:Union[Color, str]):
        """
        Set select foregroundcolor.
        @param c:
        @return:
        """
        self._setAttribute("selectforeground", c.value if hasattr(c, "value") else c)
    def setSelectBackGroundColor(self, c:Union[Color, str]):
        """
        Set select background color.
        @param c:
        @return:
        """
        self._setAttribute("selectbackground", c.value if hasattr(c, "value") else c)
    def setCursorColor(self, c:Union[Color, str]):
        """
        Set cursor color.
        @param c:
        @return:
        """
        self._setAttribute("insertbackground", c.value if hasattr(c, "value") else c)
        return self
    def setCursorThickness(self, i:int):
        """
        Set Cursor thickness.
        @param i:
        @return:
        """
        self._setAttribute("insertwidth", i)
        return self
    def setCursorBlinkDelay(self, d:float):
        """
        Set Cursor blink delay in seconds.
        @param d:
        @return:
        """
        self._setAttribute("insertofftime",  int(d * 1000))
        self._setAttribute("insertontime", int(d * 1000))
        return self
    def setUndo(self, b:bool, maxUndo=-1):
        """
        Enables or disables the Ctrl+Z / Ctrl+y undo/redo functionallity.
        Default: DISABLED
        @param b:
        @param maxUndo: how many undo opperations are saved in stack. -1 for infinite
        @return:
        """
        self._setAttribute("undo", int(b))
        self._setAttribute("maxundo", maxUndo)
        return self
    def setWrapping(self, w:Wrap):
        """
        Set text wrapping using 'Wrap' _Enum.
        Default: NONE
        @param w:
        @return:
        """
        self._setAttribute("wrap", w.value if hasattr(w, "value") else w)
        return self
    def _decryptEvent(self, args, event):
        return self.getText()
#continue!

class _SubFolder:
    def __init__(self, parent, _data):
        self._parent = parent
        self._data = _data
    def __getitem__(self, item):
        return self._data[item]
    def __setitem__(self, key, value):
        self._data[key] = value
    def addEntry(self, *args, index="end"):
        if isinstance(args[0], tuple) or isinstance(args[0], list):
            args = args[0]
        if len(self["headers"]) == 0:
            raise TKExceptions.InvalidHeaderException("Set Tree Headers first!")
        if len(self["headers"]) != len(list(args)):
            raise TKExceptions.InvalidHeaderException("Length of headers must be the same as args of addEntry!")
        self["widget"].insert(parent=self._parent, index=index, text=args[0], values=args[1:])
    def createFolder(self, *args, index="end"):
        if isinstance(args[0], tuple) or isinstance(args[0], list):
            args = args[0]
        if len(self["headers"]) == 0:
            raise TKExceptions.InvalidHeaderException("Set Tree Headers first!")
        if len(self["headers"]) != len(list(args)):
            raise TKExceptions.InvalidHeaderException("Length of headers must be the same as args of addEntry!")
        parent = self["widget"].insert(parent=self._parent, index=index, text=args[0], values=args[1:])
        return _SubFolder(parent, self._data)
class TreeViewElement:
    def __init__(self, tv, _id=None):
        if isinstance(tv, TreeView):
            self._data = {"master":tv, "id":_id}
        elif isinstance(tv, TreeViewElement):
            self._data = tv._data
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be TreeViewElement instance not: " + str(tv.__class__.__name__))

    #def __lt__(self, other):
        #return 1 < other.score
    def setFont(self):
        pass
    def setImage(self):
        pass
    def setFg(self, color:str | Color):
        return self
    def getIndex(self):
        pass
    def getKeys(self):
        pass
    def getValues(self):
        pass
class TreeView(Widget):
    """TODO
    tag_configure:
        font, image, foreground


    """
    def __init__(self, _master, group=None):
        if _isinstance(_master, "Tk") or isinstance(_master, NotebookTab) or _isinstance(_master, "Canvas") or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master": _master,  "widget":_ttk.Treeview(_master._get()), "headers":[], "elements":[], "onHeaderClick":None, "use_index":False, "select_mode":"single"}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def onDoubleSelectEvent(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False, useIndex=False):
        event = _EventHandler._registerNewEvent(self, func, Mouse.DOUBBLE_LEFT, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs, decryptValueFunc=self._decryptEvent)
        event["use_index"] = useIndex
        return self
    def onSingleSelectEvent(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False, useIndex=False):
        event = _EventHandler._registerNewEvent(self, func, Mouse.LEFT_CLICK_RELEASE, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs, decryptValueFunc=self._decryptEvent)
        event["use_index"] = useIndex
        return self
    def onArrowKeySelectEvent(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False, bindToOtherWidget=None, useIndex=False):
        widget = self
        if bindToOtherWidget is not None:
            widget = bindToOtherWidget
        event1 = _EventHandler._registerNewEvent(widget, func, EventType.KEY_UP + EventType.ARROW_UP, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs, decryptValueFunc=self._decryptEvent)
        event1["use_index"] = useIndex
        event2 = _EventHandler._registerNewEvent(widget, func, EventType.KEY_UP + EventType.ARROW_DOWN, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs, decryptValueFunc=self._decryptEvent)
        event2["use_index"] = useIndex
        return self
    def attachVerticalScrollBar(self, sc: ScrollBar):
        self["yScrollbar"] = sc
        sc["widget"]["orient"] = _tk.VERTICAL
        sc["widget"]["command"] = self["widget"].yview
        self["widget"]["yscrollcommand"] = sc["widget"].set
        return self
    def _decryptEvent(self, args, event):
        self["tkMaster"].updateIdleTasks()
        ids = self["widget"].selection()
        if not len(ids): return None
        items = []
        for id_ in ids:
            item = self["widget"].item(id_)
            if event is not None and event["use_index"]:
                items.append(
                    self._getIds().index(id_)
                )
                continue
            a = {self["headers"][0]:item["text"]}
            for i, h in enumerate(self["headers"][1:]): a[h] = item["values"][i]
            items.append(a)
        if self["select_mode"] == "single": return items[0]
        return items
    def _____decryptEvent(self, args):
        self["tkMaster"].updateIdleTasks()
        ids = self["widget"].selection()
        if len(ids) == 0: return None
        #if id_ == "": return None
        items = []
        for id_ in ids:
            item = self["widget"].item(id_)
            a = {self["headers"][0]:item["text"]}
            for i, h in enumerate(self["headers"][1:]): a[h] = item["values"][i]
            items.append(a)
        return items
    def _getDataFromId(self, id_):
        item = self["widget"].item(id_)
        a = {self["headers"][0]:item["text"]}
        for i, h in enumerate(self["headers"][1:]): a[h] = item["values"][i]
        return a
    def getSelectedItem(self)->list | dict | None:
        return self._decryptEvent(None, None)
    def clear(self):
        if self.length() == 0: return self
        self["widget"].delete(*self["widget"].get_children())
        self["elements"] = []
        return self
    def setTableHeaders(self, *args):
        if isinstance(args[0], tuple) or isinstance(args[0], list):
            args = args[0]
        self["headers"] = [str(i) for i in args]
        self._setAttribute("columns", self["headers"][1:])
        self["widget"].column("#0", stretch=False)
        self["widget"].heading("#0", text=self["headers"][0], anchor="w", command=lambda a=self["headers"][0], b=0:self._clickHeader((a, b)))
        for i, header in enumerate(self["headers"][1:]):
            self["widget"].column(header, stretch=False)
            self["widget"].heading(header, text=header, anchor="w", command=lambda a=header, b=1+i:self._clickHeader((a, b)))
    def addEntry(self, *args, index="end", image=None, tag:str | tuple=None):
        if isinstance(image, TkImage) or isinstance(image, PILImage):
            image = image._get()
        if isinstance(args[0], tuple) or isinstance(args[0], list):
            args = args[0]
        if len(self["headers"]) == 0:
            raise TKExceptions.InvalidHeaderException("Set Tree Headers first!")
        if len(self["headers"]) != len(list(args)):
            raise TKExceptions.InvalidHeaderException("Length of headers must be the same as args of addEntry!")

        data = {
            "text":args[0],
            "values":args[1:]
        }
        if image is not None: data["image"] = image
        if tag is not None:
            if type(tag) == tuple:
                data["tag"] = tag
            else:
                data["tag"] = (tag,)
        _id = self["widget"].insert(parent="", index=index, **data)
        entry = TreeViewElement(self, _id)
        self["elements"].append(entry)
        return self
    def setBgColorByTag(self, tag:str, color:Color | str):
        color = color.value if hasattr(color, "value") else color
        self["widget"].tag_configure(tag, background=color)
        return self
    def setFgColorByTag(self, tag:str, color:Color | str):
        color = color.value if hasattr(color, "value") else color
        self["widget"].tag_configure(tag, foreground=color)
        return self
    def setEntry(self, *args, index=0):
        index = self._getIds()[index]
        #if isinstance(image, TkImage) or isinstance(image, PILImage):
        #    image = image._get()
        if isinstance(args[0], tuple) or isinstance(args[0], list):
            args = args[0]
        if len(self["headers"]) == 0:
            raise TKExceptions.InvalidHeaderException("Set Tree Headers first!")
        if len(self["headers"]) != len(list(args)):
            raise TKExceptions.InvalidHeaderException("Length of headers must be the same as args of addEntry!")
        #if image is not None: _id = self["widget"].item(index, parent="", text=args[0], values=args[1:], image=image)
        else: _id = self["widget"].item(index, text=args[0], values=args[1:])
        return self
    def createFolder(self, *args, index="end"):
        if isinstance(args[0], tuple) or isinstance(args[0], list):
            args = args[0]
        if len(self["headers"]) == 0:
            raise TKExceptions.InvalidHeaderException("Set Tree Headers first!")
        if len(self["headers"]) != len(list(args)):
            raise TKExceptions.InvalidHeaderException("Length of headers must be the same as args of addEntry!")
        parent = self["widget"].insert(parent="", index=index, text=args[0], values=args[1:])
        return _SubFolder(parent, self._data)
    def setNoSelectMode(self):
        self._setAttribute("selectmode", "none")
        return self
    def setMultipleSelect(self):
        self._setAttribute("selectmode", "extended")
        self["select_mode"] = "multiple"
        return self
    def setSingleSelect(self):
        self._setAttribute("selectmode", "browse")
        self["select_mode"] = "single"
        return self
    def clearSelection(self):
        for item in self["widget"].selection():
            self["widget"].selection_remove(item)
        return self
    def see(self, index):
        if len(self._getIds()) > index and len(self._getIds()):
            self["widget"].see(self._getIds()[index])
        return self
    def onSelectHeader(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False, useIndex=False):
        self["onHeaderClick"] = _EventHandler._getNewEventRunnable(self, func, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs)
        self["use_index"] = useIndex
        return self
    def _clickHeader(self, hName):
        if self["onHeaderClick"] is not None:
            handler = self["onHeaderClick"]
            handler.event["value"] = hName[0] if not self["use_index"] else hName[1]
            handler()
    #TODO add length from subFolders!
    def length(self):
        return len(self._getIds())
    #TODO test after resorting items -> _getIds correct?
    def setItemSelectedByIndex(self, index:int, clearFirst=True):
        assert index < len(self._getIds()), "index is too large: \n\tListbox_length: "+str(len(self._getIds()))+"\n\tIndex: "+str(index)
        if clearFirst: self["widget"].selection_set(self._getIds()[index])
        else: self["widget"].selection_add(self._getIds()[index])
        return self
    """
    def setItemSelectedByName(self, name, clearFirst=True):
        if clearFirst: self["widget"].selection_clear(0, "end")
        if name in self.getAllSlots():
            self.setItemSelectedByIndex(self.getAllSlots().index(name))
        return self
    """
    def getSize(self):
        return len(self._getIds())
    def deleteItemByIndex(self, index):
        self["widget"].delete(self._getIds()[index])
        return self
    def getIndexByName(self, item):
        return self.getAllSlots().index(item)
    def getDataByIndex(self, index)->dict:
        return self._getDataFromId(self._getIds()[index])
    def getSelectedIndex(self)->int | None | list:
        if len(self["widget"].selection()) == 0: return None
        if self["select_mode"] == "single":
            return self._getIds().index(self["widget"].selection()[0])
        else:
            ids = self._getIds()
            return [ids.index(i) for i in self["widget"].selection()]
    def getAllSlotIndexes(self):
        return [i for i in range(self.length())]
    def getAllSlots(self):
        return [self["widget"].item(i) for i in self._getIds()]
    def _getIds(self):
        return self["widget"].get_children()
class SpinBox(_LockableWidget):
    def __init__(self, _master, group=None, optionList:list=(), readOnly=True):
        if _isinstance(_master, "Tk") or isinstance(_master, NotebookTab) or _isinstance(_master, "Canvas") or isinstance(_master, Frame):
            self._data = {"master": _master,  "widget": _tk.Spinbox(_master._get()), "readonly":readOnly, "init":{"state":"readonly" if readOnly else "normal", "values":list(optionList)}}
            self._setReadOnly(readOnly)
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + ", Frame or Tk instance not: " + str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def onButtonClick(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False):
        _EventHandler._registerNewCommand(self, func, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs, decryptValueFunc=self._decryptEvent)
    def onUserInputEvent(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False):
        _EventHandler._registerNewEvent(self, func, EventType.KEY_UP, args, priority, decryptValueFunc=self._decryptEvent, defaultArgs=defaultArgs, disableArgs=disableArgs)
    @_lockable
    def setValue(self, v, clearFirst=True):
        if clearFirst: self.clear()
        self["widget"].insert(0, str(v))
        return self
    def getValue(self)->str:
        return self["widget"].get()
    @_lockable
    def setOptionList(self, l:list):
        self._setAttribute("values", l)
    def clear(self):
        self["widget"].delete(0, "end")
    def setButtonStyle(self, style:Style):
        self._setAttribute("buttondownrelief", style.value if hasattr(style, "value") else style) #wtf
        self._setAttribute("buttonup", style.value if hasattr(style, "value") else style)
        return self
    def setButtonBackground(self, color:Color):
        self._setAttribute("buttonbackground", color.value if hasattr(color, "value") else color)
        return self
    def setButtonCursor(self, cursor:Cursor):
        self._setAttribute("buttoncursor", cursor.value if hasattr(cursor, "value") else cursor)
        return self
    def setCursorColor(self, c:Color):
        self._setAttribute("insertbackground", c.value if hasattr(c, "value") else c)
        return self
    def setCursorThickness(self, i:int):
        self._setAttribute("insertwidth", i)
        return self
    def setCursorBlinkDelay(self, d:float):
        self._setAttribute("insertofftime",  int(d * 1000))
        self._setAttribute("insertontime", int(d * 1000))
        return self
    def _decryptEvent(self, args, event):
        return self.getValue()
class DropdownMenu(_LockableWidget):
    def __init__(self, _master, group=None, optionList:list=[], readonly=True):
        if _isinstance(_master, "Tk") or isinstance(_master, NotebookTab) or _isinstance(_master, "Canvas") or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            stringVar = _tk.StringVar()
            self._data = {"master": _master,  "widget":_ttk.Combobox(_master._get(), textvariable=stringVar), "values":optionList, "stringVar":stringVar, "readonly":readonly, "init":{"state":"readonly" if readonly else "normal", "values":list(optionList)}}
            self._setReadOnly(readonly)
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def setReadOnly(self, b=True):
        self["readonly"] = b
        self._setAttribute("state", "readonly")
        return self
    def setEnabled(self, e=False):
        if self["readonly"] and not e:
            self._setAttribute("state", "readonly")
        else:
            self._setAttribute("state", "normal")
        return self
    def onSelectEvent(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False):
        _EventHandler._registerNewEvent(self, func, EventType.COMBOBOX_SELECT, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs, decryptValueFunc=self._decryptEvent)
        return self
    def onDropdownExpand(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False):
        _EventHandler._registerNewCommand(self, func, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs, cmd="postcommand")
        return self
    def onUserInputEvent(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False):
        _EventHandler._registerNewValidateCommand(self, func, args, priority, "all", decryptValueFunc=self._decryptEvent2, defaultArgs=defaultArgs, disableArgs=disableArgs)
        return self
    @_lockable
    def setValueByIndex(self, i:int):
        self["widget"].current(i)
        return self
    def getSelectedIndex(self)-> int | None:
        val = self["widget"].get()
        if val in self._data["values"]:
            return self._data["values"].index(val)
        return None
    @_lockable
    def clear(self):
        self["widget"].delete(0, "end")
        return self
    def setText(self, text):
        self.setValue(text)
        return self
    @_lockable
    def setValue(self, text, clearFirst=True):
        if clearFirst: self["widget"].delete(0, "end")
        self["widget"].insert(0, str(text))
        return self
    def getValue(self):
        return self["widget"].get()
    @_lockable
    def setOptionList(self, it:List[str]):
        self["values"] = it
        self._setAttribute("values", it)
        return self
    def addOption(self, i:str):
        self["values"].append(i)
        self.setOptionList(self["values"])
        return self
    def _decryptEvent(self, args, event):
        return self["widget"].get()
    def _decryptEvent2(self, args, event):
        return args
class Separator(Widget):
    def __init__(self, _master, group=None):
        if _isinstance(_master, "Tk") or isinstance(_master, NotebookTab) or _isinstance(_master, "Canvas") or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master": _master,  "widget":_ttk.Separator(_master._get())}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
class TaskBar(Widget):
    def __init__(self, _master, group=None):
        if _isinstance(_master, "Tk") or isinstance(_master, NotebookTab) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            if _master["hasMenu"]: raise RuntimeError("You cannot apply two Menus to the Window!") #@TODO Runtime ???
            _master["hasMenu"] = True
            self._data = {"master": _master,  "widget": _tk.Menu(_master._get(), tearoff=False), "subMenu":[], "group":group}
            _master._get().config(menu=self._data["widget"])
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def createSubMenu(self, name:str):
        m = _SubMenu(self["master"], self["widget"], self._data, name, self["group"])
        #_SubMenu._SUB_MENUS.append(m)
        self["subMenu"].append(m)
        self["widget"].add("cascade", label=name, menu=m._menu)
        return m
    def place(self, x=0, y=0, width=None, height=None, anchor=Anchor.UP_LEFT):
        pass
    def grid(self, row=0, column=0):
        pass
    def create(self):
        for i in self["subMenu"]: i.create()
class _SubMenu:
    _SUB_MENUS = []
    def __init__(self, master, menu, _data, name, group):
        self._id = "".join([str(_randint(0,9)) for _ in range(15)])
        self._widgets = [] #[["command", <type: Button>], ["cascade", <type: Button>, <type: SubMenu>]]
        self._data = _data
        self._name = name
        self._group = group
        self._data["created"] = False
        self._master = master
        self._masterMenu = menu
        self._menu = _tk.Menu(menu, tearoff=False)
        if group is not None:
            # dummy widget for Group
            self._wid = Widget(None, {"master":self._master, "widget":self._menu}, group)




    def clear(self):
        """
        for i in self._widgets:
            if i[1] is not None and "text" in i[1]["widgetProperties"].keys():
                try:
                    self._menu.delete(i[1]["widgetProperties"]["text"])
                except:
                    pass
                    """
        for i in range(len(self._widgets)+1):
            try:
                self._menu.delete(0)
            except Exception as e:
                print(e)
        self._widgets = []
    def createSubMenu(self, button:Button, group):
        m = _SubMenu(self._master, self._menu, self._data, (button["widgetProperties"]["text"] if "text" in button["widgetProperties"].keys() else ""), group)
        self._widgets.append(["cascade", button, m])
        return m
    def addSeparator(self):
        self._widgets.append(["separator", None])
    def create(self): #@TODO fix if menus are created after mainloop
        #if self._data["created"]: return#@TODO FIX self._data["create"] is True
        for widget in self._widgets:
            if widget[1] is not None:
                _data = widget[1]["widgetProperties"].copy()
                if _data.keys().__contains__("text"): _data["label"] = _data["text"]
                if widget[0] == "cascade": _data["menu"] = widget[2]._menu if hasattr(widget[2], "_menu") else widget[2]
                self._menu.add(widget[0], **{k:v for k, v in zip(_data.keys(), _data.values()) if ['accelerator', 'activebackground', 'activeforeground', 'background', 'bitmap', 'columnbreak', 'command', 'compound', 'font', 'fg', 'bg', 'hidemargin', 'image', 'label', 'menu', 'offvalue', 'onvalue', 'selectcolor', 'selectimage', 'state', 'underline', 'value', 'variable'].__contains__(k)})
                if widget[0] == "cascade" and hasattr(widget[2], "create"):
                    widget[2].create()
            else:
                #print(type(widget[0]), widget)
                self._menu.add(widget[0], {})
        self._data["created"] = True
class ContextMenu(Widget):
    def __init__(self, _master, group=None, closable=True, eventType:Union[EventType, Key, Mouse, None]=EventType.key(Mouse.RIGHT_CLICK)):
        if hasattr(_master, "_get"):
            self._data = {"master": _master,  "widget": _tk.Menu(_master._get(), tearoff=0), "subMenu":[], "closable":closable, "eventType":eventType, "group":group}
            if eventType is not None: _EventHandler._registerNewEvent(_master, self.open, eventType, [], 1, decryptValueFunc=self._decryptEvent, defaultArgs=False, disableArgs=False)
            self._data["mainSubMenu"] = self._createSubMenu()
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__.__name__))
        super().__init__(self, self._data, group)

    def _createSubMenu(self):
        m = _SubMenu(self["master"], self["widget"], self._data, "", self["group"])
        m._menu = self["widget"]
        self["subMenu"].append(m)
        return m
    def addSeparator(self):
        self["mainSubMenu"]._widgets.append(["separator", None])
    def createSubMenu(self, button:Button)->_SubMenu:
        return self["mainSubMenu"].createSubMenu(button, self["group"])
    def bindToWidget(self, widg):
        _EventHandler._registerNewEvent(widg, self.open, self["eventType"], [], 1, decryptValueFunc=self._decryptEvent, defaultArgs=False, disableArgs=False)
    def open(self, loc:Location2D | Event):
        if isinstance(loc, Event):
            if loc.getValue() is not None:
                loc = Location2D(loc.getValue())
            else:
                loc = Location2D(
                    loc.getTkArgs().x_root,
                    loc.getTkArgs().y_root,
                )
        loc.toInt()
        try:
            self["widget"].tk_popup(loc.getX(), loc.getY())
        except Exception as e:
            print(e)
        finally:
            if not self["closable"]:#fuer Fabi :^)
                self["widget"].grab_release()
        return self
    def _decryptEvent(self, e, event):
        if isinstance(e, Event):
            e = e.getTkArgs()
        # why -> Error
        return Location2D(e.x_root, e.y_root)
    def place(self, x=0, y=0, width=None, height=None, anchor=Anchor.UP_LEFT):
        pass
    def grid(self, row=0, column=0):
        pass
    def create(self):
        for i in self["subMenu"]:
            i.create()
class NotebookTab(Widget):
    def __init__(self, _master, notebook=None, name=None, group=None):
        self.setTabName = self.setText
        if _isinstance(_master, "Tk") or isinstance(_master, NotebookTab) or _isinstance(_master, "Canvas") or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master": notebook, "widget": _tk.Frame(notebook._get()), "tabWidget": notebook, "tabId": None, "name":name}
            notebook._get().add(self._data["widget"], text=name)
            self._data["tabId"] = self.getNumberOfTabs()-1
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + ", Frame or Tk instance not: " + str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def getTabIndex(self):
        return self["tabId"]
    def getTabName(self):
        return self["tabWidget"]._get().tab(self["tabId"], "text")
    def setText(self, text):
        self["tabWidget"]._get().tab(self["tabId"], text=text)
        return self
    def setSelected(self):
        self["tabWidget"]._get().select(self["tabId"])
        return self
    def getNumberOfTabs(self):
        return self["tabWidget"]._get().index("end")
    def __destroy(self):

        if not self["placed"]:
            print("!! ALREADY destroyd tab name" + self["name"])
            raise
        #assert self["placed"], f"Widget is already destroyed! {self['name']} {self}"
        print("destroy tab name"+self["name"])
        for id, widg in zip(self["childWidgets"].keys(), self["childWidgets"].values()):
            # EventHandler.unregisterAllEventsFormID(widg["id"])
            self["tkMaster"]._unregisterOnResize(widg)
        del self["master"]["childWidgets"][self["id"]]
        self["registry"].unregisterAll()
        self["tkMaster"]._unregisterOnResize(self)
        WidgetGroup.removeFromAll(self)
        self["widget"].destroy()
        self["destroyed"] = False
        self["placed"] = False
        for w in self["childWidgets"].copy().values():
            w.destroy()
class Notebook(Widget):
    _INITIALIZED = False
    _STYLE = None
    def __init__(self, _master, group=None, closable=False):
        if not self._INITIALIZED and closable:
            Notebook._STYLE = self._initializeCustomStyle()
            Notebook._INITIALIZED = True
        if _isinstance(_master, "Tk") or isinstance(_master, NotebookTab) or _isinstance(_master, "Canvas") or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master":_master,  "widget":_ttk.Notebook(_master._get()), "tabIndexList":[], "runnable":None, "group":group, "init":{"func":self._init, "style":"CustomNotebook" if closable else ""}}
            if closable:
                self._get().bind("<ButtonPress-1>", self._on_close_press, True)
                self._get().bind("<ButtonRelease-1>", self._on_close_release)
                self._active = None
                self._name = ""
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__.__name__))
        super().__init__(self, self._data, None)
    def _init(self):
        self.onTabSelectEvent(self._updateTab)
    def onTabSelectEvent(self, func, args:list=None, priority:int=0, disableArgs=False, defaultArgs=False):
        _EventHandler._registerNewEvent(self, func, EventType.customEvent("<<NotebookTabChanged>>"), args, priority, decryptValueFunc=self._decryptEvent, disableArgs=disableArgs, defaultArgs=defaultArgs)
    def setCtrlTabEnabled(self):
        self["widget"].enable_traversal()
        return self
    def getSelectedTabIndex(self):
        return self["widget"].index("current")
    def getSelectedTabName(self):
        return self["widget"].tab(self.getSelectedTabIndex(), "text")
    def createNewTab(self, name, group=None)->NotebookTab:
        nbt = NotebookTab(self["master"], self, name)
        self["tabIndexList"].append(nbt)
        if group is None: group = self["group"]
        if group is not None: group.add(nbt)
        self._addChildWidgets(nbt)
        return nbt
    def _decryptEvent(self, args, event):
        return self.getSelectedTabIndex()
    def _initializeCustomStyle(self):
        style = _ttk.Style()
        self.images = (
            _tk.PhotoImage("img_close",
                          data="R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs="),
            _tk.PhotoImage("img_closeactive",
                          data="R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs="),
            _tk.PhotoImage("img_closepressed",
                          data="R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs=")
        )

        style.element_create("close", "image", "img_close",
                             ("active", "pressed", "!disabled", "img_closepressed"),
                             ("active", "!disabled", "img_closeactive"),
                             border=8, sticky='')
        style.layout("CustomNotebook", [("CustomNotebook.client", {"sticky": "nswe"})])
        style.layout("CustomNotebook.Tab", [
            ("CustomNotebook.tab", {
                "sticky": "nswe",
                "children": [
                    ("CustomNotebook.padding", {
                        "side": "top",
                        "sticky": "nswe",
                        "children": [
                            ("CustomNotebook.focus", {
                                "side": "top",
                                "sticky": "nswe",
                                "children": [
                                    ("CustomNotebook.label", {"side": "left", "sticky": ''}),
                                    ("CustomNotebook.close", {"side": "left", "sticky": ''}),
                                ]
                            })
                        ]
                    })
                ]
            })
        ])
        return style
    def getStyle(self):
        return Notebook._STYLE
    def onCloseEvent(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False, getIdInsteadOfName=True):
        runnable = _EventHandler._getNewEventRunnable(self, func, args, priority, decryptValueFunc=self._decryptValueID if getIdInsteadOfName else self._decryptValueNAME, defaultArgs=defaultArgs, disableArgs=disableArgs)
        self["runnable"] = runnable
    def _decryptValueID(self, e):
        return self._active
    def _decryptValueNAME(self, e):
        return self._name
    def _on_close_press(self, event):
        """Called when the button is pressed over the close button"""
        element = self["widget"].identify(event.x, event.y)
        if "close" in element:
            index = self["widget"].index("@%d,%d" % (event.x, event.y))
            self["widget"].state(['pressed'])
            self._active = index
            return "break"
    def _deleteIndex(self, index):
        tab = self["tabIndexList"][index]
        shift = False
        for i, itab in enumerate(self["tabIndexList"]):
            if itab == tab:
                shift = True
            if shift: itab["tabId"] = i-1
        self["tabIndexList"].pop(index)
    def _on_close_release(self, event):
        def _call(runnable):
            runnable()
            return runnable.event

        """Called when the button is released"""
        if not self["widget"].instate(['pressed']):
            return
        element = self["widget"].identify(event.x, event.y)
        if "close" not in element:
            # user moved the mouse off of the close button
            return
        index = self["widget"].index("@%d,%d" % (event.x, event.y))
        self._name = self["widget"].tab(index, "text")
        _event = _call(self["runnable"])
        if not len(_event._data): return
        if self._active == index and (self["runnable"] is None or (self["runnable"] is not None and not _event["setCanceled"])):
            if self["destroyed"]: return
            self["widget"].forget(index)
            self._deleteIndex(index)
            self["widget"].event_generate("<<NotebookTabClosed>>")
        if self["destroyed"]: return
        self["widget"].state(["!pressed"])
        self._active = None
        self._updateTab(self.getSelectedTabIndex())
    def _updateTab(self, e):
        if len(self["tabIndexList"]) == 0: return
        """
        
        
        @param e: event or int -> tab index
        @return: 
        """
        for widget in _getAllChildWidgets(self["tabIndexList"][e.getValue() if hasattr(e, "getValue") else e]):
            if widget["id"] in list(self["tkMaster"]["dynamicWidgets"].keys()):
                self["tkMaster"]._updateDynamicSize(widget)
    def __destroy(self):
        """
        Don't need.
        tab deletion is handeld by child widget of Notebook


        @return:
        """
        print("DESTROY TABS")
        super().destroy()
        for tab in self["tabIndexList"]:  # destroy all tabs
            tab.destroy()

