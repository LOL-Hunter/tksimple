from webbrowser import open as openURL
import tkinter as _tk
import tkinter.dnd as _dnd
from datetime import datetime as _date

from .window import *
from .widget import *
from .draw import Canvas
from .util import Font, State
from .event import Event, _EventHandler, _EventRegistry
from .tkmath import _map

class HyperLinkLabel(Label):
    """
    Label for displaying URL.
    CLickable to open URL.
    """
    def __init__(self, master, group=None, url=None):
        super().__init__(master, group)
        self._hook = None
        self._hoverText = None
        self._hoverFont = None
        self._hoverColor = "black"
        self._doOpenSite = True
        self.bind(self._onEnter, EventType.ENTER)
        self.bind(self._onLeave, EventType.LEAVE)
        self.resetClickedColor()
        self.setURL(url)
        self.setFg(Color.hex("#0000EE"))
    def setURL(self, url:str):
        """
        Set URL and update on Label.
        @param url:
        @return:
        """
        self._url = url
        self.setText(url)
        self.setFont(
            Font(
                underline=True
            )
        )
        if self._hoverText is not None and self._hoverFont is not None:
            self._applyHoverText()
        return self
    def setClickedColor(self):
        """
        Set Colorcode to #551A8B (purple).
        @return:
        """
        self.setFg(Color.hex("#551A8B"))
        return self
    def resetClickedColor(self):
        """
        Set Colorcode to #0000EE (blue).
        @return:
        """
        self.setFg(Color.hex("#0000EE"))
        return self
    def setHoverText(self, t:str, font=None, color="black"):
        self._hoverText = t
        self._hoverColor = color
        self._hoverFont = Font() if font is None else font
        self._applyHoverText()
        return self
    def setCommand(self, cmd:Callable, args:list=None, priority:int=0, disableArgs=False, defaultArgs=False, openWebPage=True):
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
        self._hook = cmd
        self._doOpenSite = openWebPage
        _EventHandler._registerNewEvent(self, func=self._openWebsite, eventType=EventType.LEFT_CLICK, priority=priority, args=args, disableArgs=disableArgs, defaultArgs=defaultArgs)
        return self
    def _openWebsite(self, e):
        if self._hook is not None:
            self._hook(e)
        if e["setCanceled"]: return
        self.setClickedColor()
        if self._doOpenSite and self._url is not None:
            openURL(self._url)
    def _onEnter(self):
        if self._hoverText is not None and self._hoverFont is not None:
            self.setText(self._url)
            self.setFont(
                Font(
                    underline=True
                )
            )
            self.resetClickedColor()
    def _onLeave(self):
        if self._hoverText is not None and self._hoverFont is not None:
            self._applyHoverText()
    def _applyHoverText(self):
        self.setText(self._hoverText)
        self.setFont(self._hoverFont)
        self.setFg(self._hoverColor)
class PDFViewer(Widget):
    def __init__(self, _master, path, group=None):
        from tkPDFViewer import tkPDFViewer as pdf
        if isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            viewer = pdf.ShowPdf()
            self._data = {"master": _master, "widget": viewer.pdf_view(_master._get(), 200, 200, path), "init": {}}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + ", Frame or Tk instance not: " + str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
class MatPlotLibFigure(Widget):
    """
    Widget:
    Use this widget to display plots from matplotlib library.

    Pass the Figure instance from matplotlib.
    """
    def __init__(self, _master, fig, group=None, toolBar=False):
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
        if isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            master = _master
            init = {}
            if toolBar:
                init = {"func":self._bind}
                master = Frame(_master)
                master.setBg("green")

            figureWidget = FigureCanvasTkAgg(fig, master._get())
            figureWidget.draw()

            if toolBar:
                toolbar = NavigationToolbar2Tk(figureWidget, master._get(), pack_toolbar=False)
                toolbar.update()

                self.wwidget_plot = Widget(None, {"master":master, "widget":figureWidget.get_tk_widget()}, None)
                self.wwidget_settings = Widget(None, {"master":master, "widget":toolbar}, None)
                self.wwidget_plot.placeRelative(changeHeight=-30)
                self.wwidget_settings.placeRelative(stickDown=True, fixHeight=30)

                master = master._get()
            else:
                master = figureWidget.get_tk_widget()

            self._data = {"master": _master, "widget": master, "figureWidget":figureWidget, "init": init}
        else:
            raise TKExceptions.InvalidWidgetTypeException(
                "_master must be " + str(self.__class__.__name__) + ", Frame or Tk instance not: " + str(
                    _master.__class__.__name__))
        super().__init__(self, self._data, group)
    def _updatePlace(self, e):
        self.wwidget_plot.updateRelativePlace()
        self.wwidget_settings.updateRelativePlace()
    def _bind(self):
        self.bind(self._updatePlace, EventType.CUSTOM_RELATIVE_UPDATE)
    def draw(self):
        """
        Draws the figure.
        @return:
        """
        self["figureWidget"].draw()
        return self
