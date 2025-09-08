from random import randint as _randint, choice as _choice
from typing import Union, Callable, Tuple, List
import tkinter as _tk
import tkinter.ttk as _ttk
from tkinter.font import Font as _tk_Font
from string import ascii_lowercase
from traceback import format_exc

from .util import _lockable, Font, _isinstanceAny, WidgetGroup, _TaskScheduler, _IntVar, remEnum, ifIsNone
from .event import _EventHandler, _EventRegistry, Event
from .const import *
from .const import _ALLOWED_MENU_PROPERTIES
from .tkmath import Location2D, Rect
from .image import PILImage, TkImage
from .window import Toplevel, Tk

class _Widget:
    """
    Baseclass for all Widgets.
    """
    def __init__(self, child, widget, master, group, init:dict=None, _instanceOfMenu=False):
        self._child = self if child is None else child
        self._widget = widget
        self._tkMaster = master if isinstance(master, Tk) else master._tkMaster
        self._master = master
        self._group = group
        self._widgetProperties = {}
        self._instanceOfMenu = _instanceOfMenu #TODO need?
        self._toolTip = None
        self._xScrollbar = None
        self._yScrollbar = None
        self._placed = False
        self._destroyed = False
        self._relativePlaceData = {
            "handler":None
        }

        if hasattr(self._master, "_childWidgets"):
            self._master._childWidgets.append(self)

        self._eventRegistry = _EventRegistry(self)
        self._applyData(init)
        self._registerChild()
        if group is not None: self._group.add(self._child)
    def __repr__(self):
        return f"{self.__class__.__name__}({self._placed})"
    def __del__(self): #TODO add __del__
        if self._group is not None:
            self._group.remove(self._child)
    # Attribute Setter Methods
    @_lockable
    def setBg(self, col:Union[Color, str]):
        """
        Set the background color of this widget.

        @param col: Use Color _Enum, tkinter string or hex-code.
        @return:
        """
        self._setAttribute("bg", remEnum(col))
        return self
    def setFg(self, col:Union[Color, str]):
        """
        Set the text color of this widget.

        @param col: Use Color _Enum, tkinter string or hex-code.
        @return:
        """
        self._setAttribute("fg", remEnum(col))
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
            _data = {'family': remEnum(art),
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
        self._setAttribute("anchor", remEnum(ori))
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
        self._setAttribute("orient", remEnum(ori))
        return self
    def setStyle(self, style:Style):
        """
        Set widget style.
        Use Style _Enum to choose between styles.

        @param style:
        @return:
        """
        self._setAttribute("relief", remEnum(style))
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
        self._setAttribute("compound", remEnum(dir_))
        return self
    def setCursor(self, c:Cursor):
        """
        Set cursor image from Cursor _Enum or default tkinter string.
        This only applies while hovering over this widget.

        @note only predefined cursors are implemented yet
        @param c:
        @return:
        """
        self._setAttribute("cursor", remEnum(c))
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
        return self._widget["text"]
    def getHeight(self):
        """
        Returns the Widget Height.
        May be only possible after using any place manager.

        @return:
        """
        self.updateIdleTasks()
        return self._widget.winfo_height()
    def getWidth(self):
        """
        Returns the Widget Width.
        May be only possible after using any place manager.

        @return:
        """
        self.updateIdleTasks()
        return self._widget.winfo_width()
    def getPositionRelativeToScreen(self)->Location2D:
        """
        Returns the location of this widget relative to the screen.
        """
        return Location2D(
            self._widget.winfo_rootx(),
            self._widget.winfo_rooty()
        )
    def setFocus(self):
        """
        Sets the focus to this Window.

        @return:
        """
        self._widget.focus_set()
        return self
    def getPosition(self)->Location2D:
        """
        Returns the widget position.
        May be only possible after using any place manager.

        @return:
        """
        return Location2D(self._widget.winfo_x(), self._widget.winfo_y())
    def getPositionToMaster(self)->Location2D:
        """
        Returns the widget position relative to master window.
        May be only possible after using any place manager.

        @return:
        """
        return Location2D(self._widget.winfo_vrootx(), self._widget.winfo_vrooty())
    def getParentWindow(self)->Tk:
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
        return self._widget.focus_get() == self._get()
    def attachToolTip(self, text:str, atext:str="", group:WidgetGroup =None, waitBeforeShow=.5):
        """
        Attaches a tooltip that opens on hover over this Widget longer than 'waitBeforeShow' seconds.


        @param text: Text that will be shown in ToolTip
        @param atext: AdditionalText will be shown when shift key is pressed.
        @param group: Optional WidgetGroup instance for preset font, color etc.
        @param waitBeforeShow: Time the user have to hover over this widget to show the TooTip
        @return: ToolTip instance for further configuration
        """
        if self._toolTip is not None: self._toolTip.destroy()
        self._toolTip = _ToolTip(self, atext != "", waitBeforeShow=waitBeforeShow, group=group).setText(text).setAdditionalText(atext)
        return self._toolTip
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
        self._widget.update()
        return self
    def updateIdleTasks(self):
        """
        Updates only the tkinter idle tasks.

        @return:
        """
        self._widget.update_idletasks()
        return self
    def updateRelativePlace(self):
        """
        Updates the relative place of this widget.
        Only updates if the widget ist placed relative.

        @return:
        """
        self._tkMaster.updateDynamicWidgets(self)
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
        event = remEnum(event)
        if event.startswith("["):
            _EventHandler._registerNewCustomEvent(self, func, event, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs)
        else:
            _EventHandler._registerNewEvent(self._child, func, event, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs)
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
        event = remEnum(event)
        if event.startswith("["):
            raise NotImplemented("Trigger custom Events is not implemented yet!")
        self._widget.event_generate(event)
    # Place Manager Methods
    def grid(self, row=0, column=0):
        """
        Default tkinter grid-manager.

        @param row:
        @param column:
        @return:
        """
        assert not self._destroyed, "The widget has been destroyed and can no longer be placed."
        self._placed = True
        self._widget.grid(row=row, column=column)
        return self
    def placeRelative(self, fixX:int=None, fixY:int=None, fixWidth:int=None, fixHeight:int=None, xOffset=0, yOffset=0, xOffsetLeft=0, xOffsetRight=0, yOffsetUp=0, yOffsetDown=0, stickRight=False, stickDown=False, centerY=False, centerX=False, center=False, changeX=0, changeY=0, changeWidth=0, changeHeight=0):
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
        @param center: Centers the widget on X-Axis and Y-Axis.
        @param centerY: Centers the widget on Y-Axis.
        @param centerX: Centers the widget on X-Axis.
        @param changeX: Changes x coordinate after all calculations are done.
        @param changeY: Changes y coodinate after all calculations are done.
        @param changeWidth: Changes width coodinate after all calculations are done.
        @param changeHeight: Changes height coodinate after all calculations are done.
        @param nextTo: NOT IMPLEMENTED YET
        @return:
        """
        assert 100 >= xOffset + xOffsetLeft >= 0 and 100 >= xOffset + xOffsetRight >= 0, "xOffset must be a int Value between 0 and 100!"
        assert 100 >= yOffset + yOffsetUp >= 0 and 100 >= yOffset + yOffsetDown >= 0, "yOffset must be a int Value between 0 and 100!"
        self._placed = True
        self._relativePlaceData = {"handler": self._relativePlaceData["handler"],
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
                                      "center":center,
                                      "changeX": changeX,
                                      "changeY": changeY,
                                      "changeWidth": changeWidth,
                                      "changeHeight": changeHeight}
        self._tkMaster._updateDynamicSize(self)
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
        assert not self._destroyed, "The widget has been destroyed and can no longer be placed."
        if x is None: x = 0
        if y is None: y = 0
        if isinstance(x, Location2D):
            x, y = x.get()
        if isinstance(x, Rect):
            height = x.getHeight()
            width = x.getWidth()
            x, y = x.getLoc1().get()
        x = int(round(x, 0))
        y = int(round(y, 0))
        #self._get().place_forget()
        self._widget.place(x=x, y=y, width=width, height=height, anchor=remEnum(anchor))
        self._placed = True
        return self
    def placeForget(self):
        """
        Removes this widget from its master.
        Can be placed again after.

        @return:
        """
        self._placed = False
        try:
            self._widget.place_forget()
        except Exception as e:
            print(format_exc())
    def destroy(self):
        """
        Destroys this widget.
        The Widget instance cannot be used after destroying it!

        Can be overwritten!
        @return:
        """
        assert not self._destroyed, f"Widget {type(self)} id={self._getID()} is already destroyed!"
        self._eventRegistry.unregisterAll() #TODO need?
        WidgetGroup.removeFromAll(self)
        if self._toolTip is not None:
            self._toolTip.destroy()
        if hasattr(self._master, "_childWidgets"):
            self._master._childWidgets.remove(self)
        if self._get() is not None:
            self._get().destroy()
        self._destroyed = True
        self._placed = False
        return self
    def lift(self, widg=None):
        """
        Lifts this widget in front of all other or in front of given Widget.

        @param widg:
        @return:
        """
        if widg is not None:
            self._widget.lift(widg._get())
        else:
            self._widget.lift()
    # Intern Methods
    def _applyTkOption(self, **kwargs):
        """
        Apply one or more tkinter attributes to this widget.

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
        return self._tkMaster
    def _getID(self)-> int:
        """
        Returns this widget id.

        @return:
        """
        return hash(self)
    def _decryptEvent(self, args, event):
        pass
    def _setAttribute(self, name, value):
        if self._destroyed: return
        self._widgetProperties[name] = value
        if self._widget is None: return # only capture _widgetProperties for menu
        try:
            self._widget[name] = value
        except Exception as e:
            value = repr(value)
            valType = type(value)
            value = value[0:50]+"..." if len(str(value)) > 50 else value
            raise AttributeError("Could not set Attribute of Widget "+str(type(self._child))+"!\n\tKEY: '"+str(name)+"'\n\tVALUE["+str(valType)+"]: '"+str(value)+"'\n"+str(self._child)+" \n\tTKError: "+str(e))
    def _applyData(self, d:dict | None):
        if d is None: return
        for key, value in zip(d.keys(), d.values()):
            if key == "func":
                value()
            else:
                self._setAttribute(name=key, value=value)
    def _registerChild(self):
        if self._child == self: return
        self._master._childWidgets.append(self._child)
    def _get(self):
        return self._widget
class _ContainerWidget(_Widget):
    def __init__(self, child, widget, master, group, init:dict=None, _instanceOfMenu=False):
        self._childWidgets = []
        
        super().__init__(child=child,
                         widget=widget,
                         master=master,
                         group=group,
                         init=init,
                         _instanceOfMenu=_instanceOfMenu)
    def destroy(self):
        for w in self._childWidgets:
            w.destroy()
        super().destroy() # destroy self

    def __repr__(self):
        return str(self.__class__.__name__)+"("+str(self._childWidgets)+")"
class _LockableWidget(_Widget):
    """
    Private implementation of tkinter's [state="disabled"].
    """
    def __init__(self, child, widget, master, group):
        #if not hasattr(self, "_isReadOnly"):
        #    self._isReadOnly = False
        self._lockVal = 0
        self._isDisabled = False
        self._forceDisabled = False

        super().__init__(child=child,
                         widget=widget,
                         master=master,
                         group=group)

        # setReadOnly
        if self._isReadOnly:
            super()._setAttribute("state", self._lockState) #ifIsNone(lockState, "disabled")
            self._isDisabled = True
            return
        self.setEnabled()
    def _setReadOnly(self, b:bool, lockState=None):
        self._isReadOnly = b
        self._lockState = ifIsNone(lockState, "disabled")
        self._unlockState = "normal"

    def _unlock(self):
        self._lockVal += 1
        if self._lockVal > 1: return
        # enter UnLocking
        if not self._isDisabled: return
        super()._setAttribute("state", "normal")
    def _lock(self):
        self._lockVal -= 1
        if self._lockVal != 0: return
        # leave Unlocking
        if self._isReadOnly or self._isDisabled:
            super()._setAttribute("state", self._lockState if not self._forceDisabled else "disabled")

    def setEnabled(self):
        if not self._isDisabled: return
        super()._setAttribute("state", self._unlockState if self._lockState == "disabled" else self._lockState) # "normal" if _lockstate is None else "readonly"
        #print(self._unlockState)
        self._forceDisabled = False
        self._isDisabled = False
    def setDisabled(self):
        if self._isDisabled: return
        super()._setAttribute("state", "disabled")
        self._forceDisabled = True
        self._isDisabled = True

class _ToolTip(_Widget):
    """
    Create a tooltip for a given widget.
    It shows up on hover over widget.
    """
    def __init__(self, _master, pressShiftForMoreInfo=False, waitBeforeShow=.5, group:WidgetGroup =None):
        if not _isinstanceAny(_master, Tk, _Widget):
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + ", Frame or Tk instance not: " + str(_master.__class__.__name__))

        self._disableTip = False
        self._text = ""
        self._atext = ""
        self._wait = waitBeforeShow
        self._wrapLength = 180
        self._task = None
        self._tipToplevel = None
        self._tipLabel = None

        super().__init__(child=self,
                         widget=None,
                         master=_master,
                         group=group)
        
        self._master.bind(self._enter, "<Enter>")
        self._master.bind(self._leave, "<Leave>")
        self._master.bind(self._leave, "<ButtonPress>")
        if pressShiftForMoreInfo: 
            self._tkMaster.bind(self._more, "<KeyRelease-Shift_L>", args=["release"])
            self._tkMaster.bind(self._more, "<KeyPress-Shift_L>", args=["press"])
    def destroy(self):
        super().destroy()

    def setDisabled(self):
        self._disableTip = True
        return self
    def setEnabled(self):
        self._disableTip = False
        return self
    def setText(self, text):
        self._text = text
        return self
    def setAdditionalText(self, text):
        self._atext = text
        return self
    def _more(self, e):
        mode = e.getArgs(0)
        if self._tipToplevel:
            text = self._text if mode == "release" else self._atext
            self._tipLabel.destroy()
            self._tipLabel = Label(self._tipToplevel)._applyTkOption(text=text, justify='left', background="#ffffff", relief='solid', borderwidth=1, wraplength=self._wrapLength)
            self._tipLabel._get().pack(ipadx=1)
    def _enter(self, e):
        self._schedule()
    def _leave(self, e):
        self._unschedule()
        self._hidetip()
    def _schedule(self):
        self._unschedule()
        self._task = _TaskScheduler(self._master, self._wait, self._show).start()
    def _unschedule(self):
        task = self._task
        self._task = None
        if task: task.cancel()
    def _show(self):
        if self._disableTip:
            return
        mx, my = self._tkMaster.getMousePositionRelativeToScreen().get()
        self._hidetip()
        self._tipToplevel = Toplevel(self._tkMaster, group=self._group)
        self._tipToplevel.overrideredirect()
        self._tipToplevel.setPositionOnScreen(mx, my+15)
        self._tipLabel = Label(self._tipToplevel, group=self._group)._applyTkOption(
            text=self._text,
            justify='left',
            relief='solid',
            borderwidth=1,
            wraplength=self._wrapLength
        )
        self._tipLabel._get().pack(ipadx=1)
    def _hidetip(self):
        pin = self._tipToplevel
        self._tipToplevel = None
        if pin is not None:
            pin.destroy()
