import tkinter as _tk
import tkinter.dnd as _dnd
import tkinter.ttk as _ttk
from datetime import datetime as _date


from .widget import *
from .widget import _Widget
from .draw import Canvas
from .util import Font, State, _isinstanceAny
from .event import Event, _EventHandler
from .tkmath import _map

class HyperLinkLabel(Label):
    """
    Label for displaying URL.
    Clickable to open URL.
    """
    def __init__(self, master, group=None):
        super().__init__(master, group)
        self._hook = None
        self._hoverText = None
        self._hoverFont = None
        self._hoverColor = "black"
        self.bind(self._onEnter, EventType.ENTER)
        self.bind(self._onLeave, EventType.LEAVE)
        self.resetClickedColor()
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
        _EventHandler._registerNewEvent(self, func=self._openWebsite, eventType=EventType.LEFT_CLICK, priority=priority, args=args, disableArgs=disableArgs, defaultArgs=defaultArgs)
        return self
    def _openWebsite(self, *args):
        if self._hook is not None:
            self._hook(*args)
        self.setClickedColor()
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
class PDFViewer(_Widget):
    def __init__(self, _master, path, group=None):
        raise NotImplemented() # TODO implement
        from tkPDFViewer import tkPDFViewer as pdf

        if not _isinstanceAny(_master, Tk, NotebookTab, Canvas, Frame, LabelFrame):
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + ", Frame or Tk instance not: " + str(_master.__class__.__name__))

        super().__init__(child=self,
                         widget=viewer.pdf_view(_master._get(), 200, 200, path),
                         master=_master,
                         group=group)
        viewer = pdf.ShowPdf()
class MatPlotLibFigure(_Widget):
    """
    Widget:
    Use this widget to display plots from matplotlib library.

    Pass the Figure instance from matplotlib.
    """
    def __init__(self, _master, fig, group=None, toolBar=False):
        if not _isinstanceAny(_master, Tk, NotebookTab, Canvas, Frame, LabelFrame):
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + ", Frame or Tk instance not: " + str(_master.__class__.__name__))

        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

        self._frame = Frame(_master, group)

        self._figureWidget = FigureCanvasTkAgg(fig, self._frame._get())
        self._figureWidget.draw()

        if toolBar:
            toolbar = NavigationToolbar2Tk(self._figureWidget, self._frame._get(), pack_toolbar=False)
            toolbar.update()

            self.wwidget_plot = _Widget(child=None,
                                        widget=self._figureWidget.get_tk_widget(),
                                        master=self._frame,
                                        group=None)
            self.wwidget_settings = _Widget(child=None,
                                            widget=toolbar,
                                            master=self._frame,
                                            group=None)
            self.wwidget_plot.placeRelative(changeHeight=-30)
            self.wwidget_settings.placeRelative(stickDown=True, fixHeight=30)

        super().__init__(child=self,
                         widget=self._frame._get(),
                         master=_master,
                         group=group)
        self.bind(self._updatePlace, EventType.CUSTOM_RELATIVE_UPDATE)
    def _updatePlace(self, e):
        self.wwidget_plot.updateRelativePlace()
        self.wwidget_settings.updateRelativePlace()
    def draw(self):
        """
        Draws the figure.
        @return:
        """
        self._figureWidget.draw()
        return self