class Calendar(Widget):
    """
    Widget:
    This widget displays a calendar to select day and year.

    To use this widget the 'tkcalencar' library have to be installed.
    """
    def __init__(self, _master, group=None):
        import tkcalendar as cal
        if isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master": _master, "widget": cal.Calendar(_master._get()), "init": {}}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + ", Frame or Tk instance not: " + str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def _decryptEvent(self, args, event):
        return self["widget"].get_date()
    def setDate(self, d, m, y):
        """
        Sets the date.
        @param d: day
        @param m: month
        @param y: year
        @return:
        """
        self._setAttribute("day", d)
        self._setAttribute("month", m)
        self._setAttribute("year", y)
        return self
    def setMaxDate(self, d, m, y):
        """
        Set the maxdate.
        Used to specify a range to select the date from.
        @param d: day
        @param m: month
        @param y: year
        @return:
        """
        d = int(d)
        m = int(m)
        y = int(y)
        self._setAttribute("maxdate", _date(y, m, d))
        return self
    def setMinDate(self, d, m, y):
        """
        Set the mindate.
        Used to specify a range to select the date from.
        @param d: day
        @param m: month
        @param y: year
        @return:
        """
        d = int(d)
        m = int(m)
        y = int(y)
        self._setAttribute("mindate", _date(y, m, d))
        return self
    def getValue(self):
        """
        returns the Date in string format.
        Example: '1/1/20'
        @return:
        """
        return self["widget"].get_date()
    def onCalendarSelectEvent(self, func, args:list = None, priority:int=0, defaultArgs=False, disableArgs=False):
        """
        Bind on date select event to this widget. Runs given function on trigger.

        @param func: function get called on trigger
        @param args: Additional arguments as List.
        @param priority: If several equal events are bound, it's possible to set priorities.
        @param defaultArgs: if True the default tkinter gets passed in bound function instead of Event-instance.
        @param disableArgs: if True no args gets passed.
        @return:
        """
        _EventHandler._registerNewEvent(self, func, EventType.customEvent("<<CalendarSelected>>"), args, priority, decryptValueFunc=self._decryptEvent, defaultArgs=defaultArgs, disableArgs=disableArgs)
class DropdownCalendar(Widget):
    """
    Widget:
    This widget displays an Entry like folds out calendar to select day and year.

    To use this widget the 'tkcalencar' library have to be installed.
    """
    def __init__(self, _master, group=None):
        import tkcalendar as cal
        if isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master": _master, "widget": cal.DateEntry(_master._get()), "init": {}}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + ", Frame or Tk instance not: " + str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def _decryptEvent(self, args, event):
        return self["widget"].get_date()
    def setDate(self, d, m, y):
        """
        Sets the date.
        @param d: day
        @param m: month
        @param y: year
        @return:
        """
        self._setAttribute("day", d)
        self._setAttribute("month", m)
        self._setAttribute("year", y)
        return self
    def setMaxDate(self, d, m, y):
        """
        Set the maxdate.
        Used to specify a range to select the date from.
        @param d: day
        @param m: month
        @param y: year
        @return:
        """
        d = int(d)
        m = int(m)
        y = int(y)
        self._setAttribute("maxdate", _date(y, m, d))
        return self
    def setMinDate(self, d, m, y):
        """
        Set the mindate.
        Used to specify a range to select the date from.
        @param d: day
        @param m: month
        @param y: year
        @return:
        """
        d = int(d)
        m = int(m)
        y = int(y)
        self._setAttribute("mindate", _date(y, m, d))
        return self
    def getValue(self):
        """
        returns the Date in string format.
        Example: '1/1/20'
        @return:
        """
        return self["widget"].get_date()
    def onCalendarSelectEvent(self, func, args: list = None, priority: int = 0, defaultArgs=False, disableArgs=False):
        """
        Bind on date select event to this widget. Runs given function on trigger.

        @param func: function get called on trigger
        @param args: Additional arguments as List.
        @param priority: If several equal events are bound, it's possible to set priorities.
        @param defaultArgs: if True the default tkinter gets passed in bound function instead of Event-instance.
        @param disableArgs: if True no args gets passed.
        @return:
        """
        _EventHandler._registerNewEvent(self, func, EventType.customEvent("<<CalendarSelected>>"), args, priority, decryptValueFunc=self._decryptEvent, defaultArgs=defaultArgs, disableArgs=disableArgs)