class ScrollBar(_Widget):
    """
    Scrollbar Widget can be attached to some Widget using their 'attachScrollbar' method.
    """
    def __init__(self, _master, autoPlace=True, group:WidgetGroup =None):
        if not _isinstanceAny(_master, Tk, NotebookTab, "Canvas", Frame, LabelFrame):
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+" or Tk instance not: "+str(_master.__class__.__name__))

        self._autoPlace = autoPlace
        self._thickness = 18

        super().__init__(child=self,
                         widget=_ttk.Scrollbar(_master._get()),
                         master=_master,
                         group=group)
        if self._autoPlace: self._placed = True
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
        #self._widget["width"] = w
        #self["thickness"] = w-10
        #return self
    def set(self, a, b):
        self._get().set(a, b)
    def _decryptEvent(self, args, event):
        return None
class Frame(_ContainerWidget):
    """
    Widget:
    The Frame is used to group or organize widgets.
    Frames can be places and configured as usualy.
    Once the frame is places it can be used as Master to place other widgets on and relative to the frame.
    """
    def __init__(self, _master, group:WidgetGroup =None):
        if not _isinstanceAny(_master, Tk, NotebookTab, "Canvas", Frame, LabelFrame):
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+" or Tk instance not: "+str(_master.__class__.__name__))

        super().__init__(child=self,
                         widget=_tk.Frame(_master._get()),
                         master=_master,
                         group=group)