class Calendar(_Widget):
    """
    Widget:
    This widget displays a calendar to select day and year.

    To use this widget the 'tkcalencar' library have to be installed.
    """
    def __init__(self, _master, group=None):
        if not _isinstanceAny(_master, Tk, NotebookTab, Canvas, Frame, LabelFrame):
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + ", Frame or Tk instance not: " + str(_master.__class__.__name__))

        import tkcalendar as cal

        super().__init__(child=self,
                         widget=cal.Calendar(_master._get()),
                         master=_master,
                         group=group)
    def _decryptEvent(self, args, event):
        return self._widget.get_date()
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
        return self._widget.get_date()
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
class DropdownCalendar(_Widget):
    """
    Widget:
    This widget displays an Entry like folds out calendar to select day and year.

    To use this widget the 'tkcalencar' library have to be installed.
    """
    def __init__(self, _master, group=None):
        if not _isinstanceAny(_master, Tk, NotebookTab, Canvas, Frame, LabelFrame):
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + ", Frame or Tk instance not: " + str(_master.__class__.__name__))

        import tkcalendar as cal

        super().__init__(child=self,
                         widget=cal.DateEntry(_master._get()),
                         master=_master,
                         group=group)
    def _decryptEvent(self, args, event):
        return self._widget.get_date()
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
        return self._widget.get_date()
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
class OnOffButton(_Widget):
    """
    Widget:
    This is a custom Widget.
    This widget represents a Button wich can be toggled on and off.
    """
    def __init__(self, _master, group=None, default=False, colorsActive=True, reliefActive=False):
        if not _isinstanceAny(_master, Tk, NotebookTab, Canvas, Frame, LabelFrame):
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + ", Frame or Tk instance not: " + str(_master.__class__.__name__))

        self._value = default
        self._isRelief = reliefActive
        self._isColors = colorsActive
        self._onText = None

        init = {}

        if default:
            if colorsActive: init["bg"] = Color.GREEN.value
            if reliefActive: init["relief"] = Style.SUNKEN.value
        else:
            if colorsActive: init["bg"] = Color.RED.value
            if reliefActive: init["relief"] = Style.SUNKEN.value

        super().__init__(child=self,
                         widget=_tk.Button(_master._get()),
                         master=_master,
                         group=group,
                         init=init)
    def setValue(self, v:bool):
        """
        Set the state (on/off) as bool.
        @param v:
        @return:
        """
        self._value = bool(v)
        self._update()
        return self
    def getValue(self)->bool:
        """
        Returns the current state as boolean.

        @return:
        """
        return self._value
    def setOn(self):
        """
        Set state to True.
        @return:
        """
        self._value = True
        self._update()
        return self
    def setOff(self):
        """
        Set state to False.
        @return:
        """
        self._value = False
        self._update()
        return self
    def setOnText(self, text:Union[str, None]):
        """
        Set the text wich is displayed qh´´when state is True.
        @param text:
        @return:
        """
        self._onText = str(text)
        self._update()
        return self
    def setOffText(self, text:Union[str, None]):
        """
        Set the text wich is displayed qh´´when state is True.
        @param text:
        @return:
        """
        self._offText = str(text)
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
        self._command = _EventHandler._getNewEventRunnable(self, cmd, args, priority)
        _EventHandler._registerNewCommand(self, self._press, args, priority)
        self._update()
        return self
    def _press(self, e):
        self._value = not self._value
        self._update()
        func = self._command
        func["value"] = self._value
        if func is not None:
            func()
    def _update(self):
        if self._value:
            if self._onText is not None: self.setText(self._onText)
            if self._isColors: self.setBg(Color.GREEN)
            if self._isRelief: self.setStyle(Style.SUNKEN)
        else:
            if self._offText is not None: self.setText(self._offText)
            if self._isColors: self.setBg(Color.RED)
            if self._isRelief: self.setStyle(Style.RAISED)
        return self._value
