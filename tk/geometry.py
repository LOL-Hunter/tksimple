
class _Errors:
    class NoneTypeLocationError(Exception):
        pass
    class LocationConvertError(Exception):
        pass

class Location2D:
    def __init__(self, *args, **kwargs):
        self.copy = self.clone
        if len(args) == 0 and len(kwargs.values()) == 0:
            self._coords = {"x":0, "y":0}
        elif len(args) == 0:
            self._coords = kwargs
        else:
            if len(args) == 2:
                self._coords = {"x":args[0], "y":args[1]}
            else:
                args = args[0]
                if isinstance(args, Location2D):
                    self._coords = args._coords.copy()
                elif args is None:
                    raise _Errors.NoneTypeLocationError("Location is None.")
                elif type(args) == tuple and len(args) > 1:
                    self._coords = {"x": args[0], "y": args[1]} # ((1, 2), )
                else:
                    raise _Errors.LocationConvertError("Cold not convert to Location:\n\t"+"Type: "+str(type(args))+"\n\tStr: "+str(args))
    def __getitem__(self, item):
        if isinstance(item, int):
            item = ["x", "y"][item]
        return self._coords[item]
    def __setitem__(self, key, value):
        self._coords[key] = value
    def __eq__(self, other):
        if isinstance(other, Location2D):
            return other.get() == self.get()
        elif isinstance(other, tuple):
            return other == self.get()
        else:
            return False
    def __ne__(self, other):
        if isinstance(other, Location2D):
            return other.get() != self.get()
        elif isinstance(other, tuple):
            return other != self.get()
        else:
            return True
    def __add__(self, other):
        return Location2D(self.getX()+other.getX(), self.getY()+other.getY())
    def __repr__(self):
        return "Location2D("+str(self["x"])+", "+str(self["y"])+")"
    def __len__(self):
        return 2
    def toInt(self):
        self._coords["x"] = int(self._coords["x"])
        self._coords["y"] = int(self._coords["y"])
        return self
    @property
    def x(self):
        return self.getX()
    @x.setter
    def x(self, x):
        self.setX(x)
    @property
    def y(self):
        return self.getY()
    @y.setter
    def y(self, y):
        self.setY(y)
    def getX(self):
        return self._coords["x"]
    def getY(self):
        return self._coords["y"]
    def setX(self, x):
        self._coords["x"] = x
        return self
    def setY(self, y):
        self._coords["y"] = y
        return self
    def change(self, x=0.0, y=0.0):
        if isinstance(x, Location2D): x, y = x.get()
        self._coords["x"] = self.getX() + x
        self._coords["y"] = self.getY() + y
        return self
    def get(self):
        return tuple(self._coords.values())
    def set(self, *L):
        if len(L) == 1:
            L = L[0]
        if isinstance(L, Location2D):
            x, y = L.get()
        else:
            x, y = L
        self._coords["x"] = x
        self._coords["y"] = y
    def clone(self):
        return Location2D(x=self.getX(), y=self.getY())
    def toString(self, prefix=True):
        if prefix:
            return "X: "+str(self.getX())+"Y: "+str(self.getY())
        else:
            return str(self.getX()) + str(self.getY())
class Location3D:
    def __init__(self, *args, **kwargs):
        self.copy = self.clone
        if len(args) == 0 and len(kwargs.values()) == 0:
            self._coords = {"x":0, "y":0, "z":0}
        elif len(args) == 0:
            self._coords = kwargs
        else:
            if len(args) != 1:
                self._coords = {"x":args[0], "y":args[1], "z":args[2]}
            else:
                if isinstance(args[0], Location3D):
                    self._coords = args[0]._coords.copy()
                elif args[0] is None:
                    raise _Errors.NoneTypeLocationError("None Type Location3D")
                else:
                    self._coords = {"x": args[0][0], "y": args[0][1], "z": args[0][2]}
    def __getitem__(self, item):
        if isinstance(item, int):
            item = ["x", "y", "z"][item]
        return self._coords[item]
    def __setitem__(self, key, value):
        self._coords[key] = value
    def __eq__(self, other):
        if isinstance(other, Location3D):
            return other.get() == self.get()
        elif isinstance(other, tuple):
            return other == self.get()
    def __ne__(self, other):
        if isinstance(other, Location3D):
            return other.get() != self.get()
        elif isinstance(other, tuple):
            return other != self.get()
    def __repr__(self):
        return "Location2D("+str(self["x"])+", "+str(self["y"])+", "+str(self["z"])+")"
    def __len__(self):
        return 2
    def toInt(self):
        self._coords["x"] = int(round(self.getX()))
        self._coords["y"] = int(round(self.getY()))
        self._coords["z"] = int(round(self.getZ()))
        return self
    def getX(self):
        return self._coords["x"]
    def getY(self):
        return self._coords["y"]
    def getZ(self):
        return self._coords["z"]
    def setX(self, x):
        self._coords["x"] = x
        return self
    def setY(self, y):
        self._coords["y"] = y
        return self
    def setZ(self, z):
        self._coords["z"] = z
        return self
    @property
    def x(self):
        return self.getX()
    @x.setter
    def x(self, x):
        self.setX(x)
    @property
    def y(self):
        return self.getY()
    @y.setter
    def y(self, y):
        self.setY(y)
    @property
    def z(self):
        return self.getZ()
    @z.setter
    def z(self, z):
        self.setZ(z)
    def change(self, x=0.0, y=0.0, z=0.0):
        if isinstance(x, Location3D): x, y, z = x.get()
        self._coords["x"] = self.getX() + x
        self._coords["y"] = self.getY() + y
        self._coords["z"] = self.getZ() + z
        return self
    def get(self):
        return tuple(self._coords.values())
    def set(self, *L):
        if len(L) == 1:
            L = L[0]
        if isinstance(L, Location3D):
            x, y, z = L.get()
        else:
            x, y, z = L

        self._coords["x"] = x
        self._coords["y"] = y
        self._coords["z"] = z
    def clone(self):
        return Location3D(x=self.getX(), y=self.getY(), z=self.getZ())
    def toString(self, prefix=True):
        if prefix:
            return "X: "+str(self.getX())+"Y: "+str(self.getY())+"Z: "+str(self.getZ())
        else:
            return str(self.getX()) + str(self.getY()) + str(self.getZ())