class LabelFrame(_ContainerWidget):
    """
    Widget:
    Similar the Frame widget.
    The LabelFrame has an outline.
    A name can be set using the 'setText' methods.
    """
    def __init__(self, _master, group:WidgetGroup =None):
        if not _isinstanceAny(_master, Tk, NotebookTab, "Canvas", Frame, LabelFrame):
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + " or Tk instance not: " + str(_master.__class__.__name__))

        super().__init__(child=self,
                         widget=_tk.LabelFrame(_master._get()),
                         master=_master,
                         group=group)
class Label(_Widget):
    """
    Widget:
    The Label widget is used to display one line text or images.
    """
    def __init__(self, _master, group:WidgetGroup =None):
        if not _isinstanceAny(_master, Tk, NotebookTab, "Canvas", Frame, LabelFrame):
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+" or Tk instance not: "+str(_master.__class__.__name__))

        super().__init__(child=self,
                         widget=_tk.Label(_master._get()),
                         master=_master,
                         group=group)
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
        self._widget._image = img._get()
        self._setAttribute("image", self._widget._image)
        return self
    def clearImage(self):
        """
        Clears the displayed image.
        @return:
        """
        self._setAttribute("image", "")
        return self
class Checkbutton(_Widget):
    """
    Widget:
    The Checkbutton a Label with a checkbox on the left.
    """
    def __init__(self, _master, group:WidgetGroup =None):
        if not _isinstanceAny(_master, Tk, NotebookTab, "Canvas", Frame, LabelFrame, _SubMenu):
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+" or Tk instance not: "+str(_master.__class__.__name__))
        self._instanceOfMenu = False
        init = None
        self._text = ""
        self._intVar = None
        if isinstance(_master, _SubMenu):
            _master = _master._add("checkbutton", self)
            group = None
        else:
            self._intVar = _tk.IntVar(_master._get())
            init = {"variable":self._intVar}
        super().__init__(child=self,
                         widget=_tk.Checkbutton(_master._get()) if not self._instanceOfMenu else None,
                         master=_master,
                         group=group,
                         init=init,
                         _instanceOfMenu=self._instanceOfMenu)
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
        _EventHandler._registerNewCommand(self,
                                          func,
                                          args,
                                          priority,
                                          decryptValueFunc=self._decryptEvent,
                                          defaultArgs=defaultArgs,
                                          disableArgs=disableArgs)
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
        self._intVar.set(bool(b))
        return self
    def getState(self)->bool:
        """
        Returns the current selection state as boolean.
        @return:
        """
        return bool(self._intVar.get())
    def setSelectColor(self, c:Union[Color, str]):
        """
        Set the backgroundcolor of the checkbox.
        @param c:
        @return:
        """
        self._setAttribute("selectcolor", remEnum(c))
        return self
class CheckbuttonTTK(_Widget):
    def __init__(self, _master, group:WidgetGroup =None):
        self._intVar = _tk.IntVar(_master._get())
        super().__init__(child=self,
                         widget=_ttk.Checkbutton(_master._get()),
                         master=_master,
                         group=group,
                         init={"variable": self._intVar})
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
        self._intVar.set(bool(b))
        return self
    def getState(self)->bool:
        """
        Returns the current selection state as boolean.
        @return:
        """
        return bool(self._intVar.get())
    def setSelectColor(self, c:Union[Color, str]):
        """
        Set the backgroundcolor of the checkbox.
        @param c:
        @return:
        """
        self._setAttribute("selectcolor", remEnum(c))
        return self
class Radiobutton:
    """
    Widget:
    This is NOT the widget class.
    This class is only used to bind events or get the current selected radiobutton.
    Use the method 'createNewRadioButton' to create the radiobuttons.
    These can be placed and used as normal widgets.
    """
    def __init__(self, _master, group:WidgetGroup =None):
        if not _isinstanceAny(_master, Tk, NotebookTab, "Canvas", Frame, LabelFrame):
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+" or Tk instance not: "+str(_master.__class__.__name__))
        self._intVar = _IntVar(_master)
        self._master = _master
        self._radioButtonInstances = []
        self._eventArgs = []
        self._group = group
    def getState(self)->int:
        """
        Returns the index of selected radiobutton.
        @return:
        """
        return self._intVar.get()
    def setState(self, i:int):
        """
        Set radiobutton on index 'i' selected.
        @param i:
        @return:
        """
        self._radioButtonInstances[i].setSelected()
        return self
    def createNewRadioButton(self, group:WidgetGroup =None):
        """
        This method creates a new Radiobutton and returns it.
        The order that the Radiobuttons are added are the related indices wich are used for events.
        The returned widget can be placed and used as normal widget.
        The passed WidgetGroup is applied to this Radiobutton.
        @param group:
        @return:
        """
        rb =_RadioButton(self._master, self._intVar, (self._group if group is None else group))
        self._radioButtonInstances.append(rb)
        for i in self._eventArgs:
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
        self._eventArgs.append({"func":func, "args":args , "priority":priority, "defaultArgs":defaultArgs, "disableArgs":disableArgs})
        for btn in self._radioButtonInstances:
            _EventHandler._registerNewCommand(btn, func, args, priority, decryptValueFunc=btn._decryptEvent, defaultArgs=defaultArgs, disableArgs=disableArgs)
        return self
class _RadioButton(_Widget):
    """
    Subclass for Radiobuttons.
    Represents a single Radiobutton widget.
    """
    def __init__(self, _master, intVar, group):
        self._intVar = intVar
        super().__init__(child=self,
                         widget=_tk.Radiobutton(_master._get()),
                         master=_master,
                         group=group,
                         init={"variable": intVar._get(), "value": intVar._add()})
    def setSelected(self):
        """
        Set the Radiobutton selected.
        @return:
        """
        self._intVar.set(self._widget["value"])
        return self
    def getValue(self)->int:
        """
        Returns the Selected Index.
        @return:
        """
        return self._intVar.get()
    def setSelectColor(self, c:Union[Color, str]):
        """
        Set the backgroundcolor of the radiobutton.
        @param c:
        @return:
        """
        self._setAttribute("selectcolor", remEnum(c))
        return self
    def flash(self):
        """
        This method changes serveral times between selected color and background color.
        This can be used to indicate that the user has to click on this widget.

        @return:
        """
        self._widget.flash()
        return self
    def _decryptEvent(self, args, event):
        return self.getText()