class OnOffButton(Widget):
    """
    Widget:
    This is a custom Widget.
    This widget represents a Button wich can be toggled on and off.
    """
    def __init__(self, _master, group=None, text="", default=False, colorsActive=True, reliefActive=False):
        if isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master":_master,  "text":text, "widget":_tk.Button(_master._get()), "value":default, "relief":reliefActive, "color":colorsActive, "onText":None, "offText":None, "init":{"text":text}}
            if default:
                if colorsActive: self._data["init"]["bg"] = Color.GREEN.value
                if reliefActive: self._data["init"]["relief"] = Style.SUNKEN.value
            else:
                if colorsActive: self._data["init"]["bg"] = Color.RED.value
                if reliefActive: self._data["init"]["relief"] = Style.SUNKEN.value
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def setValue(self, v:bool):
        """
        Set the state (on/off) as bool.
        @param v:
        @return:
        """
        self["value"] = bool(v)
        self._update()
        return self
    def getValue(self)->bool:
        """
        Returns the current state as boolean.

        @return:
        """
        return self["value"]
    def setOn(self):
        """
        Set state to True.
        @return:
        """
        self["value"] = True
        self._update()
        return self
    def setOff(self):
        """
        Set state to False.
        @return:
        """
        self["value"] = False
        self._update()
        return self
    def setOnText(self, text:Union[str, None]):
        """
        Set the text wich is displayed qh´´when state is True.
        @param text:
        @return:
        """
        self["onText"] = str(text)
        self._update()
        return self
    def setOffText(self, text:Union[str, None]):
        """
        Set the text wich is displayed qh´´when state is True.
        @param text:
        @return:
        """
        self["offText"] = str(text)
        return self
    def setCommand(self, cmd, args:list=None, priority:int=0, disableArgs=False, defaultArgs=False):
        """
        Bind on click event to this widget. Runs given function on trigger.
        EventValue: None
        @param cmd: function get called on trigger
        @param args: Additional arguments as List.
        @param priority: If several equal events are bound, it's possible to set priorities.
        @param defaultArgs: if True the default tkinter gets passed in bound function instead of Event-instance.
        @param disableArgs: if True no args gets passed.
        @return:
        """
        self["command"] = _EventHandler._getNewEventRunnable(self, cmd, args, priority)
        _EventHandler._registerNewCommand(self, self._press, args, priority)
        self._update()
        return self
    def _press(self, e):
        self["value"] = not self["value"]
        self._update()
        func = self["command"]
        func["value"] = self["value"]
        if func is not None:
            func()
    def _update(self):
        if self["value"]:
            if self["onText"] is not None: self.setText(self["onText"])
            if self["color"]: self.setBg(Color.GREEN)
            if self["relief"]: self.setStyle(Style.SUNKEN)
        else:
            if self["offText"] is not None: self.setText(self["offText"])
            if self["color"]: self.setBg(Color.RED)
            if self["relief"]: self.setStyle(Style.RAISED)
        return self["value"]
