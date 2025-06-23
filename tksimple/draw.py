import tkinter as _tk
from typing import Union

from .widget import _Widget, NotebookTab, Frame, LabelFrame
from .util import _isinstanceAny, remEnum
from .event import _EventHandler, _EventRegistry
from .const import TKExceptions, EventType, Key, Mouse, Color, FontType
from .tkmath import Location2D
from .image import TkImage, PILImage
from .window import Tk


class Canvas(_Widget):
    def __init__(self, _master, group=None):
        if not _isinstanceAny(_master, Tk, NotebookTab, Canvas, Frame, LabelFrame):
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + ", Frame or Tk instance not: " + str(_master.__class__.__name__))

        self._canvasObjects = []

        super().__init__(child=self,
                         widget=_tk.Canvas(_master._get()),
                         master=_master,
                         group=group)
        
    def clear(self):
        for i in self._canvasObjects:
            i.destroy()
class CanvasObject:
    def __init__(self, child, _type, master, group):
        if group is not None:
            group.add(child)
        self._child = child
        
        self._type = _type
        self._loc1 = None
        self._loc2 = None
        self._width = None
        self._height = None
        self._canvasObjectID = None
        self._master = master # canvas
        
        self._objectConfig = {}

        self._eventRegistry = _EventRegistry(self)

        self._master._canvasObjects.append(self)
    def bind(self, func, event: Union[EventType, Key, Mouse], args:list=None, priority:int=0, defaultArgs=False, disableArgs=False):
        assert self._canvasObjectID is not None, "Render canvasObj before binding!"
        _EventHandler._registerNewTagBind(self, self._canvasObjectID, func, event, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs)
    def render(self):
        assert self._loc1 is not None, "Location must be defined use .setLocation()!"
        assert self._loc2 is not None or (self._width is not None and self._height is not None), "Location2 or width and height must be defined!"
        if self._canvasObjectID is not None:
            self._master._get().coords(
                self._canvasObjectID,
                ((self._loc1.getX(), self._loc1.getY(), self._loc1.getX() + self._width, self._loc1.getY() + self._height)
                 if self._loc2 is None else
                 (self._loc1.getX(), self._loc1.getY(), self._loc2.getX(), self._loc2.getY()))
            )
            self._master._get().itemconfigure(self._canvasObjectID, self._objectConfig)
        else:
            if self._loc2 is None:
                self._canvasObjectID = self._master._get()._create(self._type, args=(self._loc1.getX(), self._loc1.getY(), self._loc1.getX()+self._width, self._loc1.getY()+self._height), kw=self._objectConfig)
            else:
                self._canvasObjectID = self._master._get()._create(self._type, args=(self._loc1.getX(), self._loc1.getY(), self._loc2.getX(), self._loc2.getY()), kw=self._objectConfig)
        return self
    def setLocation(self, loc:Location2D):
        self._loc1 = loc
        return self
    def setSecondLoc(self, loc:Location2D):
        self._loc2 = loc
        return self
    def setWidth(self, w:int):
        self._width = int(w)
        return self
    def setHeight(self, h:int):
        self._height = int(h)
        return self
    def setBg(self, col: Union[Color, str]):
        self._objectConfig["fill"] = remEnum(col)
        return self
    def setOutlineThickness(self, i:int):
        self._objectConfig["width"] = i
        return self
    def setOutlineColor(self, col: Union[Color, str]):
        self._objectConfig["outline"] = remEnum(col)
        return self
    def setAnchor(self, anchor):
        self._objectConfig["anchor"] = remEnum(anchor)
    def clone(self):
        clazz = self._child.__class__(self._master)
        clazz._loc1 = self._loc1
        clazz._loc2 = self._loc2
        clazz._width = self._width
        clazz._height = self._height
        clazz._canvasObjectID = None
        clazz._objectConfig = self._objectConfig.copy()
        return clazz
    def destroy(self):
        if self._canvasObjectID is not None:
            self._master._canvasObjects.pop(self)
            self._master._get().delete(self._canvasObjectID)
            self._canvasObjectID = None
class CanvasImage(CanvasObject):
    def __init__(self, _master, group=None):
        if not isinstance(_master, Canvas):
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + " instance or Canvas not: " + str(_master.__class__.__name__))

        super().__init__(child=self,
                         _type="image",
                         master=_master,
                         group=group)

    def setImage(self, i:Union[TkImage, PILImage]):
        self._objectConfig["image"] = i._get()
        return self
class CanvasRect(CanvasObject):
    def __init__(self, _master, group=None):
        if not isinstance(_master, Canvas):
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + " instance or Canvas not: " + str(_master.__class__.__name__))

        super().__init__(child=self,
                         _type="rectangle",
                         master=_master,
                         group=group)
class CanvasCircle(CanvasObject):
    def __init__(self, _master, group=None):
        if not isinstance(_master, Canvas):
            raise TKExceptions.InvalidWidgetTypeException(
                "_master must be " + str(self.__class__.__name__) + " instance or Canvas not: " + str(
                    _master.__class__.__name__))

        super().__init__(child=self,
                         _type="oval",
                         master=_master,
                         group=group)
    def placeCenterWithRadius(self, loc:Location2D, r:int):
        loc = loc.clone()
        self.setLocation(loc.change(x=-r, y=-r))
        self.setWidth(r*2)
        self.setHeight(r*2)
        return self
class CanvasLine(CanvasObject):
    def __init__(self, _master=None, group=None):
        if not isinstance(_master, Canvas):
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + " instance or Canvas not: " + str(_master.__class__.__name__))

        super().__init__(child=self,
                         _type="line",
                         master=_master,
                         group=group)
    def placeByDegree(self, loc:Location2D, d:int, length:int):
        import math
        x = loc.getX()+math.cos(math.radians(d)) * length
        y = loc.getY()+math.sin(math.radians(d)) * length
        self.setLocation(loc)
        self.setSecondLoc(Location2D(x, y))
        return self
class CanvasText(CanvasObject):
    def __init__(self, _master=None, group=None):
        if not isinstance(_master, Canvas):
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + " instance or Canvas not: " + str(_master.__class__.__name__))

        super().__init__(child=self,
                         _type="text",
                         master=_master,
                         group=group)
    def setText(self, text):
        self._objectConfig["text"] = str(text)
        return self
    def setFont(self, size, art=FontType.ARIAL):
        self._objectConfig["font"] = (art.value if hasattr(art, "value") else art, size)
        return self
    def setTextAngle(self, a):
        self._objectConfig["angle"] = int(a)
        return self