class TextEntry(LabelFrame):
    """
    Widget:
    This is a Custom Widget.
    An Entry and a Label are combined.
    Used to give the user a hint, what to write in the Entry.
    Important: First set the Text and THEN place the widget.
    """
    def __init__(self, _master, group=None):
        if not _isinstanceAny(_master, Tk, NotebookTab, Canvas, Frame, LabelFrame):
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + ", Frame or Tk instance not: " + str(_master.__class__.__name__))
        
        super().__init__(_master, group)
        
        self._entry = Entry(self, group)
        self._label = Label(self, group)
    def updatePlace__(self):
        self._label._get().grid(row=0, column=0)
        self._entry._get().grid(row=0, column=1, sticky=Anchor.RIGHT.value)
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
        return self._entry
    def getLabel(self)->Label:
        """
        Returns the sub Label.
        Used for further configuration.
        @return:
        """
        return self._label
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
        self._label.place(0, 0)
        labelWidth = self._label.getWidth()
        if entryStartX is not None: labelWidth = entryStartX
        if width is None:
            width = labelWidth+100
            entryWidth = 100
        else:
            entryWidth = width - labelWidth
        super().place(x, y, width, height)
        self._label.place(0, 0, labelWidth, height-offset)
        self._entry.place(labelWidth, 0, entryWidth-offset, height-offset)
        return self
    def placeRelative(self, fixX=None, fixY=None, fixWidth=None, fixHeight=None, xOffset=0, yOffset=0, xOffsetLeft=0, xOffsetRight=0, yOffsetUp=0, yOffsetDown=0, stickRight=False, stickDown=False, centerY=False, centerX=False, center=False, changeX=0, changeY=0, changeWidth=0, changeHeight=0):
        assert fixWidth is not None and fixHeight is not None, "fixWidth and fixHeight must be defined!"
        x = fixX if fixX is not None else 0
        y = fixY if fixY is not None else 0
        self.place(x, y, fixWidth, fixHeight)
        super().placeRelative(fixX, fixY, fixWidth, fixHeight, xOffset, yOffset, xOffsetLeft, xOffsetRight, yOffsetUp, yOffsetDown, stickRight, stickDown, centerY, centerX, center, changeX, changeY, changeWidth, changeHeight)
        return self
    def setFg(self, col:Union[Color, str]):
        self.getEntry().setFg(col)
        self.getLabel().setFg(col)
        return self
    def setBg(self, col:Union[Color, str]):
        self.getEntry().setBg(col)
        self.getLabel().setBg(col)
        return self