class TextEntry(LabelFrame):
    """
    Widget:
    This is a Custom Widget.
    An Entry and a Label are combined.
    Used to give the user a hint, what to write in the Entry.
    Important: First set the Text and THEN place the widget.
    """
    def __init__(self, _master, group=None, text=""):
        super().__init__(_master, None)
        if isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            _data = {"value":"", "label":Label(self, group), "entry":Entry(self, group)}
            _data["label"].setText(text)
            self._addData(_data)
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__.__name__))
        #if group is not None:
        #    group.add(self._ins)
    def bind(self, func:callable, event: Union[EventType, Key, Mouse, str], args:list=None, priority:int=0, defaultArgs=False, disableArgs=False):
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
        _EventHandler._registerNewEvent(self, func, event, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs)
        return self
    def updatePlace(self):
        self._data["label"]._get().grid(row=0, column=0)
        self._data["entry"]._get().grid(row=0, column=1, sticky=Anchor.RIGHT.value)
    def getValue(self)->str:
        """
        Returns the Entry value.
        @return:
        """
        return self.getEntry().getValue()
    def setValue(self, v:str):
        """
        Set the Entry value.
        @param v:
        @return:
        """
        self.getEntry().clear()
        self.getEntry().setValue(str(v))
        return self
    def setText(self, text:str):
        """
        Set the Label text.
        @param text:
        @return:
        """
        self.getLabel().setText(text)
        return self
    def getEntry(self)->Entry:
        """
        Returns the sub Entry.
        Used for further configuration.
        @return:
        """
        return self._data["entry"]
    def getLabel(self)->Label:
        """
        Returns the sub Label.
        Used for further configuration.
        @return:
        """
        return self._data["label"]
    def clear(self):
        """
        Clears the Entry.
        @return:
        """
        self.getEntry().clear()
        return self
    def setDisabled(self):
        """
        Disables the Entry.
        @return:
        """
        self.getEntry().setDisabled()
        return self
    def setEnabled(self):
        """
        Enables the Entry.
        @return:
        """
        self.getEntry().setEnabled()
        return self
    def place(self, x=0, y=0, width=None, height=25, anchor=Anchor.UP_LEFT, entryStartX=None):
        """
        @param x:
        @param y:
        @param width:
        @param height:
        @param anchor:
        @param entryStartX: Use this to force lineup different Entrys
        @return:
        """
        offset = 5
        self._data["label"].place(0, 0)
        labelWidth = self._data["label"].getWidth()
        if entryStartX is not None: labelWidth = entryStartX
        if width is None:
            width = labelWidth+100
            entryWidth = 100
        else:
            entryWidth = width - labelWidth
        super().place(x, y, width, height)
        self._data["label"].place(0, 0, labelWidth, height-offset)
        self._data["entry"].place(labelWidth, 0, entryWidth-offset, height-offset)
        return self
    def placeRelative(self, fixX=None, fixY=None, fixWidth=None, fixHeight=None, xOffset=0, yOffset=0, xOffsetLeft=0, xOffsetRight=0, yOffsetUp=0, yOffsetDown=0, stickRight=False, stickDown=False, centerY=False, centerX=False, changeX=0, changeY=0, changeWidth=0, changeHeight=0, nextTo=None, updateOnResize=True):
        assert fixWidth is not None and fixHeight is not None, "fixWidth and fixHeight must be defined!"
        x = fixX if fixX is not None else 0
        y = fixY if fixY is not None else 0
        self.place(x, y, fixWidth, fixHeight)
        super().placeRelative(fixX, fixY, fixWidth, fixHeight, xOffset, yOffset, xOffsetLeft, xOffsetRight, yOffsetUp, yOffsetDown, stickRight, stickDown, centerY, centerX, changeX, changeY, changeWidth, changeHeight, nextTo, updateOnResize)
        return self
    def setFg(self, col:Union[Color, str]):
        self.getEntry().setFg(col)
        self.getLabel().setFg(col)
        return self
    def setBg(self, col:Union[Color, str]):
        self.getEntry().setBg(col)
        self.getLabel().setBg(col)
        return self
    def _get(self):
        return self._data["widget"]