class Button(_Widget):
    """
    Widget:
    The Button widget is clickable.
    The onclick event can be bound via the 'setCommand' method.
    """
    def __init__(self, _master, group:WidgetGroup =None, canBePressedByReturn=True, fireOnlyOnce=True, fireInterval:float=0.1, firstDelay:float=0.5):
        if not _isinstanceAny(_master, Tk, NotebookTab, "Canvas", Frame, LabelFrame, _SubMenu, ContextMenu):
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+" or Tk instance not: "+str(_master.__class__.__name__))

        self._canBePressedByReturn = canBePressedByReturn
        self._instanceOfMenu = False

        init = None
        if isinstance(_master, _SubMenu) or isinstance(_master, ContextMenu):
            _master = _master._add("command", self)
            group = None

        else:
            if not fireOnlyOnce:
                init = {
                    "repeatdelay": int(firstDelay * 1000),
                    "repeatinterval": int(fireInterval * 1000)
                }

        super().__init__(child=self,
                         widget=_tk.Button(_master._get()) if not self._instanceOfMenu else None,
                         master=_master,
                         group=group,
                         init=init,
                         _instanceOfMenu=self._instanceOfMenu)
    def triggerButtonPress(self, changeRelief=True):
        """
        This method can be used to trigger the Button and its command.
        @param normalRelief: if True the pressanimation is shown otherwise only the bound function is triggered.
        @return:
        """
        if changeRelief:
            self.setStyle(Style.SUNKEN)
        self.update()
        trigger = self._eventRegistry.getHandler("cmd")
        if trigger is not None:
            trigger()
        if changeRelief:
            self.setStyle(Style.RAISED)
        self.update()
    def setActiveBg(self, col:Color):
        """
        Set the active background color.
        Visible if button is pressed.

        @param col: Use Color _Enum, tkinter string or hex-code.
        @return:
        """
        self._setAttribute("activebackground", remEnum(col))
        return self
    def setActiveFg(self, col:Color):
        """
        Set the active foreground color.
        Visible if button is pressed.

        @param col: Use Color _Enum, tkinter string or hex-code.
        @return:
        """
        self._setAttribute("activeforeground", remEnum(col))
        return self
    def setStyleOnHover(self, style:Style):
        """
        Changes the Style on hover.
        Use the Style _Enum to change.
        @param style:
        @return:
        """
        self._setAttribute("overrelief", remEnum(style))
        return self
    def flash(self):
        """
        This method changes serveral times between selected color and background color.
        This can be used to indicate that the user has to click on this widget.

        @return:
        """
        self._widget.flash()
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
        runnable = _EventHandler._registerNewCommand(self, cmd, args, priority, disableArgs=disableArgs, defaultArgs=defaultArgs, onlyGetRunnable=self._instanceOfMenu)
        if self._instanceOfMenu:
            self._widgetProperties["command"] = runnable
        elif self._canBePressedByReturn:
            _EventHandler._registerNewEvent(self, cmd, Key.RETURN, args, priority=1, disableArgs=disableArgs, defaultArgs=defaultArgs)
        return self
    def setImage(self, img:Union[TkImage, PILImage]):
        """
        Set the image displayed on the Label.
        Use either an 'TkImage' or an 'PILImage' instance.
        @param img:
        @return:
        """
        self._widget._image = img._get()
        self._setAttribute("image", self._widget._image)
        return self
class Entry(_LockableWidget):
    """
    Widget:
    The Entry is used to ask single line text from the user.
    """
    def __init__(self, _master, group:WidgetGroup=None, readOnly=False):
        if not _isinstanceAny(_master, Tk, NotebookTab, "Canvas", Frame, LabelFrame):
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+" or Tk instance not: "+str(_master.__class__.__name__))

        self._xScrollbar = None

        self._setReadOnly(readOnly)
        super().__init__(child=self,
                         widget=_tk.Entry(_master._get()),
                         master=_master,
                         group=group)
    def attachHorizontalScrollBar(self, sc:ScrollBar):
        """
        Used to attach a horizontal scrollbar to the Entry.
        Pass a Scrollbar instance to this method.
        @param sc:
        @return:
        """
        self._xScrollbar = sc
        sc._setAttribute("orient", _tk.HORIZONTAL)
        sc._setAttribute("command", self._scrollHandler)
        self._setAttribute("xscrollcommand", sc._get().set)
        return self
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
        self._setAttribute("insertbackground", remEnum(c))
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
        self._setAttribute("selectforeground", remEnum(c))
        return self
    def setSelectBackGroundColor(self, c:Union[Color, str]):
        """
        Set select background color.
        @param c:
        @return:
        """
        self._setAttribute("selectbackground", remEnum(c))
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
        self._widget.delete(0, _tk.END)
        return self
    @_lockable
    def setValue(self, text:str):
        """
        Overwrites the text content in the Entry.
        @param text:
        @return:
        """
        self.clear()
        self._widget.insert(0, str(text))
        return self
    @_lockable
    def addText(self, text:str, index="end"):
        """
        Adds the text at 'index', by default at the end.
        @param text:
        @param index:
        @return:
        """
        self._widget.insert(index, str(text))
        return self
    def getValue(self)->str:
        """
        Returns the text content from the Entry.
        @return:
        """
        return self._widget.get()
    def _decryptEvent(self, args, event):
        return args
    def _scrollHandler(self, *l):
        op, howMany = l[0], l[1]
        if op == 'scroll':
            units = l[2]
            self._widget.xview_scroll(howMany, units)
        elif op == 'moveto':
            self._widget.xview_moveto(howMany)
