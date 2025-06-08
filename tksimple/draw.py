import tkinter as _tk
from random import randint as _randint
from typing import Union

from .widget import Widget
from .util import _isinstance
from .event import _EventHandler, _EventRegistry
from .const import TKExceptions, EventType, Key, Mouse, Color, FontType
from .tkmath import Location2D
from .image import TkImage, PILImage

class Canvas(Widget):
    def __init__(self, _master, group=None):
        if _isinstance(_master, "Tk", "NotebookTab", "Frame", "LabelFrame") or isinstance(_master, Canvas):
            self._data = {"master": _master, "widget": _tk.Canvas(_master._get()), "canObjs":{}}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def clear(self):
        for i in list(self["canObjs"].values()).copy():
            i.destroy()
class CanvasObject:
    def __init__(self, _ins, _data, group):
        if group is not None:
            group.add(_ins)
        self._ins = _ins
        self._data = _data
        self.draw = self.render
        if not list(self._data.keys()).__contains__("id"):
            self._data["loc1"] = None
            self._data["loc2"] = None
            self._data["width"] = None
            self._data["height"] = None
            self._data["id"] = "".join([str(_randint(0,9)) for _ in range(15)])
            self._data["master"]["canObjs"][self._ins["id"]] = self._ins
            self._data["registry"] = _EventRegistry(self)
    def __getitem__(self, item):
        return self._data[item]
    def __setitem__(self, key, value):
        self._data[key] = value
    def bind(self, func, event: Union[EventType, Key, Mouse], args:list=None, priority:int=0, defaultArgs=False, disableArgs=False):
        if event == "CANCEL": return
        assert self["objID"] is not None, "Render canvasObj before binding!"
        _EventHandler._registerNewTagBind(self, self["objID"], func, event, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs)
    def render(self, updatePos=False):
        assert self["loc1"] is not None, "Location must be defined use .setLocation()!"
        assert self["loc2"] is not None or (self["width"] is not None and self["height"] is not None), "Location2 or width and height must be defined!"
        if updatePos and self["objID"] is not None:
            self["master"]._get().coords(
                self["objID"],
                ((self["loc1"].getX(), self["loc1"].getY(), self["loc1"].getX() + self["width"], self["loc1"].getY() + self["height"])
                 if self["loc2"] is None else
                 (self["loc1"].getX(), self["loc1"].getY(), self["loc2"].getX(), self["loc2"].getY()))
            )

        else:
            self.destroy()
            if self["loc2"] is None:
                self["objID"] = self["master"]._get()._create(self["type"], args=(self["loc1"].getX(), self["loc1"].getY(), self["loc1"].getX()+self["width"], self["loc1"].getY()+self["height"]), kw=self["_data"])
            else:
                self["objID"] = self["master"]._get()._create(self["type"], args=(self["loc1"].getX(), self["loc1"].getY(), self["loc2"].getX(), self["loc2"].getY()), kw=self["_data"])
            self._data["master"]["canObjs"][self._ins["id"]] = self._ins
        return self
    def setLocation(self, loc:Location2D):
        self["loc1"] = loc.clone()
        return self
    def setSecondLoc(self, loc:Location2D):
        self["loc2"] = loc.clone()
        return self
    def setWidth(self, w:int):
        self["width"] = int(w)
        return self
    def setHeight(self, l:int):
        self["height"] = int(l)
        return self
    def setBg(self, col: Union[Color, str]):
        self["_data"]["fill"] = col.value if hasattr(col, "value") else col
        return self
    def setOutlineThickness(self, i:int):
        self["_data"]["width"] = i
        return self
    def setOutlineColor(self, col: Union[Color, str]):
        self["_data"]["outline"] = col.value if hasattr(col, "value") else col
        return self
    def setAnchor(self, anchor):
        self["_data"]["anchor"] = anchor.value if hasattr(anchor, "value") else anchor
    def clone(self):
        _data = self._data.copy()
        _data["objID"] = None
        return self._ins.__class__(_data)
    def destroy(self):
        if self._data["objID"] is not None and self._ins["id"] in self["master"]["canObjs"]:
            #self["registry"].unregisterAll()
            self["master"]["canObjs"].pop(self._ins["id"])
            self["master"]._get().delete(self["objID"])
            self["objID"] = None
    def _get(self):
        return self._data["master"]._get()