class TextDropdownMenu(Widget):
    """
    Widget:
    This is a Custom Widget.
    DropdownMenu and Label combination.
    Used to give the user a hint, what to write/select in the DropdownMenu.
    Important: First set the Text and THEN place the widget.
    """
    def __init__(self, _master, group=None, text=""):
        if isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            widg = LabelFrame(_master)
            self._data = {"master":_master,  "widget":widg, "value":"", "dropdownMenu":DropdownMenu(widg), "label":Label(widg)}
            self._data["widget"]._get().grid(padx=10, pady=10)
            self._data["label"].setText(text)
            self._data["label"]._get().grid(row=0, column=0)
            self._data["dropdownMenu"]._get().grid(row=0, column=1)
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def bind(self, func, event: Union[EventType, Key, Mouse], args:list=None, priority:int=0, defaultArgs=False, disableArgs=False):
        """
        Binds a specific event to the Widget. Runs given function on trigger.

        @param func: function get called on trigger
        @param event:  Event type: EventType _Enum or default tkinter event as string.
        @param args: Additional arguments as List.
        @param priority: If several equal events are bound, it's possible to set priorities.
        @param defaultArgs: if True the default tkinter gets passed in bound function instead of Event-instance.
        @param disableArgs: if True no args gets passed.
        @return:
        """
        if event == "CANCEL": return
        _EventHandler._registerNewEvent(self, func, event, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs)
        return self
    def getValue(self)->str:
        """
        Returns Dropdownmenu content.
        @return:
        """
        return self.getDropdownMenu().getValue()
    def setValue(self, v:str):
        """
        Set the DropdownMenu value.
        @param v:
        @return:
        """
        self.getDropdownMenu().setValue(str(v))
        return self
    def getLabel(self):
        """
        Returns the sub Label.
        Used for further configuration.
        @return:
        """
        return Label(self["label"])
    def getDropdownMenu(self):
        """
        Returns the sub DropdownMenu.
        Used for further configuration.
        @return:
        """
        return DropdownMenu(self["dropdownMenu"])
    def setDisabled(self):
        """
        Disables the DropdownMenu.
        @return:
        """
        self.getDropdownMenu().setDisabled()
        return self
    def setEnabled(self):
        """
        Enables the DropdownMenu.
        @return:
        """
        self.getDropdownMenu().setEnabled()
        return self
    def _get(self):
        return self["widget"]._get()
class _DndHandler:
    def __init__(self, canvas, _id, widget, widgetCreator):
        self.canvas = canvas
        self.widget = widget
        self.widgetCreator = widgetCreator
        self.id = _id
    def press(self, event:Event):
        tkArgs = event.getTkArgs()
        event.printEventInfo()
        if _dnd.dnd_start(self, tkArgs):
            self.x_off = tkArgs.x
            self.y_off = tkArgs.y
    def dnd_end(self, target, event):
        pass
    def getWidgetCursorPos(self, event, canvas)->Location2D:
        # widget position relative to the screen
        rsx, rsy = canvas.getRelScreenPos()

        # pointer relative to the canvas
        return Location2D(
            (event.x_root - rsx) - self.x_off,
            (event.y_root - rsy) - self.y_off,
        )