class Listbox(_Widget):
    """
    Widget:
    The user can select one (Default) or multiple items.
    A Scrollbar can also be added.

    """
    def __init__(self, _master, group:WidgetGroup =None):
        if not _isinstanceAny(_master, Tk, NotebookTab, "Canvas", Frame, LabelFrame):
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+" or Tk instance not: "+str(_master.__class__.__name__))

        self._selectionMode = "single"
        self._defaultColor = Color.DEFAULT.value
        self._yScrollbar = None

        super().__init__(child=self,
                         widget=_tk.Listbox(_master._get()),
                         master=_master,
                         group=group,
                         init={"selectmode":"single"})
    def bindArrowKeys(self, widget=None, ifNoSelectionSelect0=True):
        """
        The arrowkeys get bound to navigate up and down via the arrowkeys.
        @param widget: bind to given widget (Default = self)
        @param ifNoSelectionSelect0: Select on arrowkeys index zero if none is selected
        @return:
        """
        def _up(e):
            if self._placed:
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
                self._widget.event_generate("<<ListboxSelect>>")
        def _down(e):
            if self._placed:
                selected = self.getSelectedIndex()
                if selected is None:
                    selected = 0
                    if ifNoSelectionSelect0: self.setItemSelectedByIndex(0)
                else:
                    if selected < self.length():
                        selected += 1
                        self.setItemSelectedByIndex(selected)

                self.see(selected)
                self._widget.event_generate("<<ListboxSelect>>")
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
        self._widget.see(index)
        return self
    def setSelectForeGroundColor(self, c:Union[Color, str]):
        """
        Foregroundcolor applied if item is selected.
        @param c:
        @return:
        """
        self._setAttribute("selectforeground", remEnum(c))
    def setSelectBackGroundColor(self, c:Union[Color, str]):
        """
        Backgroundcolor applied if item is selected.
        @param c:
        @return:
        """
        self._setAttribute("selectbackground", remEnum(c))
    def attachVerticalScrollBar(self, sc:ScrollBar):
        """
        Used to attach a vertical scrollbar to the Entry.
        Pass a Scrollbar instance to this method.
        @param sc:
        @return:
        """
        self._yScrollbar = sc
        sc._setAttribute("orient", _tk.VERTICAL)
        sc._setAttribute("command", self._widget.yview)
        self._setAttribute("yscrollcommand", sc._get().set)
        return self
    def clearSelection(self):
        """
        Clears the selection.
        @return:
        """
        self._widget.selection_clear(0, "end")
    def setMultipleSelect(self):
        """
        Set the Listbox in 'multiselectmode'.
        The User can select more than one item.
        @return:
        """
        self._setAttribute("selectmode", "multiple")
        self._selectionMode = "multiple"
        return self
    def setSingleSelect(self):
        """
        Set the Listbox in 'singleselectmode'.
        The User can select only one item.
        This is the DEFAULT mode.
        @return:
        """
        self._setAttribute("selectmode", "single")
        self._selectionMode = "single"
        return self
    def setSlotBgDefault(self, color:Union[Color, str]=Color.DEFAULT):
        self._defaultColor = remEnum(color)
    def add(self, entry:str, index="end", color:Union[Color, str]=None):
        """
        Adds an entry to the Listbox.
        For large amount of items the 'addAll' method is way faster!
        @param entry: entry content as string
        @param index: where to insert. At the end by default.
        @param color: Background color of this item.
        @return:
        """
        color = ifIsNone(remEnum(color), self._defaultColor)
        self._widget.insert(index, str(entry))
        index = (self.length()-1 if index=="end" else index)
        if self.length() > 0:
            self.setSlotBg(index, color)
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
        length = self.length()
        color = ifIsNone(remEnum(color), self._defaultColor)
        self._widget.insert(index, *entry)
        if color != Color.DEFAULT and False:
            for i in range(length-1, self.length()-1): # TODO TEST
                self.setSlotBg(i, color)
            self.updateIdleTasks()
        return self
    def length(self)->int:
        """
        Returns the amount of items in Listbox.
        @return:
        """
        return self._widget.size()
    def clear(self):
        """
        Removes all items from Listbox.
        @return:
        """
        self._widget.delete(0, _tk.END)
        return self
    def setSlotBgAll(self, color:Union[Color, str]=None):
        """
        Set the Backgroundcolor of all slots.
        This can be slow.
        Better is to set the color while adding.
        @param color:
        @return:
        """
        color = ifIsNone(remEnum(color), self._defaultColor)
        for i in self.getAllSlotIndexes():
            self.setSlotBg(i, color)
        return self
    def setSlotBg(self, index:int, color:Union[Color, str] = None):
        """
        Set backgroundcolor of item a given index.
        @param index:
        @param col:
        @return:
        """
        color = ifIsNone(remEnum(color), self._defaultColor)
        self._widget.itemconfig(index, bg=color)
        return self
    def setItemSelectedByIndex(self, index:int, clearFirst=True):
        """
        Set an item selected by given index.
        @param index:
        @param clearFirst: clears the old selection before setting the new.
        @return:
        """
        if clearFirst: self._widget.selection_clear(0, "end")
        self._widget.select_set(index)
        return self
    def setItemSelectedByName(self, name:str, clearFirst=True):
        """
        Set the first item with given name selected.
        @param name:
        @param clearFirst: clears the old selection before setting the new.
        @return:
        """
        if clearFirst: self._widget.selection_clear(0, "end")
        if name in self.getAllSlots():
            self.setItemSelectedByIndex(self.getAllSlots().index(name))
        return self
    def deleteItemByIndex(self, index:int):
        """
        Deletes an item by given index
        @param index:
        @return:
        """
        self._widget.delete(index)
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
        if len(self._widget.curselection()) == 0: return None
        if self._selectionMode == "single":
            return int(self._widget.curselection()[0])
        else:
            return [int(i) for i in self._widget.curselection()]
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
        return [self._widget.get(i) for i in range(self.length())]
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
            if self._selectionMode == "single":
                return w.get(int(w.curselection()[0]))
            else:
                return [w.get(int(i)) for i in w.curselection()]
        except Exception as e:
            return "CANCEL"
class Scale(_Widget):
    """
    Widget:
    Adds a Slider to set values from specified value range.
    """
    def __init__(self, _master, group:WidgetGroup = None, from_=0, to=100, orient:Orient=Orient.HORIZONTAL):
        if not _isinstanceAny(_master, Tk, NotebookTab, "Canvas", Frame, LabelFrame):
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+" or Tk instance not: "+str(_master.__class__.__name__))
        
        self._doubleVar = _tk.DoubleVar(_master._get())
        
        super().__init__(child=self,
                         widget=_tk.Scale(_master._get()),
                         master=_master,
                         group=group,
                         init={"variable": self._doubleVar, 
                               "from_": from_, 
                               "to":to, 
                               "orient":remEnum(orient)
                               })

    def getValue(self)->float:
        """
        Returns the selected value.
        @return:
        """
        return self._doubleVar.get()
    def setValue(self, v:float):
        """
        Set scale value.
        @param v:
        @return:
        """
        self._doubleVar.set(v)
        return self
    def getSlideLocation(self, value=None)->Location2D:
        """
        Returns the slider location on screen.
        @param value: if None current scale value is taken
        @return:
        """
        if value is None: value = self.getValue()
        return Location2D(self._widget.coords(value))
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
        self._setAttribute("troughcolor", remEnum(color))
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
        self._setAttribute("sliderrelief", remEnum(style))
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
    def _decryptValue(self, args, event):
        return self.getValue()
class Progressbar(_Widget):
    """
    Widget:
    Creates a Processbar to indicate process.
    """
    def __init__(self, _master, group:WidgetGroup =None, values:int=100):
        if not _isinstanceAny(_master, Tk, NotebookTab, "Canvas", Frame, LabelFrame):
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+" or Tk instance not: "+str(_master.__class__.__name__))
        
        self._values = values
        self._value = 0
        
        super().__init__(child=self,
                         widget=_ttk.Progressbar(_master._get()),
                         master=_master,
                         group=group)
    def setNormalMode(self):
        """
        Set the Processbar to normal mode.
        It can fill from 0 to 100%.
        @return:
        """
        self._widget.stop()
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
        self._widget.start(int(delay*1000))
        return self
    def iter(self, reset=True):
        """
        A for loop can be used to 'iter' through the processbar.
        The for loop index are the steps from the Processbar.
        @param reset: if the Processbar should be set to zero before.
        @return:
        """
        if reset:
            v = self._values
            self.reset()
        else:
            v = self._values - self._value
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
        self._setAttribute("orient", remEnum(o))
        return self
    def setValues(self, val:int):
        """
        Set the max Value.
        Value range 0 to 'val'
        @param val:
        @return:
        """
        self._values = int(val)
    def update(self):
        """
        Updates the Processbar.
        @return:
        """
        self._setAttribute("value", int((self._value / self._values) * 100))
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
        if self._values >= self._value+v:
            self._value += v
            self._setAttribute("value", int((self._value / self._values) * 100))
        return self
    def isFull(self)->bool:
        """
        Returns a boolean if the Processbar is full.
        @return:
        """
        return self._values <= self._value
    def reset(self):
        """
        Sets the bar progress to 0.
        Processbar is empty.
        @return:
        """
        self._setAttribute("value", 0)
        self._value = 0
        return self
    def setValue(self, v:int):
        """
        Set the Processbar percentage by value.
        Default maxvalue is 100 (full Processbar).
        Can be chnged by using 'setValues' method.
        @param v:
        @return:
        """
        if self._values >= v:
            self._value = v
            self._setAttribute("value", int((self._value / self._values) * 100))
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
        self._value = p / 100 * self._values
        return self