class CanvasImage(CanvasObject):
    def __init__(self, _master=None, group=None):
        if isinstance(_master, Canvas):
            self._data = {"master": _master, "objID":None, "widget":None, "type":"image", "image":None, "_data":{"anchor":"nw"}}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + " instance or Canvas not: " + str(_master.__class__.__name__))
        super().__init__(self, self._data, group)

    def setImage(self, i:Union[TkImage, PILImage]):
        self["_data"]["image"] = i._get()
        return self
    def render(self, updatePos=False):
        if updatePos and self["objID"] is not None:
            self["master"]._get().coords(
                self["objID"],
                ((self["loc1"].getX(), self["loc1"].getY(), self["loc1"].getX() + self["width"],
                  self["loc1"].getY() + self["height"])
                 if self["loc2"] is None else
                 (self["loc1"].getX(), self["loc1"].getY(), self["loc2"].getX(), self["loc2"].getY()))
            )
        else:
            self.destroy()
            self["objID"] = self["master"]._get()._create(self["type"], (self["loc1"].getX(), self["loc1"].getY()), self["_data"])
            self._data["master"]["canObjs"][self["id"]] = self
        return self
class CanvasRect(CanvasObject):
    def __init__(self, _master=None, group=None):
        if isinstance(_master, Canvas):
            self._data = {"master": _master, "objID":None, "widget":None, "type":"rectangle", "_data":{}}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + " instance or Canvas not: " + str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
class CanvasCircle(CanvasObject):
    def __init__(self, _master=None, group=None):
        if isinstance(_master, Canvas):
            self._data = {"master": _master, "objID":None, "widget":None, "type":"oval", "_data":{}}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + " instance or Canvas not: " + str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def placeCenterWithRadius(self, loc:Location2D, r:int):
        loc = loc.clone()
        self.setLocation(loc.change(x=-r, y=-r))
        self.setWidth(r*2)
        self.setHeight(r*2)
        return self
class CanvasLine(CanvasObject):
    def __init__(self, _master=None, group=None):
        if isinstance(_master, Canvas):
            self._data = {"master": _master, "objID":None, "widget":None, "type":"line", "_data":{}}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + " instance or Canvas not: " + str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def placeByDegree(self, loc:Location2D, d:int, length:int):
        import math
        x = loc.getX()+math.cos(math.radians(d)) * length
        y = loc.getY()+math.sin(math.radians(d)) * length
        self.setLocation(loc)
        self.setSecondLoc(Location2D(x, y))
        return self
class CanvasText(CanvasObject):
    def __init__(self, _master=None, group=None):
        if isinstance(_master, Canvas):
            self._data = {"master": _master, "objID":None, "widget":None, "type":"text", "data":{}}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + " instance or Canvas not: " + str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def setText(self, text):
        self["data"]["text"] = str(text)
        return self
    def setFont(self, size, art=FontType.ARIAL):
        self["data"]["font"] = (art.value if hasattr(art, "value") else art, size)
        return self
    def render(self, updatePos=False):
        if "loc2" not in list(self._data.keys()):
            self["objID"] = self["master"]._get()._create(self["type"], args=(self["loc1"].getX(), self["loc1"].getY()), kw=self["data"])
        else:
            self["objID"] = self["master"]._get()._create(self["type"], args=(self["loc1"].getX(), self["loc1"].getY()), kw=self["data"])
        return self
    def setTextAngle(self, a):
        self["data"]["angle"] = int(a)
        return self