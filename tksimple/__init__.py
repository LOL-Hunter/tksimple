import os
import tkinter as _tk_
import tkinter.colorchooser as colorChooser
import tkinter.dnd as _dnd
import tkinter.filedialog as fd
import tkinter.font as _font
import tkinter.messagebox as msg
import tkinter.simpledialog as simd
import tkinter.ttk as ttk
from datetime import date
from enum import Enum
from random import randint, choice
from string import ascii_lowercase
from time import strftime, time, sleep
from traceback import format_exc
from typing import Union, Callable, Iterable, List

#TODO parameter description in __init__
#TODO parameter type in __init__
#TODO event value in bind
#TODO Remove pysettings.text package
#TODO write description
#TODO TextEntry.placeRelative implementation

WIDGET_DELETE_DEBUG = False
"""

Master-Classes:
Tk
Toplevel
Dialog

Widgets:

"""

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
                elif type(args) == tuple and len(args) > 1:
                    self._coords = {"x": args[0], "y": args[1]} # ((1, 2), )
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
def _map(value, iMin, iMax, oMin=None, oMax=None):
    if oMin is None and oMax is None:
        oMax = iMax
        iMax = iMin
        iMin = 0
        oMin = 0
    return int((value-iMin) * (oMax-oMin) / (iMax-iMin) + oMin)
class Rect:
    def __init__(self, loc1, loc2):
        self.ratio = None
        self.loc1 = loc1
        self.loc2 = loc2
    @staticmethod
    def fromLocLoc(loc1:Location2D, loc2:Location2D):
        return Rect(loc1, loc2)
    @staticmethod
    def fromLocWidthHeight(loc:Location2D, width:int | float=0, height:int | float=0):
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

class TKExceptions:
    class InvalidFileExtention(Exception):
        pass
    class PathNotExisits(Exception):
        pass
    class InvalidUsageException(Exception):
        pass
    class InvalidHeaderException(Exception):
        pass
    class InvalidWidgetTypeException(Exception):
        pass
    class EventExecutorException(Exception):
        pass
    class BindException(Exception):
        pass
class Symbol:
    """
    Example Symbol collection.
    """
    #TODO: add more symbol-codes
    DICE_1 = "\u2680"
    DICE_2 = "\u2681"
    DICE_3 = "\u2682"
    DICE_4 = "\u2683"
    DICE_5 = "\u2684"
    DICE_6 = "\u2685"
class FontType(Enum):
    """
    FontTypes enum
    """
    #TODO: add more font types
    ARIAL ="arial"
class Orient(Enum):
    """
    Enum to specify the Orientation
    """
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
class Style(Enum):
    """
    Enum to specify widget style.
    """
    FLAT = "flat"
    SOLID = "solid"
    RAISED = "raised"
    SUNKEN = "sunken"
    GROOVE = "groove"
    RIDGE = "ridge"
class Anchor(Enum):
    """
    Enum to specify the Anchor.
    """
    NW = UP_LEFT = "nw"
    NE = UP_RIGHT = "ne"
    SW = DOWN_LEFT = "sw"
    SE = DOWN_RIGHT = "se"
    CENTER = MIDDLE = "center"
    N = UP = "n"
    E = RIGHT = "e"
    S = DOWN = "s"
    W = LEFT = "w"
class Direction(Enum):
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"
    NONE = "none"
    TOP = "top"
    BOTTOM = "bottom"
class Color(Enum):
    DEFAULT = "#F0F0F0"
    WHITE = "white"
    BLACK = "black"
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    CYAN = "cyan"
    YELLOW = "yellow"
    MAGENTA = "magenta"
    ORANGE = "#CB772F"
    @staticmethod
    def rgb(r:int, g:int, b:int):
        return '#%02x%02x%02x' % (r, g, b)
    @staticmethod
    def hex(hex_:str):
        return hex_
class Wrap(Enum):
    NONE = "none"
    WORD = "word"
    CHAR = "char"
class Cursor(Enum):
    NONE = "none"
    WIN_DEFAULT = "arrow"
    WIN_TURN = "exchange"
    WIN_FOUR_ARROW = "fleur"
    WIN_TWO_ARROW_HORIZONTAL = "sb_h_double_arrow"
    WIN_TWO_ARROW_VERTICAL = "sb_v_double_arrow"
    WIN_TWO_ARROW_DIAGONAL = "size_nw_se"
    WIN_TWO_ARROW_DIAGONAL_INVERTED = "size_ne_sw"
    WIN_LOADING = "watch"
    WIN_CROSS = "tcross"
    WIN_CLICK_HAND = "hand2"
    WIN_MARK_TEXT = "xterm"

    SHAPE_CIRCLE = "circle"
    SHAPE_CROSS = "cross"
    SHAPE_DOTBOX = "dotbox"
    SHAPE_PLUS = "plus"

    CUSTOM_CLOCK = "clock"
    CUSTOM_HEART = "heart"
    CUSTOM_MAN = "man"
    CUSTOM_MOUSE = "mouse"
    CUSTOM_PIRATE = "pirate"
    CUSTOM_SHUTTLE = "shuttle"
    CUSTOM_SIZING = "sizing"
    CUSTOM_SPIDER = "spider"
    CUSTOM_SPRAYCAN = "spraycan"
    CUSTOM_STAR = "star"
    CUSTOM_TARGET = "target"
    CUSTOM_TRECK = "trek"

class Key(Enum):
    SHIFT = "<Shift>"
    RETURN = "<Return>"
    DOWN = "<Down>"
    RIGHT = "<Right>"
    LEFT = "<Left>"
    UP = "<Up>"
class Mouse(Enum):
    MOUSE_MOTION = "<Motion>"
    WHEEL_MOTION = "<MouseWheel>"

    LEFT_CLICK_RELEASE = "<ButtonRelease-1>"
    RIGHT_CLICK_RELEASE = "<ButtonRelease-2>"
    MIDDLE_CLICK_RELEASE = "<ButtonRelease-2>"

    LEFT_CLICK_PRESS = "<ButtonPress-1>"
    RIGHT_CLICK_PRESS = "<ButtonPress-2>"
    MIDDLE_CLICK_PRESS = "<ButtonPress-2>"

    LEFT_CLICK = "<Button-1>"
    RIGHT_CLICK = "<Button-3>"
    MIDDLE_CLICK = "<Button-2>"

    MOTION_WITH_LEFT_CLICK = "<B1-Motion>"
    MOTION_WITH_RIGHT_CLICK = "<B2-Motion>"
    MOTION_WITH_MIDDLE_CLICK = "<B3-Motion>"

    DOUBBLE_LEFT = "<Double-Button-1>"
    DOUBBLE_RIGHT = "<Double-Button-2>"
    DOUBBLE_MIDDLE = "<Double-Button-3>"

class FunctionKey(Enum):
    CONTROL = CTRL = "Control"
    ALT = "Alt"
class EventType(Enum):

    def __add__(self, other):
        this = self.value.replace("<", "").replace(">", "")
        other = (other.value if hasattr(other, "value") else other).replace("<", "").replace(">", "")
        return "<"+this+"-"+other+">"

    #Mouse
    MOUSE_MOTION = "<Motion>"
    WHEEL_MOTION = "<MouseWheel>"

    LEFT_CLICK = "<Button-1>"
    RIGHT_CLICK = "<Button-3>"
    MIDDLE_CLICK = "<Button-2>"

    LEFT_CLICK_RELEASE = "<ButtonRelease-1>"
    RIGHT_CLICK_RELEASE = "<ButtonRelease-2>"
    MIDDLE_CLICK_RELEASE = "<ButtonRelease-2>"

    LEFT_CLICK_PRESS = "<ButtonPress-1>"
    RIGHT_CLICK_PRESS = "<ButtonPress-2>"
    MIDDLE_CLICK_PRESS = "<ButtonPress-2>"


    DOUBBLE_LEFT = "<Double-Button-1>"
    DOUBBLE_RIGHT = "<Double-Button-2>"
    DOUBBLE_MIDDLE = "<Double-Button-3>"

    MOTION_WITH_LEFT_CLICK = "<B1-Motion>"
    MOTION_WITH_RIGHT_CLICK = "<B2-Motion>"
    MOTION_WITH_MIDDLE_CLICK = "<B3-Motion>"

    MOUSE_NEXT = "<Button-5>"
    MOUSE_PREV = "<Button-4>"
    #key Events
    KEY_UP = "<KeyRelease>"
    KEY_DOWN = "<KeyDown>"
    ESCAPE = ESC = "<Escape>"
    DELETE = "<Delete>"
    SPACE = "<space>"
    BACKSPACE = "<BackSpace>"

    STRG_LEFT = "<Control_L>"
    STRG_RIGHT = "<Control_R>"
    STRG_LEFT_UP = "<KeyRelease-Control_L>"
    STRG_RIGHT_UP = "<KeyRelease-Control_R>"
    STRG_LEFT_DOWN = "<KeyPress-Control_L>"
    STRG_RIGHT_DOWN = "<KeyPress-Control_R>"

    ALT_LEFT = "<Alt_L>"
    ALT_RIGHT = "<Alt_R>"
    ALT_LEFT_UP = "<KeyRelease-Alt_L>"
    ALT_RIGHT_UP = "<KeyRelease-Alt_R>"
    ALT_LEFT_DOWN = "<KeyPress-Alt_L>"
    ALT_RIGHT_DOWN = "<KeyPress-Alt_R>"

    SHIFT = "<Shift>"
    SHIFT_LEFT_UP = "<KeyRelease-Shift_L>"
    SHIFT_RIGHT_UP = "<KeyRelease-Shift_R>"
    SHIFT_LEFT_DOWN = "<KeyPress-Shift_L>"
    SHIFT_RIGHT_DOWN = "<KeyPress-Shift_R>"

    RETURN = "<Return>"
    RETURN_UP = "<KeyRelease-Return>"
    RETURN_DOWN = "<KeyPress-Return>"

    ARROW_DOWN = "<Down>"
    ARROW_RIGHT = "<Right>"
    ARROW_LEFT = "<Left>"
    ARROW_UP = "<Up>"

    #hotkeys
    CONTROL_S = "<Control-s>"
    CONTROL_C = "<Control-c>"
    CONTROL_V = "<Control-v>"
    CONTROL_Y = "<Control-y>"
    CONTROL_Z = "<Control-z>"
    CONTROL_X = "<Control-x>"

    F1 = "<F1>"
    F2 = "<F2>"
    F3 = "<F3>"
    F4 = "<F4>"
    F5 = "<F5>"


    #widget Events
    SIZE_CONFIUGURE = "<Configure>"
    DESTROY = "<Destroy>"
    ALL = ALL_KEYS = "<Key>"
    ENTER = "<Enter>"
    LEAVE = "<Leave>"
    LISTBOX_SELECT = "<<ListboxSelect>>"
    COMBOBOX_SELECT = "<<ComboboxSelected>>"
    #custom
    CUSTOM_RELATIVE_UPDATE = "[relative_update]" # [x, y, width, height]
    CUSTOM_RELATIVE_UPDATE_AFTER = "[relative_update_after]" # [x, y, width, height]

    @staticmethod
    def mouse(m):
        return m
    @staticmethod
    def key(k):
        return k
    @staticmethod
    def keyDown(k):
        return "<KeyPress-"+(k.value if hasattr(k, "value") else k)+">"
    @staticmethod
    def keyUp(k):
        return "<KeyRelease-"+(k.value if hasattr(k, "value") else k)+">"
    @staticmethod
    def customEvent(k):
        return k
    @staticmethod
    def hotKey(k1:FunctionKey, k2, k3=None):
        if k3 is not None and not isinstance(k2, FunctionKey): raise ValueError("if k3 is not None then k2 must be instance of 'FunctionKey'!")
        return "<"+(k1.value if hasattr(k1, "value") else k1)+"-"+(k2.value if hasattr(k2, "value") else k2)+("-"+(k3.value if hasattr(k3, "value") else k3) if k3 is not None else "")+">"