class DndCanvas(Canvas):
    def __init__(self, _master, group=None):
        super().__init__(_master, group)
        canvas = self._get()
        canvas.dnd_accept = self._onDndWidget
        self._outlineID = None
        self["hide_widg_on_drag"] = False
        self["drag_enabled"] = True
        # register "private" methods
        setattr(self, "dnd_accept", self._onDndWidget)
        setattr(self, "dnd_enter", self._onDndEnter)
        setattr(self, "dnd_motion", self._onDndMotion)
        setattr(self, "dnd_leave", self._onDndLeave)
        setattr(self, "dnd_commit", self._onDndCommit)
    def _onDndWidget(self, dndHandl, event):
        return self if self["drag_enabled"] else None
    def _onDndEnter(self, dndHandl, event):
        self.setFocus()
        rsx, rsy = dndHandl.getWidgetCursorPos(event, self)
        x1, y1, x2, y2 = dndHandl.canvas._get().bbox(dndHandl.id) # WICHTIG .id impl

        canvasRect = Rect(
            Location2D(x1, y1),
            Location2D(x2, y2)
        )
        self._outlineID = self["widget"].create_rectangle(rsx, rsy, rsx+canvasRect.getWidth(), rsy+canvasRect.getHeight())
        self._onDndMotion(dndHandl, event)
    def _onDndMotion(self, dndHandl, event):
        if self["hide_widg_on_drag"]: dndHandl.canvas._get().itemconfigure(dndHandl.id, state="hidden")
        rsx, rsy = dndHandl.getWidgetCursorPos(event, self)
        x1, y1, x2, y2 = self["widget"].bbox(self._outlineID)  # WICHTIG .id impl
        self["widget"].move(self._outlineID, rsx-x1, rsy-y1)
    def _onDndLeave(self, dndHandl, event):
        self._getTkMaster().setFocus()
        self["widget"].delete(self._outlineID)
        self["widget"]["dnd_canvas"] = None
        self._outlineID = None
    def _onDndCommit(self, dndHandl, event):
        self._onDndLeave(dndHandl, event)
        rsx, rsy = dndHandl.getWidgetCursorPos(event, self)
        self.attachWidgetCreator(dndHandl.widget, rsx, rsy)

    def disableDrag(self):
        self["drag_enabled"] = False
    def enableDrag(self):
        self["drag_enabled"] = True
    def setWidgetHiddenWhileDrag(self, b:bool=True):
        self["hide_widg_on_drag"] = bool(b)
        return self

    def attachWidget(self, widget:Widget, x=0, y=0, width=None, height=None):
        """
        Attaches a widget to be dragged on this canvas.
        Only on this canvas. If multi-canvas dragging is needed use 'DndCanvas.attachWidgetCreator' method.
        """
        if "dnd_canvas" not in widget._data.keys():
            widget["dnd_canvas"] = None
        if widget["dnd_canvas"] is None: # register
            _id = self._get().create_window(x, y, window=widget._get(), anchor="nw")
            widget["dnd_canvas"] = _DndHandler(self, _id, widget, None)
            widget.bind(widget["dnd_canvas"].press, "<ButtonPress>", priority=10)
        else:
            widget["dnd_canvas"].canvas._get().delete(widget["dnd_canvas"].id)
            _id = self._get().create_window(x, y, width=width, height=height, window=widget._get(), anchor="nw")
            widget["dnd_canvas"].id = _id


    def attachWidgetCreator(self, widgetCreator:Callable, x=0, y=0):
        """
        Attaches a function which creates a widget.
        This widget can be dragged around on this canvas and to other canvases.
        Attach the widget again if you need to change any widget attribute.

        The passed function have to look like this:

        def function(root):
            label = Label(root)
            ...
            return label

        @param widgetCreator: function to create dragged widget.
        @param x: x position of widget.
        @param y: y position of widget.
        @return:
        """
        if isinstance(widgetCreator, Widget):
            _widget = widgetCreator
            widgetCreator = widgetCreator["dnd_canvas"].widgetCreator
            self.detachWidget(_widget)
        widget = widgetCreator(self)
        # check and register variables
        if "dnd_canvas" not in widget._data.keys():
            widget["dnd_canvas"] = None
        # check if already registered to this canvas
        if widget["dnd_canvas"] is not None:
            if widget["dnd_canvas"].widget._getID() == self._getID():
                return
            self.detachWidget(widget)
        _id = self._get().create_window(x, y, window=widget._get(), anchor="nw")
        widget["dnd_canvas"] = _DndHandler(self, _id, widget, widgetCreator)
        widget.bind(widget["dnd_canvas"].press, "<ButtonPress>", priority=10)
    def detachWidget(self, widget:Widget):
        if "dnd_canvas" not in widget._data.keys():
            widget["dnd_canvas"] = None
        if widget["dnd_canvas"] is not None:
            widget["dnd_canvas"].canvas._get().delete(widget["dnd_canvas"].id)
            widget["registry"].unregisterType("<ButtonPress>")
            print("destroy")
            widget._get().destroy()