class Rect:
    def __init__(self, loc1, loc2):
        self.ratio = None
        self.loc1 = loc1
        self.loc2 = loc2
    @staticmethod
    def fromLocLoc(loc1:Location2D, loc2:Location2D):
        return Rect(loc1, loc2)
    @staticmethod
    def fromLocWidthHeight(loc:Location2D, width:int|float=0, height:int|float=0):
        return Rect(loc, loc.clone().change(x=width, y=height))
    """@staticmethod
    def fromTkWidget(w):
        return Rect(w.)"""
    def __repr__(self):
        return "Rect("+str(self.loc1)+", "+str(self.loc2)+")"
    @property
    def width(self):
        return self.getWidth()
    @property
    def height(self):
        return self.getHeight()
    @property
    def size(self):
        return self.getWidth(), self.getHeight()
    def clone(self):
        return Rect(self.loc1.clone(), self.loc2.clone())
    def getLoc1(self):
        return Location2D(min(self.loc1.getX(), self.loc2.getX()),  min(self.loc1.getY(), self.loc2.getY()))
    def getWidth(self):
        return max(self.loc1.getX(), self.loc2.getX()) - min(self.loc1.getX(), self.loc2.getX())
    def getHeight(self):
        return max(self.loc1.getY(), self.loc2.getY()) - min(self.loc1.getY(), self.loc2.getY())
    def collisionWithPoint(self, loc):
        return loc.getX() >= min(self.loc1.getX(), self.loc2.getX()) and loc.getX() <= max(self.loc1.getX(), self.loc2.getX()) and loc.getY() >= min(self.loc1.getY(), self.loc2.getY()) and loc.getY() <= max(self.loc1.getY(), self.loc2.getY())
    def collisionWithRect(self, rect):
        rect2 = Rect(Location2D(rect.loc1.getX()-self.getWidth(), rect.loc1.getY()-self.getHeight()), Location2D(rect.loc1.getX()+rect.getWidth(), rect.loc1.getY()+rect.getHeight()))
        return rect2.collisionWithPoint(self.loc1)
    def resizeToRectWithRatio(self, rect, offset=0, updateRatio=False, upLeftFix=True):
        if updateRatio or self.ratio is None:
            self.ratio = self.getWidth()/self.getHeight()
        newWidth = rect.getWidth()-offset*2
        newHeight = (1/self.ratio) * newWidth
        if newHeight + offset*2 > rect.getHeight():
            newHeight = rect.getHeight() - offset*2
            newWidth = self.ratio * newHeight
        if upLeftFix:
            self.loc2 = Location2D(self.loc1.getX()+newWidth, self.loc1.getY()+newHeight)
        else:
            self.loc1 = Location2D(rect.loc1.getX()+offset, rect.loc1.getY()+offset)
            self.loc2 = Location2D(rect.loc1.getX()+newWidth, rect.loc1.getY()+newHeight)
class Circle:
    def __init__(self, loc:Location2D, radius:int):
        self._radius = radius
        self._centerLoc = loc
    @staticmethod
    def fromCenterRadius(loc:Location2D, radius:int):
        return Circle(loc, radius)
    @staticmethod
    def fromLocLoc(loc:Location2D, loc2:Location2D):
        x, y = loc.get()
        x1, y1 = loc2.get()
        w = max(x, x1) - min(x, x1)
        h = max(y, y1) - min(y, y1)
        assert w == h, "Width and Height are not equal!"
        return Circle(loc.change(x=w, y=w), w/2)
    def collisionWithPoint(self):
        pass
def _map(value, iMin, iMax, oMin=None, oMax=None):
    if oMin is None and oMax is None:
        oMax = iMax
        iMax = iMin
        iMin = 0
        oMin = 0
    return int((value-iMin) * (oMax-oMin) / (iMax-iMin) + oMin)

if __name__ == "__main__":
    l = Location2D()
    l.x= 1