class TextDropdownMenu(LabelFrame):
    """
    Widget:
    This is a Custom Widget.
    DropdownMenu and Label combination.
    Used to give the user a hint, what to write/select in the DropdownMenu.
    Important: First set the Text and THEN place the widget.
    """
    def __init__(self, _master, group=None):
        if not _isinstanceAny(_master, Tk, NotebookTab, Canvas, Frame, LabelFrame):
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + ", Frame or Tk instance not: " + str(_master.__class__.__name__))

        super().__init__(_master, group)

        self._dropdown = DropdownMenu(self, group)
        self._label = Label(self, group)
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
    def setText(self, text:str):
        """
        Set the Label text.
        @param text:
        @return:
        """
        self.getLabel().setText(text)
        return self
    def getLabel(self)->Label:
        """
        Returns the sub Label.
        Used for further configuration.
        @return:
        """
        return self._label
    def getDropdownMenu(self)->DropdownMenu:
        """
        Returns the sub DropdownMenu.
        Used for further configuration.
        @return:
        """
        return self._dropdown
    def clear(self):
        self.getDropdownMenu().clear()
        return self
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
        self._label.place(0, 0)
        labelWidth = self._label.getWidth()
        if entryStartX is not None: labelWidth = entryStartX
        if width is None:
            width = labelWidth+100
            entryWidth = 100
        else:
            entryWidth = width - labelWidth
        super().place(x, y, width, height)
        self._label.place(0, 0, labelWidth, height-offset)
        self._dropdown.place(labelWidth, 0, entryWidth-offset, height-offset)
        return self
    def placeRelative(self, fixX=None, fixY=None, fixWidth=None, fixHeight=None, xOffset=0, yOffset=0, xOffsetLeft=0, xOffsetRight=0, yOffsetUp=0, yOffsetDown=0, stickRight=False, stickDown=False, centerY=False, centerX=False, center=False, changeX=0, changeY=0, changeWidth=0, changeHeight=0):
        assert fixWidth is not None and fixHeight is not None, "fixWidth and fixHeight must be defined!"
        x = fixX if fixX is not None else 0
        y = fixY if fixY is not None else 0
        self.place(x, y, fixWidth, fixHeight)
        super().placeRelative(fixX, fixY, fixWidth, fixHeight, xOffset, yOffset, xOffsetLeft, xOffsetRight, yOffsetUp, yOffsetDown, stickRight, stickDown, centerY, centerX, center, changeX, changeY, changeWidth, changeHeight)
        return self
    def setFg(self, col:Union[Color, str]):
        self.getDropdownMenu().setFg(col)
        self.getLabel().setFg(col)
        return self
    def setBg(self, col:Union[Color, str]):
        self.getDropdownMenu().setBg(col)
        self.getLabel().setBg(col)
        return self
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
        self._hideWidgetOnDrag = False
        self._dragEnabled = True
        # register "private" methods
        setattr(self, "dnd_accept", self._onDndWidget)
        setattr(self, "dnd_enter", self._onDndEnter)
        setattr(self, "dnd_motion", self._onDndMotion)
        setattr(self, "dnd_leave", self._onDndLeave)
        setattr(self, "dnd_commit", self._onDndCommit)
    def _onDndWidget(self, dndHandl, event):
        return self if self._dragEnabled else None
    def _onDndEnter(self, dndHandl, event):
        self.setFocus()
        rsx, rsy = dndHandl.getWidgetCursorPos(event, self)
        x1, y1, x2, y2 = dndHandl.canvas._get().bbox(dndHandl.id) # WICHTIG .id impl

        canvasRect = Rect(
            Location2D(x1, y1),
            Location2D(x2, y2)
        )
        self._outlineID = self._widget.create_rectangle(rsx, rsy, rsx+canvasRect.getWidth(), rsy+canvasRect.getHeight())
        self._onDndMotion(dndHandl, event)
    def _onDndMotion(self, dndHandl, event):
        if self._hideWidgetOnDrag: dndHandl.canvas._get().itemconfigure(dndHandl.id, state="hidden")
        rsx, rsy = dndHandl.getWidgetCursorPos(event, self)
        x1, y1, x2, y2 = self._widget.bbox(self._outlineID)  # WICHTIG .id impl
        self._widget.move(self._outlineID, rsx-x1, rsy-y1)
    def _onDndLeave(self, dndHandl, event):
        self._getTkMaster().setFocus()
        self._widget.delete(self._outlineID)
        self._widget.dnd_canvas = None
        self._outlineID = None
    def _onDndCommit(self, dndHandl, event):
        self._onDndLeave(dndHandl, event)
        rsx, rsy = dndHandl.getWidgetCursorPos(event, self)
        self.attachWidgetCreator(dndHandl.widget, rsx, rsy)
    def disableDrag(self):
        self._dragEnabled = False
    def enableDrag(self):
        self._dragEnabled = True
    def setWidgetHiddenWhileDrag(self, b:bool=True):
        self._hideWidgetOnDrag = bool(b)
        return self
    def attachWidget(self, widget:_Widget, x=0, y=0, width=None, height=None):
        """
        Attaches a widget to be dragged on this canvas.
        Only on this canvas. If multi-canvas dragging is needed use 'DndCanvas.attachWidgetCreator' method.
        """
        if hasattr(widget, "dnd_canvas"):
            setattr(widget, "dnd_canvas", None)
        if widget.dnd_canvas is None: # register
            _id = self._get().create_window(x, y, window=widget._get(), anchor="nw")
            widget._dnd_canvas = _DndHandler(self, _id, widget, None)
            widget.bind(widget._dnd_canvas.press, "<ButtonPress>", priority=10)
        else:
            widget.dnd_canvas.canvas._get().delete(widget.dnd_canvas.id)
            _id = self._get().create_window(x, y, width=width, height=height, window=widget._get(), anchor="nw")
            widget.dnd_canvas.id = _id
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
        if isinstance(widgetCreator, _Widget):
            _widget = widgetCreator
            widgetCreator = widgetCreator.dnd_canvas.widgetCreator
            self.detachWidget(_widget)
        widget = widgetCreator(self)
        # check and register variables
        if "dnd_canvas" not in widget._data.keys():
            widget.dnd_canvas = None
        # check if already registered to this canvas
        if widget.dnd_canvas is not None:
            if hash(widget.dnd_canvas.widget) == hash(self):
                return
            self.detachWidget(widget)
        _id = self._get().create_window(x, y, window=widget._get(), anchor="nw")
        widget.dnd_canvas = _DndHandler(self, _id, widget, widgetCreator)
        widget.bind(widget.dnd_canvas.press, "<ButtonPress>", priority=10)
    def detachWidget(self, widget:_Widget):
        if hasattr(widget, "dnd_canvas"):
            setattr(widget, "dnd_canvas", None)
        if widget.dnd_canvas is not None:
            widget.dnd_canvas.canvas._get().delete(widget.dnd_canvas.id)
            widget._eventRegistry.unregisterType("<ButtonPress>")
            widget._get().destroy()