class Text(_LockableWidget):
    """
    Widget:
    Textbox where the user can input Text.
    Can also be user to display multiline text.
    Text widget can be made read only.
    Colors and font can be changed individually.
    """
    def __init__(self, _master, group:WidgetGroup =None, readOnly=False):
        if not _isinstanceAny(_master, Tk, NotebookTab, "Canvas", Frame, LabelFrame):
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+" or Tk instance not: "+str(_master.__class__.__name__))
        
        self._autoScroll = False
        self._tagCounter = 0
        
        self._setReadOnly(readOnly)
        
        super().__init__(child=self,
                         widget=_tk.Text(_master._get()),
                         master=_master,
                         group=group)
    def addLine(self, text:str, tags:str | tuple=None):
        """
        Adds a Line of text to the Textbox widget.
        @param text:
        @param color: color of that line. Default: BLACK
        @return:
        """
        if not text.endswith("\n"): text = text+"\n"
        self.addText(text, tags)
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
                self._widget.tag_add(_id, firstMarker, secondMarker)
                self._widget.tag_config(_id, foreground=colors[textSection[0]].value)
            else:
                print(f"'{textSection}' has no valid color tag.")
            firstMarkerChar = int(secondMarker.split(".")[1])
    def setText(self, text:str, tags:str | tuple=None):
        """
        Overwrites the text with 'text'.
        @param text:
        @return:
        """
        self.clear()
        self.addText(text, tags)
        return self
    def setAutoScroll(self, b:bool=True):
        """
        Enabled Automatic Scrolling if text were added.
        """
        self._autoScroll = b
        return self
    @_lockable
    def addText(self, text:str, tags:str | tuple=None):
        """
        Adds text to the Text box.
        Can be modfied by tag.
        @param text:
        @param tags:
        @return:
        """
        self._tagCounter += 1
        tags = tags if type(tags) is tuple else (tags,)
        self._widget.insert("end", str(text), tags)
        if self._autoScroll:
            self._widget.see("end")
        self._tagCounter += text.count("\n")
        return self
    def setBgColorByTag(self, tag:str, color:Color | str):
        self._widget.tag_configure(tag, background=remEnum(color))
        return self
    def setFgColorByTag(self, tag:str, color:Color | str):
        self._widget.tag_configure(tag, foreground=remEnum(color))
        return self
    def setFontByTag(self, tag:str, font:Font):
        #TODO impl
        pass
    def getText(self)->str:
        """
        Returns Text content.
        @return:
        """
        return self._widget.get(0.0, "end")
    def scrollDown(self):
        """
        Scrolls all the way down.
        Redundant to: 'Text.see("end")'
        @return:
        """
        self._widget.see("end")
        return self
    @_lockable
    def clear(self):
        """
        Clears the Textbox.
        @return:
        """
        self._widget.delete(0.0, _tk.END)
        for i in self._widget.tag_names():
            self._widget.tag_delete(i)
        return self
    def getSelectedText(self)->Union[str, None]:
        """
        Returns the selected text.
        Returns None if no text is selected.
        @return:
        """
        try:
            return self._widget.get("sel.first", "sel.last")
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
        # old: _EventHandler.registerNewValidateCommand(self, func, [], "all", decryptValueFunc=self._decryptEvent, defaultArgs=defaultArgs, disableArgs=disableArgs)
        return self
    def setSelectForeGroundColor(self, c:Union[Color, str]):
        """
        Set select foregroundcolor.
        @param c:
        @return:
        """
        self._setAttribute("selectforeground", remEnum(c))
    def setSelectBackGroundColor(self, c:Union[Color, str]):
        """
        Set select background color.
        @param c:
        @return:
        """
        self._setAttribute("selectbackground", remEnum(c))
    def setCursorColor(self, c:Union[Color, str]):
        """
        Set cursor color.
        @param c:
        @return:
        """
        self._setAttribute("insertbackground", remEnum(c))
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
        self._setAttribute("wrap", remEnum(w))
        return self
    def _decryptEvent(self, args, event):
        return self.getText()
#continue!

class _SubFolder:
    #TODO finish
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
        if len(self._headers) == 0:
            raise TKExceptions.InvalidHeaderException("Set Tree Headers first!")
        if len(self._headers) != len(list(args)):
            raise TKExceptions.InvalidHeaderException("Length of headers must be the same as args of addEntry!")
        self._widget.insert(parent=self._parent, index=index, text=args[0], values=args[1:])
    def createFolder(self, *args, index="end"):
        if isinstance(args[0], tuple) or isinstance(args[0], list):
            args = args[0]
        if len(self._headers) == 0:
            raise TKExceptions.InvalidHeaderException("Set Tree Headers first!")
        if len(self._headers) != len(list(args)):
            raise TKExceptions.InvalidHeaderException("Length of headers must be the same as args of addEntry!")
        parent = self._widget.insert(parent=self._parent, index=index, text=args[0], values=args[1:])
        return _SubFolder(parent, self._data)
class TreeView(_Widget):
    """TODO
    tag_configure:
        font, image, foreground


    """
    def __init__(self, _master, group:WidgetGroup =None):
        # TODO check / add sorting (headers)
        if not _isinstanceAny(_master, Tk, NotebookTab, "Canvas", Frame, LabelFrame):
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+" or Tk instance not: "+str(_master.__class__.__name__))

        self._xScrollbar = None
        self._headers = []
        self._onHeaderClick = None
        self._useIndex = None
        self._selectMode = "single"

        super().__init__(child=self,
                         widget=_ttk.Treeview(_master._get()),
                         master=_master,
                         group=group)
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
        self._yScrollbar = sc
        #sc.setOrientation(Orient.VERTICAL)
        sc._setAttribute("orient", _tk.VERTICAL)
        sc._setAttribute("command", self._widget.yview)
        self._setAttribute("xscrollcommand", sc._get().set)
        return self
    def getSelectedItem(self)->list | dict | None:
        return self._decryptEvent(None, None)
    def clear(self):
        if self.length() == 0: return self
        self._widget.delete(*self._widget.get_children())
        return self
    def setTableHeaders(self, *args):
        if isinstance(args[0], tuple) or isinstance(args[0], list):
            args = args[0]
        self._headers = [str(i) for i in args]
        self._setAttribute("columns", self._headers[1:])
        self._widget.column("#0", stretch=False)
        self._widget.heading("#0", text=self._headers[0], anchor="w", command=lambda a=self._headers[0], b=0:self._clickHeader((a, b)))
        for i, header in enumerate(self._headers[1:]):
            self._widget.column(header, stretch=False)
            self._widget.heading(header, text=header, anchor="w", command=lambda a=header, b=1+i:self._clickHeader((a, b)))
    def addEntry(self, *args, index="end", image=None, tag:str | tuple=None):
        if isinstance(image, TkImage) or isinstance(image, PILImage):
            image = image._get()
        if isinstance(args[0], tuple) or isinstance(args[0], list):
            args = args[0]
        if len(self._headers) == 0:
            raise TKExceptions.InvalidHeaderException("Set Tree Headers first!")
        if len(self._headers) != len(list(args)):
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
        _id = self._widget.insert(parent="", index=index, **data)
        return self
    def setBgColorByTag(self, tag:str, color:Color | str):
        self._widget.tag_configure(tag, background=remEnum(color))
        return self
    def setFgColorByTag(self, tag:str, color:Color | str):
        self._widget.tag_configure(tag, foreground=remEnum(color))
        return self
    def setEntry(self, *args, index=0):
        index = self._getIds()[index]
        #if isinstance(image, TkImage) or isinstance(image, PILImage):
        #    image = image._get()
        if isinstance(args[0], tuple) or isinstance(args[0], list):
            args = args[0]
        if len(self._headers) == 0:
            raise TKExceptions.InvalidHeaderException("Set Tree Headers first!")
        if len(self._headers) != len(list(args)):
            raise TKExceptions.InvalidHeaderException("Length of headers must be the same as args of addEntry!")
        #if image is not None: _id = self._widget.item(index, parent="", text=args[0], values=args[1:], image=image)
        else: _id = self._widget.item(index, text=args[0], values=args[1:])
        return self
    def createFolder(self, *args, index="end"):
        if isinstance(args[0], tuple) or isinstance(args[0], list):
            args = args[0]
        if len(self._headers) == 0:
            raise TKExceptions.InvalidHeaderException("Set Tree Headers first!")
        if len(self._headers) != len(list(args)):
            raise TKExceptions.InvalidHeaderException("Length of headers must be the same as args of addEntry!")
        parent = self._widget.insert(parent="", index=index, text=args[0], values=args[1:])
        return _SubFolder(parent, self._data)
    def setNoSelectMode(self):
        self._setAttribute("selectmode", "none")
        return self
    def setMultipleSelect(self):
        self._setAttribute("selectmode", "extended")
        self._selectMode = "multiple"
        return self
    def setSingleSelect(self):
        self._setAttribute("selectmode", "browse")
        self._selectMode = "single"
        return self
    def clearSelection(self):
        for item in self._widget.selection():
            self._widget.selection_remove(item)
        return self
    def see(self, index):
        if len(self._getIds()) > index and len(self._getIds()):
            self._widget.see(self._getIds()[index])
        return self
    def onSelectHeader(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False, useIndex=False):
        self._onHeaderClick = _EventHandler._getNewEventRunnable(self, func, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs)
        self._useIndex = useIndex
        return self
    #TODO add length from subFolders!
    def length(self):
        return len(self._getIds())
    #TODO test after resorting items -> _getIds correct?
    def setItemSelectedByIndex(self, index:int, clearFirst=True):
        assert index < len(self._getIds()), "index is too large: \n\tListbox_length: "+str(len(self._getIds()))+"\n\tIndex: "+str(index)
        if clearFirst: self._widget.selection_set(self._getIds()[index])
        else: self._widget.selection_add(self._getIds()[index])
        return self
    """
    def setItemSelectedByName(self, name, clearFirst=True):
        if clearFirst: self._widget.selection_clear(0, "end")
        if name in self.getAllSlots():
            self.setItemSelectedByIndex(self.getAllSlots().index(name))
        return self
    """
    def getSize(self):
        return len(self._getIds())
    def deleteItemByIndex(self, index):
        self._widget.delete(self._getIds()[index])
        return self
    def getIndexByName(self, item):
        return self.getAllSlots().index(item)
    def getDataByIndex(self, index)->dict:
        return self._getDataFromId(self._getIds()[index])
    def getSelectedIndex(self)->int | None | list:
        if len(self._widget.selection()) == 0: return None
        if self._selectMode == "single":
            return self._getIds().index(self._widget.selection()[0])
        else:
            ids = self._getIds()
            return [ids.index(i) for i in self._widget.selection()]
    def getAllSlotIndexes(self):
        return [i for i in range(self.length())]
    def getAllSlots(self):
        return [self._widget.item(i) for i in self._getIds()]
    def _getIds(self):
        return self._widget.get_children()
    def _decryptEvent(self, args, event):
        self.getParentWindow().updateIdleTasks()
        ids = self._widget.selection()
        if not len(ids): return None
        items = []
        for id_ in ids:
            item = self._widget.item(id_)
            if event is not None and event["use_index"]:
                items.append(
                    self._getIds().index(id_)
                )
                continue
            a = {self._headers[0]:item["text"]}
            for i, h in enumerate(self._headers[1:]): a[h] = item["values"][i]
            items.append(a)
        if self._selectMode == "single": return items[0]
        return items
    def _clickHeader(self, hName):
        if self._onHeaderClick is not None:
            handler = self._onHeaderClick
            handler.event["value"] = hName[0] if not self._useIndex else hName[1]
            handler()
    def _getDataFromId(self, id_):
        item = self._widget.item(id_)
        a = {self._headers[0]:item["text"]}
        for i, h in enumerate(self._headers[1:]): a[h] = item["values"][i]
        return a