class MenuPage(Frame):
    def __init__(self, master, group=None):
        super().__init__(master, group)
        self._menuData = {
            "history":[self],
            "master":self["tkMaster"],
            "active":False
        }
    def __str__(self):
        return type(self).__name__
    def openMenuPage(self, **kwargs):
        # remove other active Page
        self._menuData["active"] = True
        self.onShow(**kwargs)
        self._menuData["master"].updateDynamicWidgets()
    def openNextMenuPage(self, mp, **kwargs):
        self._menuData["active"] = False
        self.onHide()
        self.placeForget()
        history = self._menuData["history"].copy()
        history.append(mp)
        mp._menuData["history"] = history
        mp._menuData["active"] = True
        mp.onShow(**kwargs)
        self._menuData["master"].updateDynamicWidgets()
    def openLastMenuPage(self):
        if len(self._menuData) > 1:
            self.onHide()
            self.placeForget()
            newHistory = self._menuData["history"].copy()[:-1] # remove self
            history = newHistory[-1] # get new "self" -> last item
            history._menuData["history"] = newHistory # set hist to new instance
            history.onShow() # show new instance
            history._menuData["active"] = True
            self._menuData["master"].updateDynamicWidgets()
    def _onShow(self, **kwargs):
        self._menuData["active"] = True
        self.onShow(**kwargs)
    def isActive(self):
        return self._menuData["active"]
    def onShow(self, **kwargs):
        pass
    def onHide(self):
        pass
    def openHomePage(self, mainPage):
        assert isinstance(mainPage, MenuPage), "Please use 'MenuPage' instance!"
        mainPage._menuData["history"] = [mainPage]
        self.placeForget()
        mainPage.openMenuPage()