class MenuPage(Frame):
    def __init__(self, master, group=None):
        super().__init__(master, group)
        self._master = self.getParentWindow()
        self._history = [self]
        self._active = False
    def __str__(self):
        return type(self).__name__
    def openMenuPage(self, **kwargs):
        # remove other active Page
        self._active = True
        self.onShow(**kwargs)
        self.getParentWindow().updateDynamicWidgets()
    def openNextMenuPage(self, mp, **kwargs):
        self._active = False
        self.onHide()
        self.placeForget()
        history = self._history.copy()
        history.append(mp)
        mp._history = history
        mp._active = True
        mp.onShow(**kwargs)
        self.getParentWindow().updateDynamicWidgets()
    def openLastMenuPage(self):
        self.onHide()
        self.placeForget()
        newHistory = self._history.copy()[:-1] # remove self
        history = newHistory[-1] # get new "self" -> last item
        history._history = newHistory # set hist to new instance
        history.onShow() # show new instance
        history._active = True
        self.getParentWindow().updateDynamicWidgets()
    def _onShow(self, **kwargs):
        self._active = True
        self.onShow(**kwargs)
    def isActive(self):
        return self._active
    def onShow(self, **kwargs):
        pass
    def onHide(self):
        pass
    def openHomePage(self, mainPage):
        assert isinstance(mainPage, MenuPage), "Please use 'MenuPage' instance!"
        mainPage._history = [mainPage]
        self.placeForget()
        mainPage.openMenuPage()
class ScrollableText(Text):
    def __init__(self, _master, group=None, readOnly=False):
        self._frame = Frame(_master)
        self._frame.setBg("red")
        self._scrollBar = ScrollBar(self._frame, autoPlace=False)
        self._scrollBar._get().pack(side=_tk.RIGHT, fill=_tk.Y)

        super().__init__(self._frame,
                         group=group,
                         readOnly=readOnly)

        self._get()["yscrollcommand"] = self._scrollBar.set
        self._get().pack(side=_tk.LEFT, fill=_tk.BOTH, expand=True)
        self._scrollBar._get()['command'] = self._get().yview
    def placeRelative(self, fixX:int=None, fixY:int=None, fixWidth:int=None, fixHeight:int=None, xOffset=0, yOffset=0, xOffsetLeft=0, xOffsetRight=0, yOffsetUp=0, yOffsetDown=0, stickRight=False, stickDown=False, centerY=False, centerX=False, center=False, changeX=0, changeY=0, changeWidth=0, changeHeight=0):
        self._frame.placeRelative(fixX, fixY, fixWidth, fixHeight, xOffset, yOffset, xOffsetLeft, xOffsetRight, yOffsetUp, yOffsetDown, stickRight, stickDown, centerY, centerX, center, changeX, changeY, changeWidth, changeHeight)
    def place(self, x=None, y=None, width=None, height=None, anchor:Anchor=Anchor.UP_LEFT):
        self._frame.place(x, y, width, height, anchor)
    def grid(self, row=0, column=0):
        self._frame.grid(row, column)
    def getScrollBar(self)->ScrollBar:
        return self._scrollBar
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
class ClosableNotebook():pass
