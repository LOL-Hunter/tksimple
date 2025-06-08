from enum import Enum as _Enum

#TODO rework event enums
WIDGET_DELETE_DEBUG = False
class _Const:
    WIDGET_METHODS = []
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
class FontType(_Enum):
    """
    FontTypes _Enum
    """
    #TODO: add more font types
    ARIAL ="arial"
class Orient(_Enum):
    """
    _Enum to specify the Orientation
    """
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
class Style(_Enum):
    """
    _Enum to specify widget style.
    """
    FLAT = "flat"
    SOLID = "solid"
    RAISED = "raised"
    SUNKEN = "sunken"
    GROOVE = "groove"
    RIDGE = "ridge"
class Anchor(_Enum):
    """
    _Enum to specify the Anchor.
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
class Direction(_Enum):
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"
    NONE = "none"
    TOP = "top"
    BOTTOM = "bottom"
class Color(_Enum):
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
class Wrap(_Enum):
    NONE = "none"
    WORD = "word"
    CHAR = "char"
class Cursor(_Enum):
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
class Key(_Enum):
    SHIFT = "<Shift>"
    RETURN = "<Return>"
    DOWN = "<Down>"
    RIGHT = "<Right>"
    LEFT = "<Left>"
    UP = "<Up>"
class Mouse(_Enum):
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
class FunctionKey(_Enum):
    CONTROL = CTRL = "Control"
    ALT = "Alt"
class EventType(_Enum):

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
    F6 = "<F6>"
    F7 = "<F7>"
    F8 = "<F8>"
    F9 = "<F9>"
    F10 = "<F10>"
    F11 = "<F11>"
    F12 = "<F12>"

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
    def mouse(m: str):
        return m
    @staticmethod
    def key(k: str):
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