class CustomRunnable:
    """
    Custom Runnable.
    It forces to pass exactly the augments that are given to the __init__.
    """
    def __init__(self, command, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.command = command
    def __call__(self, *args, **kwargs):
        self.command(*self.args, **self.kwargs)

class PILImage:
    """
    Pillow image adapter for tkinter.
    Use 'PILImage.loadImage(<path>)' to load image from string path.
    Or use 'PILImage.loadImageFromPIL(<path>)' to load image from PIL.Image object.
    Used for advanced image progression.
    Package 'PIL.Image' have to be installed.
    """
    def __init__(self, image):
        import PIL.Image as Image
        self.copy = self.clone # redundant method
        self._preRenderedImage = None
        self._pilImage = Image # save pil.image from import!
        self._useOrg = False
        if isinstance(image, str):
            self._image = self._pilImage.open(image)
        elif isinstance(image, Image.Image):
            self._image = image
        else:
            raise TKExceptions.InvalidUsageException("Use 'Image.loadImage(<path>)' instead! Not:"+str(type(image)))
        self._original = self._image.copy()
    def __del__(self):
        self._original.close()
        self._image.close()
        del self._pilImage
    @staticmethod
    def loadImage(path:str):
        if os.path.exists(path):
            return PILImage(path)
        else:
            raise TKExceptions.PathNotExisits("This path does not Exists: "+str(path))
    @staticmethod
    def loadImageFromPIL(image):
        return PILImage(image)
    def clone(self, useOriginal=False):
        """
        Copies the image and returns a new image instance.
        @param useOriginal: if the original image should be taken.
        @return:
        """
        return PILImage(self._image.copy() if not useOriginal else self._original.copy())
    def toOriginal(self):
        """
        Resets the Image to original.
        @return:
        """
        self._image = self._original.copy()
        return self
    def resizeToIcon(self, useOriginal=False):
        """
        Resizes the image to default 16x16 icon size.
        @param useOriginal: if the original image should be taken.
        @return:
        """
        #256x256
        if useOriginal:
            self._image = self._original.resize((16, 16))
        else:
            self._image = self._image.resize((16, 16))
        return self
    def resize(self, fac:float, useOriginal=False):
        """
        Resizes the image with given factor.
        @param fac: factor for resize
        @param useOriginal: if the original image should be taken.
        @return:
        """
        if useOriginal:
            self._image = self._original.resize((int(round(self._original.width * fac, 0)), int(round(self._original.height * fac, 0))))
        else:
            self._image = self._image.resize((int(round(self._image.width * fac, 0)), int(round(self._image.height * fac, 0))))
        return self
    def resizeTo(self, x, y=None, useOriginal=False):
        """
        Resizes the image to fix size.
        @param x: int or Location2D instance
        @param y: int or None
        @param useOriginal: if the original image should be taken.
        @return:
        """
        if isinstance(x, Rect):
            x, y = x.getWidth(), x.getHeight()
        x = int(round(x, 0))
        y = int(round(y, 0))
        if useOriginal:
            self._image = self._original.resize((x, y))
        else:
            self._image = self._image.resize((x, y))
        return self
    def crop(self, loc:Location2D, loc2:Location2D, useOriginal=False):
        """
        Crops a square out of the image.
        @param loc: Location2D instance representing the first location
        @param loc2: Location2D instance representing the second location
        @param useOriginal: if the original image should be taken.
        @return:
        """
        if useOriginal:
            self._image = self._original.crop((*loc.get(), *loc2.get()))
        else:
            self._image = self._image.crop((*loc.get(), *loc2.get()))
        return self
    def getWidth(self):
        """
        Returns the current width of the image.
        @return:
        """
        return self._image.width
    def getHeight(self):
        """
        Returns the current width of the image.
        @return:
        """
        return self._image.height
    def preRender(self):
        """
        Converts the image to tkinter image.
        Call this earlyer in your code if an image error occurs.
        @return:
        """
        import PIL.ImageTk as imgTk
        self._preRenderedImage = imgTk.PhotoImage(self._image)
        return self
    def _get(self):
        if self._preRenderedImage is None:
            self.preRender()
            img = self._preRenderedImage
            self._preRenderedImage = None
            return img
        else:
            return self._preRenderedImage
    def _getPIL(self):
        return self._image
class TkImage:
    """
    Default tkinter image adapter.
    Use 'TkImage.loadImage(<path>)' to load image from string path.
    """
    def __init__(self, image:_tk_.PhotoImage):
        if isinstance(image, _tk_.PhotoImage):
            self.image = image
        else:
            raise TKExceptions.InvalidUsageException("Use 'Image.loadImage(<path>)' instad! Not:" + str(type(image)))
    @staticmethod
    def loadImage(path:str):
        if os.path.exists(path):
            return TkImage(_tk_.PhotoImage(file=path))
        else:
            raise TKExceptions.PathNotExisits("This path does not Exists: " + str(path))
    def resize(self, f:int):
        """
        Resizes the image using the tkinter 'subsample' method.
        @param f:
        @return:
        """
        self.image = self.image.subsample(f)
    def getWidth(self):
        """
        Returns the current width of the image.
        @return:
        """
        return int(self.image["width"])
    def getHeight(self):
        """
        Returns the current width of the image.
        @return:
        """
        return int(self.image["height"])
    def _get(self):
        return self.image

class Event:
    """
    Event class.
    Do not instantiate this class by yourself.
    The instance is passed by every bound function.
    It provides all nessesary values and information.
    """
    def __init__(self, dic=None, **kwargs):
        # feature deprecated
        assert dic is None, "Event cannot be casted!"
        if dic is None:
            self._data = {"afterTriggered":None,
                          "setCanceled": False,
                          "widget": None,
                          "args":[],
                          "priority":0,
                          "tkArgs":None,
                          "func":None,
                          "value":None,
                          "eventType":None,
                          "defaultArgs":False,
                          "disableArgs":True,
                          "decryptValueFunc":None,
                          "forceReturn":None,
                          "handler":None,
                          "pos":None
                          }
        else:
            self._data = dic._data

        for k, v in zip(kwargs.keys(), kwargs.items()):
            self._data[k] = v
    def __repr__(self):
        func = f"'{'' if not hasattr(self._data['func'], '__self__') else self._data['func'].__self__.__class__.__name__ + '.'}{self._data['func'] if not hasattr(self._data['func'], '__name__') else self._data['func'].__name__}'"
        return f"Event({{func: {func}, args:"+str(self["args"])+", priority:"+str(self["priority"])+", setCanceled:"+str(self["setCanceled"])+"})"
    def __del__(self):
        if hasattr(self, "_data"):
            self._data.clear()
    def __call__(self):
        if self["handler"] is None:
            return
        return self["handler"]()
    def __getitem__(self, item):
        return self._data[item]
    def __setitem__(self, key, value):
        self._data[key] = value
    def __lt__(self, other):
        return self["priority"] < other["priority"]
    def getTkArgs(self):
        """
        Returns the default tkinter event class.
        @return:
        """
        return self["tkArgs"]
    def setCanceled(self, b:bool=True):
        """
        Cancels the event.
        This works NOT for all events.
        @param b:
        @return:
        """
        self["setCanceled"] = b
    def getWidget(self):
        """
        Returns the widget which called the event.
        @return:
        """
        return self["widget"]
    def getValue(self):
        """
        Returns the selected Item or None.
        This works NOT for all events.
        @return:
        """
        return self["value"]
    def getPos(self)->Location2D:
        """
        Returns the mouse posistion when available through tkinter event.
        @return:
        """
        return self["pos"]
    def getScrollDelta(self)->Union[float, None]:
        """
       Returns the mouse scroll delta posistion when available through tkinter event.
       @return:
       """
        return self["tkArgs"].delta if hasattr(self["tkArgs"], "delta") else None
    def getArgs(self, i=None):
        """
        Returns the on bound specifyed Args.

        @param i: If args is a list returns the index i from that list.
        @return:
        """
        if self["args"] is None: return None
        if type(i) is int: return self["args"][i]
        return self["args"]
    def getEventType(self):
        """
        Returns bound EventType.
        @return:
        """
        return self["eventType"]
    def getKey(self):
        """
        If event type is any kind of keyboard event, this method returns the pressed key which triggered the event.
        @return:
        """
        return self.getTkArgs().keysym
    def isKey(self, k)->bool:
        """
        Checks if specific key was pressed.
        @param k:
        @return:
        """
        k = k.value if hasattr(k, "value") else k
        k = k.replace("<", "").replace(">", "")
        if not hasattr(self.getTkArgs(), "keysym"): return False
        return k == self.getTkArgs().keysym
    def printEventInfo(self):
        """
        Returns info about current event.
        @return:
        """
        print("This Event[type: "+self["eventType"]+"] was triggered by "+str(type(self["widget"]))+"! | Args:"+str(self["args"]))
class _EventRegistry:
    """
    Private event implementation.
    Handles event priorities.
    Used for debugging events.
    """
    def __init__(self, ins):
        if isinstance(ins, Widget) or isinstance(ins, Tk) or isinstance(ins, CanvasObject):
            self._data = {"event":{}, "widget":ins} # event : { type_ : ( <type:_EventHandler>, [<type:Event>, ...] ) }
        elif isinstance(ins, dict):
            self._data = ins
        elif isinstance(ins, _EventRegistry):
            self._data = ins._data
        else:
            raise TKExceptions.InvalidWidgetTypeException("ins must be " + str(self.__class__.__name__) + " instance not: " + str(ins.__class__.__name__))
    def __repr__(self):
        return str(self.__class__.__name__)+"("+str(self._data)+")"
    def __del__(self):
        self._data.clear()
    def __getitem__(self, item):
        return self._data[item]
    def __setitem__(self, key, value):
        self._data[key] = value
    def printAllBinds(self):
        print("Widget: "+self["widget"].__class__.__name__)
        for k, v in zip(self["event"].keys(), self["event"].values()):
            print("-EventType: "+k+":")
            for event in v[1]:
                print(" -bind to: "+event["func"].__name__)
    def addEvent(self, event, type_):
        handler = None
        if type_ in self["event"].keys(): # add Event
            self["event"][type_][1].append(event)
            self["event"][type_][1].sort()
            self["event"][type_][1].reverse()
        else:                             # new event type
            handler = _EventHandler(event)
            self["event"][type_] = (handler, [event])
        if _EventHandler.DEBUG:
            print(self["event"][type_][0])
        return handler
    def getRegisteredEvents(self, type_):
        return self["event"][type_][1]
    def getCallables(self, type_)->Union[Event, list]:
        if type_ in self["event"].keys():
            return self["event"][type_][1]
        return []
    def getHandler(self, type_):
        if type_ in self["event"].keys():
            return self["event"][type_][0]
        return None
    def unregisterType(self, type_):
        if type_ in self["event"].keys():
            _event = self["event"][type_][0].event
            _event.getWidget()._get().unbind(_event.getEventType())
            self["event"].pop(type_)
    def unregisterAll(self):
        for i in self["event"].values():
            _event = i[0].event
            try:
                _event.getWidget()._get().unbind(_event.getEventType())
            except:

                pass
        self["event"] = {}
class _EventHandler:
    DEBUG = False
    #OLD:  _Events = {} #save in Individual instance! { <obj_id> : <type: _EventHandler> }
    def __init__(self, event):
        assert isinstance(event, Event), "Do not instance this class by yourself!"
        self.event = event
        #print(self.event.getWidget()["registry"], self.event.getWidget())
    def __repr__(self):
        return "EventHandler("+"{widgetType:\""+type(self.event["widget"]).__name__+"\", eventType:"+str(self.event["eventType"])+", ID:"+self.event["widget"]["id"]+"}) bind on: \n\t-"+"\n\t-".join([str(i) for i in self.event["widget"]["registry"].getRegisteredEvents(self.event["eventType"])])
    def __getitem__(self, item):
        return self.event[item]
    def __setitem__(self, key, value):
        self.event[key] = value
    def __call__(self, *args):
        #print("Args:", type(args[0]))
        if self.event is None: return
        def raiseError():
            info = f"""
# Could not call bound function!
# BindTo:    '{"" if not hasattr(event["func"], "__self__") else event["func"].__self__.__class__.__name__ + "."}{event["func"] if not hasattr(event["func"], "__name__") else event["func"].__name__}'
# Widget:    '{type(event["widget"]).__name__}'
# EventType: {event["eventType"]}
# priority:  {event["priority"]}
# args:      {event["args"]}
# value:     {event["value"]}"""
            _max = max([len(i) for i in info.splitlines()])
            _info = ""
            for i in info.splitlines():
                _info += i + " "*(_max-len(i)+1) + "#" + "\n"
            info = _info
            info = "\n" + "#" *(_max+2) + info + "#" *(_max+2)

            raise TKExceptions.EventExecutorException(info)
        args = args[0] if len(args) == 1 else list(args)
        event = None
        out = None
        if "widget" not in self.event._data.keys(): return #  event already dropped
        for event in self.event["widget"]["registry"].getCallables(self.event["eventType"]): #TODO get only the output of the last called func. problem? maybe priorities
            func = event["func"]
            event["tkArgs"] = args
            if event["decryptValueFunc"] is not None:
                event["value"] = event["decryptValueFunc"](args) #TODO event in 'decryptValueFunc'
                if event["value"] == "CANCEL":
                    return
            if not event["defaultArgs"]:
                if event["value"] is None:
                    if hasattr(args, "x") and hasattr(args, "y"):
                        event["pos"] = Location2D(args.x, args.y)
                args = event
            # call event
            if ((not hasattr(func, "__code__")) or ("self" in func.__code__.co_varnames and func.__code__.co_argcount > 1) or ("self" not in func.__code__.co_varnames and func.__code__.co_argcount > 0)) and not event["disableArgs"]:
                try: out = func(args)
                except: raiseError()
            else:
                try: out = func()
                except: raiseError()
            if not len(event._data): return False # destroyed
            if event["afterTriggered"] is not None: event["afterTriggered"](event, out)
        # After all events are processed
        if event["forceReturn"] is not None:
            return event["forceReturn"]
    @staticmethod
    def setEventDebug(b:bool):
        _EventHandler.DEBUG = b
    @staticmethod
    def printAllBinds(widget):
        widget["registry"].printAllBinds()
    @staticmethod
    def _registerNewEvent(obj, func, eventType:Union[EventType, Key, Mouse], args: list, priority:int, decryptValueFunc=None, defaultArgs=False, disableArgs=False):
        """
        This is the intern Event-Register
        @param obj: the widget
        @param func: the target function to be bound
        @param eventType: the event type to trigger the event
        @param args: arguments which are transferred to the function
        @param decryptValueFunc: this function gets called before the binded func was called
        @param defaultArgs: this bool decides if the 'Event' instance or the mormal tkinter args are passed into the target function
        @param disableArgs: if this is True no arguments will be passed
        @return: None
        """
        if hasattr(eventType, "value"):
            eventType = eventType.value
        assert isinstance(func, Callable), eventType + " bound Func is not callable " + str(func) + " instead!"
        event = Event()
        event["defaultArgs"] = defaultArgs
        event["disableArgs"] = disableArgs
        event["widget"] = obj
        event["args"] = args
        event["func"] = func
        event["decryptValueFunc"] = decryptValueFunc
        event["eventType"] = eventType
        event["priority"] = priority
        handler = obj["registry"].addEvent(event, eventType)
        if handler is not None:
            try:
                obj._get().bind(eventType, handler)
            except:
                func = f"'{'' if not hasattr(func, '__self__') else func.__self__.__class__.__name__ + '.'}{func if not hasattr(func, '__name__') else func.__name__}'"
                raise TKExceptions.BindException(f"Could not bind event type '{eventType}' to func {func}!")
        event["handler"] = _EventHandler(event)
        return event
    @staticmethod
    def _registerNewCommand(obj, func, args:Union[list, None], priority:int, decryptValueFunc=None, defaultArgs=False, disableArgs=False, onlyGetRunnable=False, cmd="command"):
        assert isinstance(func, Callable), "command binded Func is not callable " + str(type(func)) + " instead!"
        event = Event()
        event["defaultArgs"] = defaultArgs
        event["disableArgs"] = disableArgs
        event["widget"] = obj
        event["args"] = args
        event["func"] = func
        event["priority"] = priority
        event["decryptValueFunc"] = decryptValueFunc
        event["eventType"] = "cmd"
        handler = obj["registry"].addEvent(event, "cmd")
        if not onlyGetRunnable:
            if handler is not None:
                obj._get()[cmd] = handler
            event["handler"] = _EventHandler(event)

        else:
            return handler
        return event
    @staticmethod
    def _registerNewValidateCommand(obj, func, args:list, priority:int, type_="all", decryptValueFunc=None, defaultArgs=False, disableArgs=False):
        assert isinstance(func, Callable), "vCommand binded Func is not callable " + str(type(func)) + " instead!"
        event = Event()
        event["defaultArgs"] = defaultArgs
        event["disableArgs"] = disableArgs
        event["widget"] = obj
        event["args"] = args
        event["func"] = func
        event["priority"] = priority
        event["decryptValueFunc"] = decryptValueFunc
        event["forceReturn"] = True
        event["eventType"] = "vcmd"
        handler = obj["registry"].addEvent(event, "vcmd")
        if handler is not None:
            obj["widget"]["validate"] = type_
            obj["widget"]["validatecommand"] = (obj["master"]._get().register(handler), '%P')
        event["handler"] = _EventHandler(event)
    @staticmethod
    def _registerNewTracer(obj, var, func, args:list, priority:int, decryptValueFunc=None, defaultArgs=False, disableArgs=False):
        assert isinstance(func, Callable), "tracer bound Func is not callable " + str(type(func)) + " instead!"
        event = Event()
        event["defaultArgs"] = defaultArgs
        event["disableArgs"] = disableArgs
        event["widget"] = obj
        event["args"] = args
        event["func"] = func
        event["priority"] = priority
        event["decryptValueFunc"] = decryptValueFunc
        event["eventType"] = "trace"
        handler = obj["registry"].addEvent(event, "trace")
        if handler is not None:
            var.trace("w", handler)
        event["handler"] = _EventHandler(event)
    @staticmethod
    def _getNewEventRunnable(obj, func, args, priority:int, decryptValueFunc=None, defaultArgs=False, disableArgs=False, after=None):
        assert isinstance(func, Callable), "Runnable bound Func is not callable " + str(type(func)) + " instead!"
        event = Event()
        event["defaultArgs"] = defaultArgs
        event["disableArgs"] = disableArgs
        event["widget"] = obj
        event["args"] = args
        event["func"] = func
        event["priority"] = priority
        event["decryptValueFunc"] = decryptValueFunc
        event["afterTriggered"] = after
        event["eventType"] = "runnable"
        handler = obj["registry"].addEvent(event, "runnable")
        if handler is not None:
            event["handler"] = handler
        else:
            event["handler"] = _EventHandler(event)
        return event["handler"]
    @staticmethod
    def _registerNewCustomEvent(obj, func, eventType:Union[EventType, Key, Mouse], args, priority: int, decryptValueFunc=None, defaultArgs=False, disableArgs=False, after=None):
        assert isinstance(func, Callable), "CustomEvent bound Func is not callable " + str(type(func)) + " instead!"
        if hasattr(eventType, "value"):
            eventType = eventType.value
        event = Event()
        event["defaultArgs"] = defaultArgs
        event["disableArgs"] = disableArgs
        event["widget"] = obj
        event["args"] = args
        event["func"] = func
        event["priority"] = priority
        event["decryptValueFunc"] = decryptValueFunc
        event["afterTriggered"] = after
        event["eventType"] = eventType
        handler = obj["registry"].addEvent(event, eventType)
        eventType = eventType.value if hasattr(eventType, "value") else eventType
        event["handler"] = _EventHandler(event)


        if eventType == "[relative_update]" or eventType == "[relative_update_after]":
            obj["placeRelData"]["handler"] = _EventHandler(event)


        return handler
    @staticmethod
    def _registerNewTagBind(obj, id_, func, eventType: Union[EventType, Key, Mouse], args: list, priority:int, decryptValueFunc=None, defaultArgs=False, disableArgs=False):
        if hasattr(eventType, "value"):
            eventType = eventType.value
        assert isinstance(func, Callable), eventType + " boun Func is not callable " + str(func) + " instead!"
        event = Event()
        event["defaultArgs"] = defaultArgs
        event["disableArgs"] = disableArgs
        event["widget"] = obj
        event["args"] = args
        event["func"] = func
        event["priority"] = priority
        event["decryptValueFunc"] = decryptValueFunc
        event["eventType"] = eventType
        handler = obj["registry"].addEvent(event, eventType)
        if handler is not None:
            obj._get().tag_bind(id_, eventType, handler)
        event["handler"] = _EventHandler(event)
class _TaskScheduler:
    def __init__(self, _master, delay, func, repete=False, dynamic=False):
        if hasattr(_master, "_get"):
            self._id = None
            self._master = _master
            self._delay = delay
            self._func = func
            self._repete = repete
            self._dynamic = dynamic
        else:
            raise TKExceptions.InvalidWidgetTypeException("WidgetType must be any 'tkWidget' or 'Tk' not:"+str(type(_master)))
    def __call__(self):
        f = time()
        self._func()
        if self._repete:
            self._id = self._master._get().after(self._delay*1000 if not self._dynamic else self._delay-(time()-f) if self._delay-(time()-f) > 0 else 0, self)
    def start(self):
        self._id = self._master._get().after(int(self._delay*1000), self)
        return self
    def cancel(self):
        if self._id is not None: self._master._get().after_cancel(self._id)
class _IntVar:
    def __init__(self, _master):
        self.index = -1
        self.command = None
        self._intvar = _tk_.IntVar(_master._get())
    def _add(self):
        self.index +=1
        return self.index
    def _get(self):
        return self._intvar
    def get(self):
        return self._intvar.get()
    def set(self, v:int):
        self._intvar.set(v)

class Tk:
    """
    The toplevel window class

    """
    def __init__(self, _master=None, group=None):
        self.setAllwaysOnTop = self.setTopmost
        self.title = self.setTitle
        self.quit = self.quitMainLoop
        self.withdraw = self.hide
        self.setBackgroundColor = self.setBg
        if _master is None:
            self._data = {"master": _tk_.Tk(), "registry":_EventRegistry(self), "placeRelData":{"handler":None}, "isRunning":False, "destroyed":False, "hasMenu":False, "childWidgets":{},"oldWinSize":(-1, -1), "setSize":(),  "privateOldWinSize":(-1, -1), "id":"".join([str(randint(0,9)) for _ in range(15)]), "dynamicWidgets":{}, "closeRunnable":None, "title":""}
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
    def __del__(self):
        pass
        #print("__DELETE__", type(self))
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
    def getWindowActive(self)->bool:
        return self["isRunning"]
    def throwErrorSound(self):
        self["master"].bell()
    def onWindowResize(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False, filterEvent=True):
        _EventHandler._registerNewEvent(self, func, EventType.key("<Configure>"), args, priority, decryptValueFunc=(self._decryptWindowResize if filterEvent else self._decryptNonFilteredWindowResize), defaultArgs=defaultArgs, disableArgs=disableArgs)
    def copyToClip(self, s):
        self["master"].clipboard_append(str(s))
        return self
    def clearClip(self):
        self["master"].clipboard_clear()
        return self
    def getClip(self):
        return self["master"].clipboard_get()
    def setFocus(self):
        """
        Sets the focus to this Window.

        @return:
        """
        self["master"].focus_set()
        return self
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
    def setIcon(self, icon:Union[TkImage, PILImage]):
        """
        Sets the icon in the top left corner from the Window.

        @param icon:
        @return:
        """
        self["master"].iconphoto(True, icon._get())
        return self
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
    def lift(self):
        """
        Lifts the Window on top of all other Windows.
        @return:
        """
        self["master"].lift()
        return self
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
    #def bindToWidgetType(self, func, eventType:Union[EventType, Key, Mouse], event, args:list=None, defaultArgs=False, disableArgs=False):
        #_EventHandler.registerNewEvent(self, func, event.__name__, args, defaultArgs=defaultArgs, disableArgs=disableArgs, bindFunc="bind_class")
    def bind(self, func:Callable, event:Union[EventType, Key, Mouse, str], args:list=None, priority:int=0, defaultArgs=False, disableArgs=False):
        """
        Binds a specific event to the Window. Runs given function on trigger.

        @param func: function get called on trigger
        @param event: Event type: EventType enum or default tkinter event as string.
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
    #def bindAll(self, func, event: Union[EventType, Key, Mouse], args: list=None, priority:int=0, defaultArgs=False, disableArgs=False):
        #EventHandler._registerNewEvent(self, func, event, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs, bindFunc="bind_all")
    def unbindEvent(self, event:Union[EventType, Key, Mouse]):
        """
        Unbinds all Events from given EventType.

        @param event:
        @return:
        """
        #self["registry"].unregisterType(event)
        raise NotImplemented()
    def unbindAllEvents(self):
        """
        Unbind all Events.

        @return:
        """
        #self["registry"].unregisterAll()
        raise NotImplemented()
    def getMousePosition(self):
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
    def setCursor(self, c:Union[Cursor, str]):
        """
        Set cursor image from Cursor enum or default tkinter string.

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
    def clearAllWidgets(self):
        """
        Destroys all Widgets in the Window.

        @return:
        """
        #for i in self["master"].winfo_children():
        #    i.destroy()
        raise NotImplemented()
    def centerWindowOnScreen(self, forceSetSize=False):
        """
        Centers the Window on screen

        @param forceSetSize: get the Parameters from 'setWindowSize' function and not from tkinter
        @return:
        """
        width, height = self.getWindowSize()
        if width == 1 or forceSetSize:
            if len(self["setSize"]) == 2:
                width, height = self["setSize"]
            else:
                raise TKExceptions.InvalidUsageException("Run the mainloop first or specify a window size manually to center the Window!")
        swidth , sheight = self.getScreenSize()
        nwidth = int(round((swidth/2-width/2), 0))
        nheight = int(round((sheight/2-height/2), 0))
        self.setPositionOnScreen(nwidth, nheight)
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
    def activeWidgets(self): #@TODO: FIX!
        #for i in self["master"].winfo_children():
        #    yield i
        raise NotImplemented()
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
    def disable(self, b=True):
        self["master"].wm_attributes("-disabled", b)
    def overrideredirect(self, b=True):
        self["master"].overrideredirect(b)
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
    def setFullscreen(self, b:bool):
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
    def close(self):
        """
        Closes the window only if it was not prevented in the 'windowCloseEvent' with the setCanceled.

        @return:
        """
        if self["closeRunnable"] is None:
            self.destroy()
        else:
            self["closeRunnable"]()
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
    def setBg(self, col:Union[Color, str]):
        """
        Set the Background Color of the Window.

        @param col: Use Color enum, tkinter string or hex-code.
        @return:
        """
        self["master"]["bg"] = col.value if hasattr(col, "value") else col
        return self
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
    def setWindowSize(self, x:int, y:int, minsize=False):
        """
        Set the Windowsize. Can also set the 'minsize'.

        @param x:
        @param y:
        @param minsize:
        @return:
        """
        self["setSize"] = (x, y)
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
    def quitMainLoop(self):
        """
        Quit the Window. BUT the Window mainloop is still running.

        @return:
        """
        self["master"].quit()
    def mainloop(self):
        """
        Starts the Window mainloop.
        Call this Method after the creation of all Widgets to open/start the Window.
        All code after the mainloop is only executed if the Window is terminated.

        @return:
        """
        self._mainloop()
    def _mainloop(self):
        """
        Private Implementations of 'mainloop' call.
        @return:
        """
        if self["destroyed"]: return
        self._finishLastTasks()
        self["isRunning"] = True
        self["master"].mainloop()
        self["isRunning"] = False
        self["destroyed"] = True
    def _updateDynamicSize(self, widget):
        """
        Private implementation of the 'updateDynamicWidgets'.
        @param widget:
        @return:
        """
        if not widget["destroyed"] and "xOffset" in widget["placeRelData"]:# and widget["id"] in list(self["dynamicWidgets"].keys()):
            widget._get().place_forget()
            self._get().update_idletasks()
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
            widget._get().update_idletasks()
            widget["placed"] = True
    def updateDynamicWidgets(self):
        """
        Call this method to update all relative placed Widgets
        wich are placed with 'placeRelative' manager.

        @return:
        """
        # OLD implementation
        #for widget in list(self["dynamicWidgets"].values())[::-1]: # place frames first
        #    if not widget["destroyed"]: self._updateDynamicSize(widget)

        relevantIDs = list(self["dynamicWidgets"].keys())
        for widget in self._getAllChildWidgets(self):
            if widget._getID() in relevantIDs:
                if isinstance(widget, _ToolTip): continue
                if not widget["destroyed"]: self._updateDynamicSize(widget)
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
        self["dynamicWidgets"][widget["id"]] = widget
    def _unregisterOnResize(self, widget):
        if list(self["dynamicWidgets"].keys()).__contains__(widget["id"]):
            del self["dynamicWidgets"][widget["id"]]
    def _decryptWindowResize(self, args):
        _size = self.getWindowSize()
        if self["oldWinSize"] == _size:
            return "CANCEL"
        else:
            self["oldWinSize"] = _size
            return _size
    def _decryptNonFilteredWindowResize(self, args):
        return self.getWindowSize()
    def _privateDecryptWindowResize(self, args):
        _size = self.getWindowSize()
        if self["privateOldWinSize"] == _size:
            return "CANCEL"
        else:
            self["privateOldWinSize"] = _size
            return _size
    def _finishLastTasks(self):
        _EventHandler._registerNewEvent(self, self.updateDynamicWidgets, EventType.key("<Configure>"), args=[], priority=1, decryptValueFunc=self._privateDecryptWindowResize)
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
    @staticmethod
    def _getAllChildWidgets(widget):
        """
        @TODO REMOVED widget gets added to its child wigets many wrong
        @param widget:
        @return:
        """
        ch = [] # [widget]
        def point(_widget):
            for cw in _widget["childWidgets"].values():
                ch.append(cw)
                point(cw)
        point(widget)
        return ch
    @staticmethod
    def _getAllParentWidgets(widget):
        ch = []

        while True:
            if isinstance(widget, Tk):
                break
            widget = widget["master"]
            ch.append(widget)

        return ch
    @staticmethod #TODO FINISH
    def _showParentChildTree(widget):
        print("==Hierarchy==")
        def point(_widget):
            for cw in _widget["childWidgets"].values():
                #print("".join([("| " if not isinstance(cw, _tk_.Tk) and not isinstance(cw["master"], _tk_.Tk) and not isinstance(cw["master"]["master"], _tk_.Tk) and any([index == (len(Tk._getAllParentWidgets(cw))-2)]) and list(cw["master"]["master"]["childWidgets"].values()).index(cw["master"]) != len(list(cw["master"]["master"]["childWidgets"].values()))-1 else "  ") for index in range(len(Tk._getAllParentWidgets(cw))-1)]) + ("└" if len(_widget["childWidgets"].values())-1 == list(_widget["childWidgets"].values()).index(cw) else "├")+"─"+cw.__class__.__name__)
                print("".join([("| " if not isinstance(cw, _tk_.Tk) and not isinstance(cw["master"], _tk_.Tk) and not isinstance(cw["master"]["master"], _tk_.Tk) and any([index == (len(Tk._getAllParentWidgets(cw))-2)]) and list(cw["master"]["master"]["childWidgets"].values()).index(cw["master"]) != len(list(cw["master"]["master"]["childWidgets"].values()))-1 else "  ") for index in range(len(Tk._getAllParentWidgets(cw))-1)]) + ("" if len(_widget["childWidgets"].values())-1 == list(_widget["childWidgets"].values()).index(cw) else "")+""+cw.__class__.__name__)
                point(cw)
        print(widget.__class__.__name__)
        point(widget)
    def _get(self):
        return self["master"]
class Toplevel(Tk):
    """
    Toplevel window.
    Pass 'Tk' for _master to Use 'Toplevel' as 'Tk-class'.
    This is useful if your application can run standalone (Tk) and can be imported to run as a Toplevel window above another application.
    """
    def __init__(self, _master, group=None, topMost=True):
        if isinstance(_master, Tk):
            self._data = {"master": _tk_.Toplevel(), "tkMaster":_master, "registry":_EventRegistry(self), "setSize":(), "isRunning":False, "destroyed":False, "hasMenu":False, "childWidgets":{},"oldWinSize":(-1, -1), "privateOldWinSize":(-1, -1), "id":"".join([str(randint(0,9)) for _ in range(15)]), "dynamicWidgets":{}, "title":"", "closeRunnable":None}
            _EventHandler._registerNewEvent(self, self.updateDynamicWidgets, EventType.key("<Configure>"), args=[], priority=1, decryptValueFunc=self._privateDecryptWindowResize)
            # configure internal onCloseEvent
            self["master"].protocol("WM_DELETE_WINDOW", self._internalOnClose)
        elif isinstance(_master, str) and _master == "Tk":
            self._data = {"master":_tk_.Tk(), "tkMaster":_master, "placeRelData":{"handler":None}, "registry":_EventRegistry(self), "setSize":(),"isRunning":False, "destroyed":False, "hasMenu":False, "childWidgets":{},"oldWinSize":(-1, -1), "privateOldWinSize":(-1, -1),"id":"".join([str(randint(0, 9)) for _ in range(15)]), "dynamicWidgets":{}, "title":"", "closeRunnable":None}
            _EventHandler._registerNewEvent(self, self.updateDynamicWidgets, EventType.key("<Configure>"), args=[], priority=1, decryptValueFunc=self._privateDecryptWindowResize)
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
        if isinstance(self["master"], _tk_.Tk):
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
        self._get().grab_set()
    def show(self):
        """
        Shows the dialog.

        @return:
        """
        self._get().grab_set()
        self["master"].deiconify()
    def hide(self):
        """
        Hides the dialog.

        @return:
        """
        self._get().grab_release()
        self["master"].withdraw()

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
        if list(_data.keys()).__contains__("id"): self._data = _data
        else:
            _data["tkMaster"] = _data["master"] if isinstance(_data["master"], Tk) else _data["master"]["tkMaster"]
            id = "".join([str(randint(0,9)) for _ in range(15)])
            self._data = {**_data, **{"widgetProperties":{},"childWidgets":{}, "id":id, "placed":True, "destroyed":False, "placeRelData":{"handler":None}, "registry":_EventRegistry(self), "group":group}}
            self._data["master"]["childWidgets"][self["id"]] = self._ins
            if list(_data.keys()).__contains__("init"):
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
        print("__DELETE__", type(self))
        if not len(self._data): return
        if self["group"] is not None:
            self["group"].remove(self._ins)
        self._data.clear()
    # Attribute Setter Methods
    def setBg(self, col:Union[Color, str]):
        """
        Set the background color of this widget.

        @param col: Use Color enum, tkinter string or hex-code.
        @return:
        """
        self._setAttribute("bg", col.value if hasattr(col, "value") else col)
        return self
    def setFg(self, col:Union[Color, str]):
        """
        Set the text color of this widget.

        @param col: Use Color enum, tkinter string or hex-code.
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
    def setFont(self, size:int=10, art=FontType.ARIAL, underline=False, bold=False, slant=False, overstrike=False):
        """
        Use this method to configure the Font.

        @param size: text size
        @param art: font type
        @param underline: text is underlined
        @param bold: text is bold
        @param slant: text is slant
        @param overstrike: text is overstrike
        @return:
        """
        _data = {'family': art.value if hasattr(art, "value") else art,
                'size': size,                            # size
                'weight': 'bold' if slant else 'normal', # fett
                'slant': 'italic' if bold else'roman',   # kusiv
                'underline': bool(underline),            # unterstrichen
                'overstrike': bool(overstrike)}          # durchgestrichen

        self._setAttribute("font", _font.Font(**_data))
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
        Set the Orientation via Orient enum.
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
        Use Style enum to choose between styles.

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
        Set cursor image from Cursor enum or default tkinter string.
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
        self._setAttribute("state", _tk_.DISABLED)
        return self
    def setEnabled(self):
        """
        Enables this widget.

        @return:
        """
        self._setAttribute("state", _tk_.NORMAL)
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
    def getRelScreenPos(self)->Location2D:
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
        @param event: Event type: EventType enum or default tkinter event as string.
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
        self._get().place_forget()
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
        except:
            pass
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
    def _getTkMaster(self)-> Tk | Toplevel:
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
    def _decryptEvent(self, args):
        pass
    def _id(self):
        return self["id"]
    def _register(self, e):
        self["master"].register(e)
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
class _WidgetGroupMethod:
    def __init__(self, _ins, name):
        self._ins = _ins
        self._name = name
    def __call__(self, *args, **kwargs):
        if self._ins._priorityData is not None:
            """
            There is an execution with settings only used once!
            """
            _data = self._ins._priorityData.copy()
            self._ins._priorityData = None
        else:
            _data = self._ins._data.copy()

        for i, w in enumerate(self._ins._widgets):
            if _data["changeOnlyForType"] is not None and not isinstance(w, _data["changeOnlyForType"]): continue
            try:
                out = getattr(w, self._name)(*args, **kwargs)
            except Exception as e:
                if _data["ignoreErrors"]: continue
                raise Exception(f"Error while execute '{self._name}' command on [{len(self._ins._widgets)}].\nType: {type(w)}, Error: {e}")
class WidgetGroup:
    """
    Use the WidgetGroup to group widget.

    Methods can than be called on the group to configure all members in the group.
    """
    _GROUPS = []
    def __init__(self, instantiate=None):
        """
        @param instantiate: creates a copy of given group.
        """
        self._widgets = []
        self._commandsOnRegister = [*instantiate._commandsOnRegister] if instantiate is not None else []
        self._data = {
            "ignoreErrors":False,
            "changeOnlyForType":None,
        }
        self._priorityData = None # data for settings with execute once
        for method in dir(Widget):
            if method.startswith("__"): continue
            setattr(self, method, _WidgetGroupMethod(self, method))
        WidgetGroup._GROUPS.append(self)
    def add(self, w):
        """
        Adds widget w to this group.

        @param w:
        @return:
        """
        for method in dir(type(w)):
            if method.startswith("__"): continue
            if hasattr(self, method): continue
            setattr(self, method, _WidgetGroupMethod(self, method))
        self._widgets.append(w)
        self.executeCommands(w)
        if WIDGET_DELETE_DEBUG: print(f"+{len(self._widgets)} {type(w)}")
    def remove(self, w):
        """
        Removes widget from this group.

        @param w:
        @return:
        """
        if w in self._widgets:
            self._widgets.remove(w)
            if WIDGET_DELETE_DEBUG: print(f"-{len(self._widgets)} {type(w)}")
    def addCommand(self, function_name:str, *args, ignoreErrors=False, onlyFor=None):
        """
        Given function is executed on if Widget is created with this Group.

        set Function_name '@custom' for Custom change.
        Pass function with one Argument (for widget) to args!

        @param function_name: name of the function to call on instantiate.
        @param args: arguments for this function
        @param ignoreErrors: if the errors should be ignored
        @param onlyFor: the function is only executed for widget type
        @return:
        """
        self._commandsOnRegister.append([function_name, args, ignoreErrors, onlyFor])
    def executeCommands(self, w=None, ignoreAll=False):
        """
        This method runs all the registered Commands.

        @param w: widget to execute commands on | None -> all widgets
        @param ignoreAll: if errors should be ignored
        @return:
        """
        def _run(w):
            for cmd, args, igErr, olyF in self._commandsOnRegister:
                if cmd is None and igErr: continue
                if olyF is not None and type(w) != olyF: continue
                if ignoreAll: igErr = True
                try:
                    if cmd == "@custom":
                        args[0](w)
                    else:
                        getattr(w, cmd)(*args)
                except Exception as e:
                    if igErr: continue
                    raise Exception(f"Error while execute '{cmd}' command on [{len(self._widgets)}].\nType: {type(w)}, Error: {e}")
        if w is None:
            for w in self._widgets: _run(w)
        else:
            _run(w)
    def clearCommands(self):
        """
        Clears all registered Commands/Functions.

        @return:
        """
        self._commandsOnRegister.clear()
    def setIgnoreErrors(self, b:bool):
        """
        Errors in methods that are executed from this group are ingnored.

        @param b: is error ignored.
        @return:
        """
        self._data["ignoreErrors"] = bool(b)
        return self
    def runWithSettings(self, ignoreErrors=False, changeOnlyForType=None):
        """
        Run only the following Command with these settings.

        Example:
            group.runWithSettings(changeOnlyForType=tk.Button).

        @param ignoreErrors: is error ignored.
        @param changeOnlyForType: command is only executed on that widget. Type: Widget.
        @return:
        """
        self._priorityData = {
            "ignoreErrors":ignoreErrors,
            "changeOnlyForType":changeOnlyForType,
        }
        return self

    @staticmethod
    def removeFromAll(widg):
        """
        This widget get removed from all groups.

        @param widg:
        @return:
        """
        for group in WidgetGroup._GROUPS:
            group.remove(widg)
class Placer:
    def __init__(self, ySpace, yStart=0):
        self._ySpace = ySpace
        self._yStart = yStart
    def get(self):
        x = self._yStart
        self._yStart += self._ySpace
        return x

class _ToolTip(Widget):
    """
    Create a tooltip for a given widget.
    It shows up on hover over widget.
    """
    def __init__(self, _master, pressShiftForMoreInfo=False, waitBeforeShow=.5, group=None):
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Tk) or isinstance(_master, Widget):
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
class PDFViewer(Widget):
    def __init__(self, _master, path, group=None):
        from tkPDFViewer import tkPDFViewer as pdf
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
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
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
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
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master": _master, "widget": cal.Calendar(_master._get()), "init": {}}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + ", Frame or Tk instance not: " + str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def _decryptEvent(self, args):
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
        self._setAttribute("maxdate", date(y, m, d))
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
        self._setAttribute("mindate", date(y, m, d))
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
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master": _master, "widget": cal.DateEntry(_master._get()), "init": {}}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + ", Frame or Tk instance not: " + str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def _decryptEvent(self, args):
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
        self._setAttribute("maxdate", date(y, m, d))
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
        self._setAttribute("mindate", date(y, m, d))
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
        _EventHandler._registerNewEvent(self, func, EventType.customEvent("<<CalendarSelected>>"), args, priority,
                                        decryptValueFunc=self._decryptEvent, defaultArgs=defaultArgs,
                                        disableArgs=disableArgs)
class ScrollBar(Widget):
    """
    Scrollbar Widget can be attached to some Widget using their 'attachScrollbar' method.
    """
    def __init__(self, _master, autoPlace=True, group=None):
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master": _master, "widget": ttk.Scrollbar(_master._get()), "autoPlace":autoPlace, "thickness":18, "init": {}}
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
    def _decryptEvent(self, args):
        return None
class Frame(Widget):
    """
    Widget:
    The Frame is used to group or organize widgets.
    Frames can be places and configured as usualy.
    Once the frame is places it can be used as Master to place other widgets on and relative to the frame.
    """
    def __init__(self, _master, group=None):
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master": _master,  "widget": _tk_.Frame(_master._get())}
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
        if isinstance(_master, dict):
            self._data = _master

        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master": _master,  "widget": _tk_.LabelFrame(_master._get())}
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
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master":_master,  "widget":_tk_.Label(_master._get()), "init":kwargs}
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
    def __init__(self, _master, group=None, widgetClass=_tk_.Checkbutton):
        self.getValue = self.getState
        self.setValue = self.setState
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, _SubMenu):
            self._data = {"master": _master._master,  "widget": _tk_.Checkbutton(_master._master._get()), "instanceOfMenu":True}
            _master._widgets.append(["checkbutton", self])
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            intVar = _tk_.IntVar(_master._get())
            self._data = {"master":_master, "text":"", "widget":widgetClass(_master._get()), "intVar":intVar, "init":{"variable":intVar}}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def __bool__(self):
        return bool(self.getState())
    def _decryptEvent(self, e):
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
        super().__init__(_master, group, widgetClass=ttk.Checkbutton)
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
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
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
        self._data = {"master": _master, "widget": _tk_.Radiobutton(_master._get()), "intvar": intVar, "init": {"variable": intVar._get(), "value": intVar._add()}}
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
    def _decryptEvent(self, args):
        return self.getText()
class Button(Widget):
    """
    Widget:
    The Button widget is clickable.
    The onclick event can be bound via the 'setCommand' method.
    """
    def __init__(self, _master, group=None, text="", canBePressedByReturn=True, fireOnlyOnce=True, fireInterval:float=0.1, firstDelay:float=0.5):
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master":_master, "widget":_tk_.Button(_master._get()), "canBePressedByReturn":canBePressedByReturn, "instanceOfMenu":False, "init":{"text":text}}
            if not fireOnlyOnce:
                self._data["init"]["repeatdelay"] = int(firstDelay * 1000)
                self._data["init"]["repeatinterval"] = int(fireInterval * 1000)
        elif isinstance(_master, _SubMenu) or isinstance(_master, ContextMenu):
            group = None # not possible!
            if isinstance(_master, ContextMenu): _master = _master["mainSubMenu"]
            self._data = {"master":_master._master, "widget":_tk_.Button(_master._master._get()), "instanceOfMenu":True}
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

        @param col: Use Color enum, tkinter string or hex-code.
        @return:
        """
        self._setAttribute("activebackground", col.value if hasattr(col, "value") else col)
        return self
    def setActiveFg(self, col:Color):
        """
        Set the active foreground color.
        Visible if button is pressed.

        @param col: Use Color enum, tkinter string or hex-code.
        @return:
        """
        self._setAttribute("activeforeground", col.value if hasattr(col, "value") else col)
        return self
    def setStyleOnHover(self, style:Style):
        """
        Changes the Style on hover.
        Use the Style enum to change.
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
class OnOffButton(Widget):
    """
    Widget:
    This is a custom Widget.
    This widget represents a Button wich can be toggled on and off.
    """
    def __init__(self, _master, group=None, text="", default=False, colorsActive=True, reliefActive=False):
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master":_master,  "text":text, "widget":_tk_.Button(_master._get()), "value":default, "relief":reliefActive, "color":colorsActive, "onText":None, "offText":None, "init":{"text":text}}
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
class Entry(Widget):
    """
    Widget:
    The Entry is used to ask single line text from the user.
    """
    def __init__(self, _master, group=None):
        self.getValue = self.getText
        self.setValue = self.setText
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master":_master,  "widget":_tk_.Entry(_master._get())}
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
        sc["widget"]["orient"] = _tk_.HORIZONTAL
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
    def clear(self):
        """
        Clears the Entry.
        @return:
        """
        self["widget"].delete(0, _tk_.END)
        return self
    def setText(self, text:str):
        """
        Overwrites the text content in the Entry.
        @param text:
        @return:
        """
        self.clear()
        self["widget"].insert(0, str(text))
        return self
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
    def _decryptEvent(self, args):
        return args
    def _scrollHandler(self, *l):
        op, howMany = l[0], l[1]
        if op == 'scroll':
            units = l[2]
            self["widget"].xview_scroll(howMany, units)
        elif op == 'moveto':
            self["widget"].xview_moveto(howMany)
class TextEntry(LabelFrame):
    """
    Widget:
    This is a Custom Widget.
    An Entry and a Label are combined.
    Used to give the user a hint, what to write in the Entry.
    Important: First set the Text and THEN place the widget.
    """
    def __init__(self, _master, group=None, text=""):
        super().__init__(_master, group)

        if isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            _data = {"value":"", "label":Label(self, group), "entry":Entry(self, group)}
            _data["label"].setText(text)
            self._addData(_data)
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__.__name__))
    def bind(self, func:callable, event: Union[EventType, Key, Mouse, str], args:list=None, priority:int=0, defaultArgs=False, disableArgs=False):
        """
        Binds a specific event to the Widget. Runs given function on trigger.

        @param func: function get called on trigger
        @param event: Event type: EventType enum or default tkinter event as string.
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
        return self["entry"]
    def getLabel(self)->Label:
        """
        Returns the sub Label.
        Used for further configuration.
        @return:
        """
        return self["label"]
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
        return self["widget"]
class TextDropdownMenu(Widget):
    """
    Widget:
    This is a Custom Widget.
    DropdownMenu and Label combination.
    Used to give the user a hint, what to write/select in the DropdownMenu.
    Important: First set the Text and THEN place the widget.
    """
    def __init__(self, _master, group=None, text=""):
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
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
        @param event:  Event type: EventType enum or default tkinter event as string.
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
class Listbox(Widget):
    """
    Widget:
    The user can select one (Default) or multiple items.
    A Scrollbar can also be added.

    """
    def __init__(self, _master, group=None):
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master":_master,  "widget":_tk_.Listbox(_master._get()), "selectionMode":"single", "init":{"selectmode":"single"}, "default_color":Color.DEFAULT}
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
        sc["widget"]["orient"] = _tk_.VERTICAL
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
        return self
    def setSingleSelect(self):
        """
        Set the Listbox in 'singleselectmode'.
        The User can select only one item.
        This is the DEFAULT mode.
        @return:
        """
        self._setAttribute("selectmode", "single")
        return self
    def add(self, entry:str, index = "end", color:Union[Color, str]=None):
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
    def addAll(self, entry:[str], index="end", color:Union[Color, str]=None):
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
        self["widget"].delete(0, _tk_.END)
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
        if self["selectionMode"] == "single":
            if len(self["widget"].curselection()) == 0: return None
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
    def _decryptEvent(self, args):
        try:
            w = args.widget
            if self["selectionMode"] == "single":
                return w.get(int(w.curselection()[0]))
            else:
                return [w.get(int(i)) for i in w.curselection()]
        except:
            return "CANCEL"
class Scale(Widget):
    """
    Widget:
    Adds a Slider to set values from specified value range.
    """
    def __init__(self, _master, group=None, from_=0, to=100, orient:Orient=Orient.HORIZONTAL):
        self.setResolution = self.setSteps
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            doubbleVar = _tk_.DoubleVar(_master._get())
            self._data = {"master":_master,  "widget":_tk_.Scale(_master._get()), "var":doubbleVar, "init":{"variable":doubbleVar, "from_":from_, "to":to, "orient":orient.value if hasattr(orient, "value") else orient}}
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
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master":_master,  "widget":ttk.Progressbar(_master._get()), "values":values, "value":0}
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
        Set the Processbar orientation using the Orient enum.
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
class _ScrolledText(_tk_.Text):
    """
    Private implementation of tkinter.scrolledtext.ScrolledText

    use ttk.Scrollbar

    """
    def __init__(self, master=None, **kw):
        self.frame = _tk_.Frame(master)
        self.vbar = ttk.Scrollbar(self.frame)
        self.vbar.pack(side=_tk_.RIGHT, fill=_tk_.Y)

        kw.update({'yscrollcommand': self.vbar.set})
        _tk_.Text.__init__(self, self.frame, **kw)
        self.pack(side=_tk_.LEFT, fill=_tk_.BOTH, expand=True)
        self.vbar['command'] = self.yview
        # hack by https://github.com/enthought/Python-2.7.3/blob/master/Lib/lib-tk/ScrolledText.py
        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        text_meths = vars(Text).keys()
        methods = vars(_tk_.Pack).keys() | vars(_tk_.Grid).keys() | vars(_tk_.Place).keys()
        methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))
    def __str__(self):
        return str(self.frame)