class SpinBox(_LockableWidget):
    def __init__(self, _master, group:WidgetGroup =None, optionList:list=None, readOnly=True):
        if not _isinstanceAny(_master, Tk, NotebookTab, "Canvas", Frame, LabelFrame):
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+" or Tk instance not: "+str(_master.__class__.__name__))

        self._setReadOnly(readOnly)
        super().__init__(child=self,
                         widget=_tk.Spinbox(_master._get()),
                         master=_master,
                         group=group)

        if optionList is not None:
            self.setOptionList(optionList)
    def onButtonClick(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False):
        _EventHandler._registerNewCommand(self, func, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs, decryptValueFunc=self._decryptEvent)
    def onUserInputEvent(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False):
        _EventHandler._registerNewEvent(self, func, EventType.KEY_UP, args, priority, decryptValueFunc=self._decryptEvent, defaultArgs=defaultArgs, disableArgs=disableArgs)
    @_lockable
    def setValue(self, v, clearFirst=True):
        if clearFirst: self.clear()
        self._widget.insert(0, str(v))
        return self
    def getValue(self)->str:
        return self._widget.get()
    @_lockable
    def setOptionList(self, l:list):
        self._setAttribute("values", l)
    def clear(self):
        self._widget.delete(0, "end")
    def setButtonStyle(self, style:Style):
        self._setAttribute("buttondownrelief", remEnum(style))
        self._setAttribute("buttonup", remEnum(style))
        return self
    def setButtonBackground(self, color:Color):
        self._setAttribute("buttonbackground", remEnum(color))
        return self
    def setButtonCursor(self, cursor:Cursor):
        self._setAttribute("buttoncursor", remEnum(cursor))
        return self
    def setCursorColor(self, c:Color):
        self._setAttribute("insertbackground", remEnum(c))
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
    def __init__(self, _master, group:WidgetGroup =None, optionList:list=None, readonly=True):
        if not _isinstanceAny(_master, Tk, NotebookTab, "Canvas", Frame, LabelFrame):
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+" or Tk instance not: "+str(_master.__class__.__name__))

        self._stringVar = _tk.StringVar()

        self._setReadOnly(readonly, lockState="readonly")
        super().__init__(child=self,
                         widget=_ttk.Combobox(_master._get(), textvariable=self._stringVar),
                         master=_master,
                         group=group)
        if optionList is not None:
            self.setOptionList(optionList)
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
        self._widget.current(i)
        return self
    def getSelectedIndex(self)-> int | None:
        val = self._widget.get()
        if val in self._values:
            return self._values.index(val)
        return None
    @_lockable
    def clear(self):
        self._widget.delete(0, "end")
        return self
    def setText(self, text):
        self.setValue(text)
        return self
    @_lockable
    def setValue(self, text, clearFirst=True):
        if clearFirst: self._widget.delete(0, "end")
        self._widget.insert(0, str(text))
        return self
    def getValue(self):
        return self._widget.get()
    @_lockable
    def setOptionList(self, it:List[str]):
        self._values = it
        self._setAttribute("values", it)
        return self
    def addOption(self, i:str):
        self._values.append(i)
        self.setOptionList(self._values)
        return self
    def _decryptEvent(self, args, event):
        return self._widget.get()
    def _decryptEvent2(self, args, event):
        return args
class Separator(_Widget):
    def __init__(self, _master, group:WidgetGroup =None):
        if not _isinstanceAny(_master, Tk, NotebookTab, "Canvas", Frame, LabelFrame):
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+" or Tk instance not: "+str(_master.__class__.__name__))

        super().__init__(child=self,
                         widget=_ttk.Separator(_master._get()),
                         master=_master,
                         group=group)
class ContextMenu(_Widget):
    def __init__(self, _master, group:WidgetGroup =None, closable=True, eventType:Union[EventType, Key, Mouse, None]=Mouse.RIGHT_CLICK):
        if not hasattr(_master, "_get"):
            raise TKExceptions.InvalidWidgetTypeException("_master must be any Widget or Tk instance not: "+str(_master.__class__.__name__))

        self._subMenus = []
        self._closeable = closable
        self._eventType = eventType

        super().__init__(child=self,
                         widget=None,#_tk.Menu(_master._get(), tearoff=0),
                         master=_master,
                         group=group)
        self._widget = self._createSubMenu()
        self._registerChild()
        if eventType is not None:
            _EventHandler._registerNewEvent(_master,
                                            self.open,
                                            eventType,
                                            args=None,
                                            priority=1,
                                            decryptValueFunc=self._decryptEvent)
    def _createSubMenu(self):
        m = _SubMenu(self, "")
        #m._menu = self._widget
        self._subMenus.append(m)
        return m
    def addSeparator(self):
        self._widget._widgets.append(["separator", None, None])
        return self
    def createSubMenu(self, button:Button):
        return self._widget.createSubMenu(button, self._group)
    def bindToWidget(self, widg):
        _EventHandler._registerNewEvent(widg, self.open, self._eventType, [], 1, decryptValueFunc=self._decryptEvent, defaultArgs=False, disableArgs=False)
    def open(self, args:Location2D | Event):
        if isinstance(args, Event):
            if args.getValue() is not None:
                loc = Location2D(args.getValue())
            else:
                loc = Location2D(
                    args.getTkArgs().x_root,
                    args.getTkArgs().y_root,
                )
        else:
            loc = args
        loc.toInt()
        try:
            self._widget._widget.tk_popup(loc.getX(), loc.getY())
        except Exception as e:
            print(e)
        finally:
            if not self._closeable: #fuer Fabi :^)
                self._widget._widget.grab_release()
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
        for i in self._subMenus:
            i.create()
    def _add(self, type_:str, clazz:_Widget, subMenu=None):
        return self._widget._add(type_, clazz, subMenu)