class ScrollableFrame(Frame):
    def __init__(self, _master, innerFrameHeight:int, innerFrameWidth:int=None, group=None):
        self._hasReturnedMaster = False
        self._outerFrame = Frame(_master, group)
        super().__init__(self._outerFrame, group)
        self._shiftState = State()
        self._getTkMaster().bind(self._shiftState.set, EventType.SHIFT_LEFT_DOWN)
        self._getTkMaster().bind(self._shiftState.unset, EventType.SHIFT_LEFT_UP)
        self._enterState = State()
        self._outerFrame.bind(self._enterState.set, EventType.ENTER)
        self._outerFrame.bind(self._enterState.unset, EventType.LEAVE)
        self._outerFrame.bind(self._updatePlace, EventType.CUSTOM_RELATIVE_UPDATE)
        self._scrollBarY = ScrollBar(self._outerFrame, False, group)
        self._scrollBarX = ScrollBar(self._outerFrame, False, group).setOrientation(Orient.HORIZONTAL)
        self._square = Label(self._outerFrame, group)
        self._getTkMaster().bind(self._onScroll, EventType.WHEEL_MOTION)
        self._innerFrameHeight = innerFrameHeight
        self._innerFrameWidth = innerFrameWidth
        self._currentYPos = 0
        self._currentXPos = 0
        self._currentSize = None
        self._scrollSpeed = 25
        self._scrollbarVisible = [True, True]
    def setInnerFrameHeight(self, height:int):
        self._innerFrameHeight = height
        return self
    def setInnerFrameWidth(self, width: int):
        self._innerFrameWidth = width
        return self
    def getOuterFrame(self)->Frame:
        return self._outerFrame
    def place(self, x=None, y=None, width=None, height=None, anchor:Anchor=Anchor.UP_LEFT):
        assert width > 25, f"This size is too small for inner Frame! width:{width}"
        self._currentSize = [width, height, (width if self._innerFrameWidth is None else self._innerFrameWidth), self._innerFrameHeight]
        self._scrollBarY.place(width-20, 0, 20, height-20)
        self._scrollBarX.place(0, height-20, width, 20)
        super()._get().place(x=0, y=self._currentYPos, width=(width-20 if self._innerFrameWidth is None else self._innerFrameWidth), height=self._innerFrameHeight)
        self._outerFrame.place(x, y, width, height, anchor)
        self._updateScrollBar()
    def placeRelative(self, fixX:int=None, fixY:int=None, fixWidth:int=None, fixHeight:int=None, xOffset=0, yOffset=0, xOffsetLeft=0, xOffsetRight=0, yOffsetUp=0, yOffsetDown=0, stickRight=False, stickDown=False, centerY=False, centerX=False, changeX=0, changeY=0, changeWidth=0, changeHeight=0, nextTo=None, updateOnResize=True):
        self._outerFrame.placeRelative(fixX, fixY, fixWidth, fixHeight, xOffset, yOffset, xOffsetLeft, xOffsetRight, yOffsetUp, yOffsetDown, stickRight, stickDown, centerY, centerX, changeX, changeY, changeWidth, changeHeight, nextTo, updateOnResize)
        return self
    def _updateScrollBar(self):
        if self._currentSize is None: return
        oWidth, oHeight, iWidth, iHeight = self._currentSize
        iHeight = oHeight if oHeight > iHeight else iHeight
        self._scrollbarVisible = [
            oWidth < iWidth,
            oHeight < iHeight
        ]
        if oHeight < iHeight:
            sHeightY = oHeight / iHeight
            try: sStartY = _map(abs(self._currentYPos), 0, abs(oHeight-iHeight), 0, 100-sHeightY*100)/100
            except ZeroDivisionError as e:
                print(format_exc(), f"{abs(oHeight-iHeight)=}")
                return
            self._scrollBarY.set(sStartY, sStartY + sHeightY)
        else:
            self._scrollBarY.placeForget()
        iWidth = oWidth if oWidth > iWidth else iWidth
        if oWidth < iWidth:
            sWidthX = oWidth / iWidth
            try: sStartX = _map(abs(self._currentXPos), 0, abs(oWidth-iWidth), 0, 100-sWidthX*100)/100
            except ZeroDivisionError as e:
                print(format_exc(), f"{abs(oWidth-iWidth)=}")
                return
            self._scrollBarX.set(sStartX, sStartX+sWidthX)
        else:
            self._scrollBarX.placeForget()
    def _updatePlace(self, iY=None):
        if type(iY) == Event:
            x, y, w, h = iY.getValue()
            if self._currentSize is not None:
                diffY = h - self._currentSize[1]
                if diffY > 0:
                    if self._currentYPos+diffY < 0:
                        self._currentYPos += diffY
                    else:
                        self._currentYPos = 0
                diffX = w - self._currentSize[0]
                if diffX > 0:
                    if self._currentXPos + diffX < 0:
                        self._currentXPos += diffX
                    else:
                        self._currentXPos = 0

            self._currentSize = [w, h, (w if self._innerFrameWidth is None else self._innerFrameWidth), self._innerFrameHeight]
            oWidth, oHeight, iWidth, iHeight = self._currentSize
            if oHeight < iHeight:
                self._scrollBarY.place(w-20, 0, 20, h-20)
            if oWidth < iWidth:
                self._scrollBarX.place(0, h-20, w-20, 20)
            self._updateScrollBar()
            if any(self._scrollbarVisible):
                self._square.place(w-20, h-20, 20, 20)
            else:
                self._square.placeForget()
        oWidth, oHeight, iWidth, iHeight = self._currentSize
        super()._get().place(x=self._currentXPos, y=self._currentYPos, width=(iWidth-20 if self._innerFrameWidth is None else self._innerFrameWidth), height=self._innerFrameHeight)
    def _onScroll(self, e:Event):
        if not self._enterState: return
        if self._currentSize is None: return
        oWidth, oHeight, iWidth, iHeight = self._currentSize
        delta = e.getScrollDelta()
        if not self._shiftState:
            if iHeight < oHeight: return
            if delta < 0: #down
                if self._currentYPos >= oHeight-iHeight-(20 if self._scrollbarVisible[0] else 0):
                    self._currentYPos -= self._scrollSpeed
                if self._currentYPos-self._scrollSpeed < oHeight-iHeight-(20 if self._scrollbarVisible[0] else 0):
                    self._currentYPos = oHeight-iHeight-(20 if self._scrollbarVisible[0] else 0)
            else: # up
                if self._currentYPos <= 0:
                    self._currentYPos += self._scrollSpeed
                if self._currentYPos+self._scrollSpeed > 0:
                    self._currentYPos = 0
        else:
            if iWidth < oWidth: return
            if delta < 0: # left
                if self._currentXPos >= oWidth-iWidth-(20 if self._scrollbarVisible[1] else 0):
                    self._currentXPos -= self._scrollSpeed
                if self._currentXPos-self._scrollSpeed < oWidth-iWidth-(20 if self._scrollbarVisible[1] else 0):
                    self._currentXPos = oWidth-iWidth-(20 if self._scrollbarVisible[1] else 0)
            else: # right
                if self._currentXPos <= 0:
                    self._currentXPos += self._scrollSpeed
                if self._currentXPos+self._scrollSpeed > 0:
                    self._currentXPos = 0
        self._updateScrollBar()
        self._updatePlace()
    def _get(self):
        """
        Returns outer frame instance once.
        Returns inner frame instance.
        """
        if self._hasReturnedMaster:
            self._hasReturnedMaster = False
            return self._outerFrame._get()
        return super()._get()