class Text(Widget):
    """
    Widget:
    Textbox where the user can input Text.
    Can also be user to display multiline text.
    Text widget can be made read only.
    Colors and font can be changed individually.
    """
    def __init__(self, _master, group=None, readOnly=False, forceScroll=False, scrollAble=False):
        self.getContent = self.getText
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master": _master,  "widget": _ScrolledText(_master._get()) if scrollAble else _tk_.Text(_master._get()), "forceScroll":forceScroll, "tagCounter":0, "scrollable":scrollAble, "init":{"state":"disabled" if readOnly else "normal"}}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def addLine(self, text:str, color:Union[Color, str]="black"):
        """
        Adds a Line of text to the Textbox widget.
        @param text:
        @param color: color of that line. Default: BLACK
        @return:
        """
        if not text.endswith("\n"): text = text+"\n"
        self.addText(text, color)
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
                _id = "".join([choice(ascii_lowercase) for _ in range(30)])
                self["widget"].tag_add(_id, firstMarker, secondMarker)
                self["widget"].tag_config(_id, foreground=colors[textSection[0]].value)
            else:
                print(f"'{textSection}' has no valid color tag.")
            firstMarkerChar = int(secondMarker.split(".")[1])  # += len(textSection.split("\n")[-1])-1


    def setText(self, text:str):
        """
        Overwrites the text with 'text'.
        @param text:
        @return:
        """
        self.clear()
        self.addText(text)
        return self


    def addText(self, text:str, color:Union[Color, str]="black"):
        """
        Adds text to the Text box.
        Can be colored. Default: BLACK
        @param text:
        @param color:
        @return:
        """
        color = color.value if hasattr(color, "value") else color
        disableAfterWrite=False
        #if text.endswith("\n"):
            #text = text[0:-1]
        self["tagCounter"]+=1
        if self["widgetProperties"]["state"] == "disabled":
            self.setEnabled()
            disableAfterWrite = True
        self["widget"].insert("end", str(text)) # changed: removed /n
        if color != "black":
            self["widget"].tag_add(str(self["tagCounter"]), str(self["tagCounter"])+".0", "end")
            self["widget"].tag_config(str(self["tagCounter"]), foreground=color)
        if self["forceScroll"]:
            self["widget"].see("end")
        self["tagCounter"]+=text.count("\n")
        if disableAfterWrite:
            self.setDisabled()
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
    def clear(self):
        """
        Clears the Textbox.
        @return:
        """
        disableAfterWrite = False
        if self["widgetProperties"]["state"] == "disabled":
            self.setEnabled()
            disableAfterWrite = True
        self["widget"].delete(0.0, _tk_.END)
        for i in self["widget"].tag_names():
            self["widget"].tag_delete(i)
        self["tagCounter"] = 0
        if disableAfterWrite:
            self.setDisabled()
        return self
    def getSelectedText(self)->Union[str, None]:
        """
        Returns the selected text.
        Returns None if no text is selected.
        @return:
        """
        try:
            return self["widget"].get("sel.first", "sel.last")
        except _tk_.TclError:
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
        Set text wrapping using 'Wrap' enum.
        Default: NONE
        @param w:
        @return:
        """
        self._setAttribute("wrap", w.value if hasattr(w, "value") else w)
        return self
    def _decryptEvent(self, args):
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
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master": _master,  "widget":ttk.Treeview(_master._get()), "headers":[], "elements":[], "onHeaderClick":None, "use_index":False}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def onDoubleSelectEvent(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False):
        _EventHandler._registerNewEvent(self, func, Mouse.DOUBBLE_LEFT, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs, decryptValueFunc=self._decryptEvent)
    def onSingleSelectEvent(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False):
        _EventHandler._registerNewEvent(self, func, Mouse.LEFT_CLICK_RELEASE, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs, decryptValueFunc=self.__decryptEvent)
    def onArrowKeySelectEvent(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False, bindToOtherWidget=None):
        widget = self
        if bindToOtherWidget is not None:
            widget = bindToOtherWidget

        _EventHandler._registerNewEvent(widget, func, EventType.KEY_UP + EventType.ARROW_UP, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs, decryptValueFunc=self.__decryptEvent)
        _EventHandler._registerNewEvent(widget, func, EventType.KEY_UP + EventType.ARROW_DOWN, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs, decryptValueFunc=self.__decryptEvent)
    def attachVerticalScrollBar(self, sc: ScrollBar):
        self["yScrollbar"] = sc
        sc["widget"]["orient"] = _tk_.VERTICAL
        sc["widget"]["command"] = self["widget"].yview
        self["widget"]["yscrollcommand"] = sc["widget"].set
        return self
    def _decryptEvent(self, args):
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
    def __decryptEvent(self, args):
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
    def getSelectedItems(self)->list:
        return self._decryptEvent(None)
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
        return self
    def setSingleSelect(self):
        self._setAttribute("selectmode", "browse")
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
    def getSelectedIndex(self):
        if self["widget"]["selectmode"] == "browse":
            if len(self["widget"].curselection()) == 0: return -1
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
class SpinBox(Widget):
    def __init__(self, _master, group=None, optionList:list=(), readOnly=True):
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame):
            self._data = {"master": _master,  "widget": _tk_.Spinbox(_master._get()), "readonly":readOnly, "init":{"state":"readonly" if readOnly else "normal", "values":list(optionList)}}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + ", Frame or Tk instance not: " + str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
    def onButtonClick(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False):
        _EventHandler._registerNewCommand(self, func, args, priority, defaultArgs=defaultArgs, disableArgs=disableArgs, decryptValueFunc=self._decryptEvent)
    def onUserInputEvent(self, func, args:list=None, priority:int=0, defaultArgs=False, disableArgs=False):
        _EventHandler._registerNewEvent(self, func, EventType.KEY_UP, args, priority, decryptValueFunc=self._decryptEvent, defaultArgs=defaultArgs, disableArgs=disableArgs)
    def setValue(self, v, clearFirst=True):
        disableAfterWrite = False
        if self["readonly"]:
            disableAfterWrite = True
            self.setEnabled()
        if clearFirst: self.clear()
        self["widget"].insert(0, str(v))
        if disableAfterWrite:
            self._setAttribute("state", "readonly")
        return self
    def getValue(self)->str:
        return self["widget"].get()
    def setOptionList(self, l:list):
        disableAfterWrite = False
        if self["readonly"]:
            disableAfterWrite = True
            self.setEnabled()
        self._setAttribute("values", l)
        if disableAfterWrite:
            self._setAttribute("state", "readonly")
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
    def _decryptEvent(self, args):
        return self.getValue()
class DropdownMenu(Widget):
    def __init__(self, _master, group=None, optionList:list=[], readonly=True):
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            stringVar = _tk_.StringVar()
            self._data = {"master": _master,  "widget":ttk.Combobox(_master._get(), textvariable=stringVar), "values":optionList, "stringVar":stringVar, "readonly":readonly, "init":{"state":"readonly" if readonly else "normal", "values":list(optionList)}}
            self.style= ttk.Style()
            #self.style.theme_use("clam")

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
    def setValueByIndex(self, i:int):
        disableAfterWrite = False
        if self["readonly"]:
            disableAfterWrite = True
            self.setEnabled(True)
        self["widget"].current(i)
        if disableAfterWrite:
            self._setAttribute("state", "readonly")
        return self
    def clear(self):
        disableAfterWrite = False
        if self["readonly"]:
            disableAfterWrite = True
            self.setEnabled(True)
        self["widget"].delete(0, "end")
        if disableAfterWrite:
            self._setAttribute("state", "readonly")
        return self
    def setText(self, text):
        self.setValue(text)
        return self
    def setValue(self, text, clearFirst=True):
        disableAfterWrite = False
        if self["readonly"]:
            disableAfterWrite = True
            self.setEnabled(True)
        if clearFirst: self["widget"].delete(0, "end")
        self["widget"].insert(0, str(text))
        if disableAfterWrite:
            self._setAttribute("state", "readonly")
        return self
    def getValue(self):
        return self["widget"].get()
    def setOptionList(self, l:Iterable):
        self["values"] = list(l)
        disableAfterWrite = False
        if self["readonly"]:
            disableAfterWrite = True
            self.setEnabled(True)
        self._setAttribute("values", l)
        if disableAfterWrite:
            self._setAttribute("state", "readonly")
        return self
    def addOption(self, i:str):
        self["values"].append(i)
        self.setOptionList(self["values"])
        return self
    def setBg(self, col:Union[Color, str]):
        disableAfterWrite = False
        if self["readonly"]:
            disableAfterWrite = True
            self.setEnabled(True)
        self.style.map("TCombobox", fieldbackground="red")#(col.value if hasattr(col, "value") else col)
        if disableAfterWrite:
            self._setAttribute("state", "readonly")
        return self
    def _decryptEvent(self, args):
        return self["widget"].get()
    def _decryptEvent2(self, args):
        return args
class Separator(Widget):
    def __init__(self, _master, group=None):
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master": _master,  "widget":ttk.Separator(_master._get())}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be "+str(self.__class__.__name__)+", Frame or Tk instance not: "+str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
class TaskBar(Widget):
    def __init__(self, _master, group=None):
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            if _master["hasMenu"]: raise RuntimeError("You cannot apply two Menus to the Window!") #@TODO Runtime ???
            _master["hasMenu"] = True
            self._data = {"master": _master,  "widget": _tk_.Menu(_master._get(), tearoff=False), "subMenu":[], "group":group}
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
        self._id = "".join([str(randint(0,9)) for _ in range(15)])
        self._widgets = [] #[["command", <type: Button>], ["cascade", <type: Button>, <type: SubMenu>]]
        self._data = _data
        self._name = name
        self._group = group
        self._data["created"] = False
        self._master = master
        self._masterMenu = menu
        self._menu = _tk_.Menu(menu, tearoff=False)
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
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif hasattr(_master, "_get"):
            self._data = {"master": _master,  "widget": _tk_.Menu(_master._get(), tearoff=0), "subMenu":[], "closable":closable, "eventType":eventType, "group":group}
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
    def _decryptEvent(self, e):
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
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master": notebook, "widget": _tk_.Frame(notebook._get()), "tabWidget": notebook, "tabId": None, "name":name}
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
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master":_master,  "widget":ttk.Notebook(_master._get()), "tabIndexList":[], "runnable":None, "group":group, "init":{"func":self._init, "style":"CustomNotebook" if closable else ""}}
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
    def _decryptEvent(self, args):
        return self.getSelectedTabIndex()
    def _initializeCustomStyle(self):
        style = ttk.Style()
        self.images = (
            _tk_.PhotoImage("img_close",
                          data="R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs="),
            _tk_.PhotoImage("img_closeactive",
                          data="R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs="),
            _tk_.PhotoImage("img_closepressed",
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
        for widget in Tk._getAllChildWidgets(self["tabIndexList"][e.getValue() if hasattr(e, "getValue") else e]):
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

class Canvas(Widget):
    def __init__(self, _master, group=None):
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Tk) or isinstance(_master, NotebookTab) or isinstance(_master, Canvas) or isinstance(_master, Frame) or isinstance(_master, LabelFrame):
            self._data = {"master": _master, "widget": _tk_.Canvas(_master._get()), "canObjs":{}}
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
            self._data["id"] = "".join([str(randint(0,9)) for _ in range(15)])
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
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Canvas):
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
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Canvas):
            self._data = {"master": _master, "objID":None, "widget":None, "type":"rectangle", "_data":{}}
        else:
            raise TKExceptions.InvalidWidgetTypeException("_master must be " + str(self.__class__.__name__) + " instance or Canvas not: " + str(_master.__class__.__name__))
        super().__init__(self, self._data, group)
class CanvasCircle(CanvasObject):
    def __init__(self, _master=None, group=None):
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Canvas):
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
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Canvas):
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
        if isinstance(_master, dict):
            self._data = _master
        elif isinstance(_master, self.__class__):
            self._data = _master._data
        elif isinstance(_master, Canvas):
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

class FileDialog:
    @staticmethod
    def openFile(master=None, title=None, initialpath=None, types=None):
        if types is None:
            types = []
        return FileDialog._dialog(fd.askopenfilename, master=master, title=title, initialpath=initialpath, types=types)
    @staticmethod
    def openDirectory(master=None, title=None, initialpath=None):
        return FileDialog._dialog(fd.askdirectory, master=master, title=title, initialpath=initialpath)
    @staticmethod
    def saveFile(master=None, title=None, initialpath=None, types:list=None):
        if types is None:
            types = []
        return FileDialog._dialog(fd.asksaveasfilename, master=master, title=title, initialpath=initialpath, types=types)
    @staticmethod
    def _dialog(func, master=None, title=None, initialpath=None, types=None):
        if types is None:
            types = []
        destroy=False
        _types = (("", "",), ("", "",))
        if type(types) == list:
            for i in types:
                if str(i).startswith("."):
                    _types += (("", "*"+str(i),),)
                elif str(i).startswith("*."):
                    _types += (("", str(i),),)
                else:
                    raise TKExceptions.InvalidFileExtention(str(i)+" is not a valid Extention! Use .<ext>!")
        _data = {"title":str(title),
                "initialdir":initialpath}
        if func != fd.askdirectory: _data["filetypes"] = _types
        if initialpath is not None and os.path.split(initialpath)[1]!="" and False:# Disabled
            _data["initialfile"] = os.path.split(initialpath)[1]
        if master is None:
            destroy = True
            master = Tk()
            master.hide()
            _data["parent"] = master._get()

        #_data["filetypes"] = (('', ''), ('', ''), ('', '*.jpg'), ('', '*.png'), ('', '*.jpeg'), ('', '*.ppm'), ('', '*.gif'))

        path = func(**_data)
        if destroy: master.destroy()
        if path == "" or path is None:
            return None
        return path
class SimpleDialog:
    @staticmethod
    def askYesNo(master, message="", title=""):
        return SimpleDialog._dialog(msg.askyesno, master, message=message, title=title)
    @staticmethod
    def askYesNoCancel(master, message="", title=""):
        """
        yes    -> True
        no     -> False
        cancel -> None
        @param master:
        @param message:
        @param title:
        @return:
        """
        return SimpleDialog._dialog(msg.askyesnocancel, master, message=message, title=title)
    @staticmethod
    def askOkayCancel(master, message="", title=""):
        """

        @rtype: object
        @param master:
        @param message:
        @param title:
        @return: True or False
        """
        return SimpleDialog._dialog(msg.askokcancel, master, message=message, title=title)
    @staticmethod
    def askRetryCancel(master, message="", title=""):
        return SimpleDialog._dialog(msg.askretrycancel, master, message=message, title=title)
    @staticmethod
    def askInfo(master, message="", title=""):
        return SimpleDialog._dialog(msg.showinfo, master, message=message, title=title)
    @staticmethod
    def askError(master, message="", title=""):
        return SimpleDialog._dialog(msg.showerror, master, message=message, title=title)
    @staticmethod
    def askWarning(master, message="", title=""):
        return SimpleDialog._dialog(msg.showwarning, master, message=message, title=title)
    @staticmethod
    def askString(master, message="", title="", initialValue="", hideWith=None):
        return SimpleDialog._dialog(simd.askstring, master, prompt=message, title=title, show=hideWith, initialvalue=initialValue)
    @staticmethod
    def askInteger(master, message="", title="", initialValue=""):
        return SimpleDialog._dialog(simd.askinteger, master, prompt=message, title=title)
    @staticmethod
    def askFloat(master, message="", title="", initialValue=""):
        return SimpleDialog._dialog(simd.askfloat, master, prompt=message, title=title)
    @staticmethod
    def askUsernamePassword(master, title="", initialUname="", initialPassw="", unameString="Username:", passwString="Password:", hidePassword=True, default=None, group=None):
        _return = None
        _masterNone = False

        def cancel(e):
            nonlocal _return
            _return = "None"
        def select(e):
            nonlocal _return
            un = unE.getValue()
            pw = pwE.getValue()
            _return = [un, pw]

        def onClose():
            nonlocal _return
            _return = "None"

        if master is None:
            _masterNone = True
            master = Tk()
            master.hide()
        dialog = Dialog(master, group=group)
        dialog.setTitle(title)
        dialog.setResizeable(False)
        dialog.setWindowSize(200, 125)
        dialog.onCloseEvent(onClose)
        dialog.bind(select, EventType.RETURN)
        dialog.bind(cancel, EventType.ESC)

        unL = Label(dialog, group=group).placeRelative(fixY=0, fixHeight=25, centerX=True, fixWidth=100).setText(unameString)
        unE = Entry(dialog, group=group).placeRelative(fixY=25, fixHeight=25, centerX=True, fixWidth=100).setValue(initialUname)
        pwL = Label(dialog, group=group).placeRelative(fixY=50, fixHeight=25, centerX=True, fixWidth=100).setText(passwString)
        pwE = Entry(dialog, group=group).placeRelative(fixY=75, fixHeight=25, centerX=True, fixWidth=100).setValue(initialPassw)
        if hidePassword: pwE.hideCharactersWith("*")

        cancB = Button(dialog, group=group).setCommand(cancel).placeRelative(fixY=100, fixHeight=25, xOffsetLeft=50).setText("Cancel")
        okB = Button(dialog, group=group).setCommand(select).placeRelative(fixY=100, fixHeight=25, xOffsetRight=50).setText("OK")

        dialog.show()
        while True:
            master.update()
            sleep(.1)
            if _return == "None":
                if _masterNone: master.destroy()
                dialog.destroy()
                return None if default is None else default
            elif isinstance(_return, list):
                if _masterNone: master.destroy()
                dialog.destroy()
                return _return
    @staticmethod
    def chooseFromList(master, title="", values=None, chooseOnlyOne=True, forceToChoose=True)->str | list | None:
        _return = None
        _masterNone = False

        def cancel(e):
            nonlocal _return
            _return = "None"
        def select(e):
            nonlocal _return
            sel = list_.getSelectedItem()
            if sel is None:
                if forceToChoose:
                    SimpleDialog.askError(dialog, "Please choose at least one!")
                else:
                    _return = "None"
            else:
                _return = [sel] if not isinstance(sel, list) else sel
        def onClose():
            nonlocal _return
            if not forceToChoose:
                _return = "None"

        if master is None:
            _masterNone = True
            master = Tk()
            master.hide()

        dialog = Dialog(master)
        dialog.onCloseEvent(onClose)
        if forceToChoose:
            dialog.setCloseable(False)
        dialog.setWindowSize(200, 200)
        dialog.setResizeable(False)
        dialog.setTitle(title)
        list_ = Listbox(dialog)
        if chooseOnlyOne:
            list_.setSingleSelect()
        else:
            list_.setMultipleSelect()
        list_.addAll(values)
        list_.placeRelative(changeHeight=-30)
        list_.bind(select, EventType.DOUBBLE_LEFT)

        Button(dialog).setText("Select").placeRelative(stickDown=True, fixHeight=30, xOffsetRight=50).setCommand(select)
        canc = Button(dialog).setText("Cancel").placeRelative(stickDown=True, stickRight=True, fixHeight=30, xOffsetRight=50).setCommand(cancel)
        if forceToChoose: canc.disable()
        dialog.show()
        while True:
            master.update()
            sleep(.1)
            if _return == "None":
                dialog.destroy()
                if _masterNone: master.destroy()
                return None
            elif isinstance(_return, list):
                dialog.destroy()
                if _masterNone: master.destroy()
                return _return
    @staticmethod
    def _dialog(d, master, **kwargs):
        if isinstance(master, Tk):
            if kwargs["title"] == "":
                kwargs["title"] = master["title"]
            return d(parent=master._get(), **kwargs)
        else:
            mas = Tk()
            mas.hide()
            anw = d(parent=mas._get(), **kwargs)
            mas.destroy()
            return anw
class ColorChooser:
    def __init__(self, c):
        self._c = c
    def getCanceled(self):
        return self._c == (None, None)
    def getHex(self):
        return self._c[1]
    def getRGB(self):
        return self._c[0]
    def __str__(self):
        return self.getRGB()
    @staticmethod
    def askColor(master=None, initialcolor=None, title=""):
        if isinstance(master, Tk):
            if initialcolor == "": initialcolor = None
            return ColorChooser(colorChooser.askcolor(initialcolor=initialcolor.value if hasattr(initialcolor, "value") else initialcolor, parent=master._get(), title=str(title)))
        else:
            mas = Tk()
            mas.hide()
            anw = ColorChooser(colorChooser.askcolor(initialcolor=initialcolor.value if hasattr(initialcolor, "value") else master, parent=mas._get(), title=title))
            mas.destroy()
            return anw

class MenuPage(Frame):
    def __init__(self, master, group=None, homeScreen=False):
        super().__init__(master, group)
        self._menuData = {
            "home_screen":homeScreen,
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

#redundant class names
Combobox = DropdownMenu
Menu = TaskBar