class TaskBar(_Widget):
    def __init__(self, _master, group:WidgetGroup =None):
        if not _isinstanceAny(_master, Tk):
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+" or Tk instance not: "+str(_master.__class__.__name__))

        if _master._hasTaskBar:
            raise RuntimeError("You cannot apply two Menus to the Window!")
        _master._hasTaskBar = True

        self._subMenus = []

        super().__init__(child=self,
                         widget=_tk.Menu(_master._get(), tearoff=False),
                         master=_master,
                         group=group)
        self._applyMenu(_master)
    def createSubMenu(self, name:str):
        m = _SubMenu(self, name)
        self._subMenus.append(m)
        self._widget.add("cascade", label=name, menu=m._get())
        return m
    def place(self, x=0, y=0, width=None, height=None, anchor=Anchor.UP_LEFT):
        pass
    def grid(self, row=0, column=0):
        pass
    def create(self):
        for i in self._subMenus: i.create()
    def _applyMenu(self, _master):
        _master._get().config(menu=self._widget)
class _SubMenu:
    _SUB_MENUS = []
    def __init__(self, parentMenu, name:str, group:WidgetGroup =None):
        self._widgets = [] #[["command", <type: Button>], ["cascade", <type: Button>, <type: SubMenu>]]
        self._name = name
        self._group = parentMenu._group if group is None else group
        self._master = parentMenu._master
        self._parentWidget = parentMenu._widget
        self._parentMaster = parentMenu if _isinstanceAny(parentMenu, TaskBar, ContextMenu) else parentMenu._parentMaster
        self._widget = _tk.Menu(self._parentWidget, tearoff=False)
    def clear(self):
        #TODO use generated widget tree
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
                self._widget.delete(0)
            except Exception as e:
                print(e)
        self._widgets = []
    def createSubMenu(self, button:Button, group:WidgetGroup =None):
        assert isinstance(button, Button), "button must be Button instance!"

        # delete this button from other menu: "menu.createSubMenu(tk.Button(menu).setText("Here"))"
        clazz = self._widgets[-1][1]
        if clazz == button:
            self._widgets.pop(-1)

        m = _SubMenu(self, button._widgetProperties.get("text", ""), group)
        self._widgets.append(["cascade", button, m])
        return m
    def addSeparator(self):
        self._widgets.append(["separator", None, None])
    def create(self): #@TODO fix if menus are created after mainloop
        for w in self._widgets:
            type_, clazz, subMenu = w
            if clazz is None:
                self._widget.add(type_) # seperator
                continue

            widgetData:dict = clazz._widgetProperties

            if subMenu is not None: # submenu
                self._widget.add(type_, self._parseData(widgetData, subMenu))
                subMenu.create()
                continue
            self._widget.add(type_, self._parseData(widgetData))

        #TODO remove after testing
        """#if self._data["created"]: return#@TODO FIX self._data["create"] is True
        for widget in self._widgets:
            if widget[1] is not None:
                _data = widget[1]._widgetProperties.copy()
                if _data.keys().__contains__("text"): _data["label"] = _data["text"]

                if widget[0] == "cascade": _data["menu"] = widget[2]._menu if hasattr(widget[2], "_menu") else widget[2]

                self._menu.add(widget[0], **{k:v for k, v in zip(_data.keys(), _data.values()) if .__contains__(k)})
                if widget[0] == "cascade" and hasattr(widget[2], "create"):
                    widget[2].create()
            else:
                #print(type(widget[0]), widget)
                self._menu.add(widget[0], {})"""
    def _add(self, type_:str, clazz:_Widget, subMenu=None)->TaskBar | ContextMenu:
        self._widgets.append([type_, clazz, subMenu])
        clazz._instanceOfMenu = True
        return self._parentMaster
    def _parseData(self, d:dict, menu=None)->dict:
        _d = {}
        for key in d.keys():
            if key in _ALLOWED_MENU_PROPERTIES:
                _d[key] = d[key]
        _d["label"] = (d["text"] if "text" in d.keys() else "")
        if menu is not None:
            _d["menu"] = menu._widget
        return _d
    def _get(self):
        return self._widget
    def destroy(self):
        pass

class NotebookTab(_ContainerWidget):
    def __init__(self, _master, title:str, group:WidgetGroup =None):
        if not isinstance(_master, Notebook):
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + " instance not: " + str(_master.__class__.__name__))

        self._title = title

        super().__init__(child=self,
                         widget=_tk.Frame(_master._get()),
                         master=_master,
                         group=group)


        self._tabIndex = self.getNumberOfTabs() - 1
        self._master._get().add(self._widget, text=self._title)
    def __repr__(self):
        return str(self.__class__.__name__) + f"(title={self._title}, " + str(self._childWidgets) + ")"
    def getTabIndex(self):
        return self._tabIndex
    def getTabName(self):
        return self._master._get().tab(self._tabIndex, "text")
    def setTitle(self, text:str):
        self._master._get().tab(self._tabIndex, text=text)
        self._title = text
        return self
    def setSelected(self):
        self._master._get().select(self._tabIndex)
        return self
    def getNumberOfTabs(self):
        return self._master._get().index("end")
    def place(self, x=None, y=None, width=None, height=None, anchor:Anchor=Anchor.UP_LEFT):
        pass
    def placeRelative(self, fixX:int=None, fixY:int=None, fixWidth:int=None, fixHeight:int=None, xOffset=0, yOffset=0, xOffsetLeft=0, xOffsetRight=0, yOffsetUp=0, yOffsetDown=0, stickRight=False, stickDown=False, centerY=False, centerX=False, center=False, changeX=0, changeY=0, changeWidth=0, changeHeight=0):
        pass
    def grid(self, row=0, column=0):
        pass
class Notebook(_ContainerWidget):
    def __init__(self, _master, group:WidgetGroup =None):
        if not _isinstanceAny(_master, Tk, NotebookTab, "Canvas", Frame, LabelFrame):
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+" or Tk instance not: "+str(_master.__class__.__name__))

        self._childWidgets = [] # All Tabs are stored here

        super().__init__(child=self,
                         widget=_ttk.Notebook(_master._get()),
                         master=_master,
                         group=group)
        self.onTabSelectEvent(self._selectTab, priority=100)
    def onTabSelectEvent(self, func, args:list=None, priority:int=0, disableArgs=False, defaultArgs=False):
        _EventHandler._registerNewEvent(self, func, EventType.customEvent("<<NotebookTabChanged>>"), args, priority, decryptValueFunc=self._decryptEvent, disableArgs=disableArgs, defaultArgs=defaultArgs)
    def setCtrlTabEnabled(self):
        self._widget.enable_traversal()
        return self
    def getSelectedTabIndex(self)->int:
        return self._widget.index("current")
    def getSelectedTabName(self)->str:
        return self._widget.tab(self.getSelectedTabIndex(), "text")
    def getSelectedTab(self)->NotebookTab:
        return self._childWidgets[self.getSelectedTabIndex()]
    def createNewTab(self, name, group:WidgetGroup =None)->NotebookTab:
        return NotebookTab(self, name, ifIsNone(group, self._group))
    def _decryptEvent(self, args, event):
        return self.getSelectedTab()
    def _selectTab(self, e:Event):
        index = self.getSelectedTabIndex()
        for i in range(len(self._childWidgets)):
            if i == index:
                self._childWidgets[i]._placed = True
                continue
            self._childWidgets[i]._placed = False
        self.updateRelativePlace()
