from threading import Thread
from types import FunctionType, MethodType
from time import time, sleep
import tkinter as _tk
import tkinter.font as _font
import tkinter.ttk as _ttk
from random import randint as _randint
from typing import Union, Callable

from .const import *


_WATCHER = None

class Font:
    def __init__(self, size:int=10, family:FontType=FontType.ARIAL, bold:bool=False, italic:bool=False, underline:bool=False, overstrike:bool=False):
        self._data = {
            "size":size,
            "family":remEnum(family),
            "bold":'bold' if bold else 'normal',
            "slant":'italic' if italic else'roman',
            "underline":underline,
            "overstrike":overstrike
        }
        self._font = _font.Font()
        self._state = False
    def setSize(self, i:int):
        self._data["size"] = int(i)
        self._state = False
        return self
    def setFontType(self, family:Union[FontType, str]):
        self._data["family"] = remEnum(family),
        self._state = False
        return self
    def setWeight(self, w:bool=True):
        self._data["weight"] = 'bold' if w else 'normal'
        self._state = False
        return self
    def setItalic(self, w:bool=True):
        self._data["slant"] = 'italic' if w else'roman'
        self._state = False
        return self
    def setUnderline(self, w:bool=True):
        self._data["underline"] = w
        self._state = False
        return self
    def setOverstrike(self, w:bool=True):
        self._data["overstrike"] = w
        self._state = False
        return self

    def updateFont(self):
        self._font.configure(**self._data)
        self._state = True
    def _get(self):
        if not self._state:
            self.updateFont()
        return self._font
def remEnum(val):
    return val.value if hasattr(val, "value") else val
def ifIsNone(valA, valB):
    return valA if valA is not None else valB
def _isinstanceAny(cls, *names):
    for name in names:
        if _isinstance(cls, name): return True
    return False
def _isinstance(cls, name):
    if cls is None: return False
    if type(name) is not str: return isinstance(cls, name)
    if cls.__class__.__name__ in name: return True
    clazz = cls.__class__.__base__
    classList = [clazz.__name__]
    while True:
        clazz = clazz.__base__
        if clazz is None: return False
        if clazz is object: break
        classList.append(clazz.__name__)
    return name in classList
def _lockable(func):
    """
    Decorator for locking Widgets which can be disabled.
    """
    disableArgs = _checkMethod(func, mustHaveArgs=1)
    def _callable(*args, **kwargs):
        obj = args[0]
        if _isinstance(obj, "_LockableWidget"):
            obj._unlock()
            try:
                if disableArgs:
                    retVal = func(*(args[:1]), **kwargs)
                else:
                    retVal = func(*args, **kwargs)
            except Exception as e:
                obj._lock()
                raise e
            obj._lock()
            return retVal
        return func(*args, **kwargs)
    return _callable
def _checkMethod(func, event=None, mustHaveArgs=0):
    if func is None: return
    if not hasattr(func, "__code__"): return
    if event is not None and event["disableArgs"]: return

    argCount:int = func.__code__.co_argcount

    if isinstance(func, FunctionType) and argCount == mustHaveArgs:
        if event is not None: event["disableArgs"] = True
        return True
    elif isinstance(func, MethodType) and argCount == mustHaveArgs+1:
        if event is not None: event["disableArgs"] = True
        return True
    return False
def enableRelativePlaceOptimization(runEvySec=2, runSecAftr=.2):
    global _WATCHER
    assert _WATCHER is None, "Relative Place Optimization cannot enabled twice!"
    _WATCHER = _RunWatcher()
    _RunWatcher._runEverySecond = runEvySec
    _RunWatcher._runAfterSecond = runSecAftr
    _WATCHER.start()
class _RunWatcher(Thread):
    _runEverySecond=None
    _runAfterSecond=None
    _queue = []
    def __init__(self):
        super().__init__(daemon=True)
    @staticmethod
    def runFunc(func, args):
        return func(*args)
    def run(self):
        while True:
            sleep(.1)
            if not _RunWatcher._queue: continue
            for i, j in enumerate(_RunWatcher._queue):
                if j is None: continue
                if time() - j[0] >= _RunWatcher._runAfterSecond:
                    _RunWatcher.runFunc(j[1], j[2])
                    _RunWatcher._queue[i] = None

    @staticmethod
    def register()->int:
        _RunWatcher._queue.append(None)
        return len(_RunWatcher._queue)-1
    @staticmethod
    def runWatcher(func):
        _id = _RunWatcher.register()
        _hook = None
        _timer = None
        def watcher(*args):
            if _RunWatcher._runAfterSecond is None:
                return func(*args)
            nonlocal _timer
            _RunWatcher._queue[_id] = (time(), func, args)
            if _timer is None:
                _timer = time()
                _RunWatcher._queue[_id] = None
                return _RunWatcher.runFunc(func, args)
            elif time() - _timer >= _RunWatcher._runEverySecond:
                _timer = time()
                _RunWatcher._queue[_id] = None
                return _RunWatcher.runFunc(func, args)
            return None
        _hook = func
        return watcher
runWatcherDec = _RunWatcher.runWatcher
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
        self._intvar = _tk.IntVar(_master._get())
    def _add(self):
        self.index +=1
        return self.index
    def _get(self):
        return self._intvar
    def get(self):
        return self._intvar.get()
    def set(self, v:int):
        self._intvar.set(v)
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
        WidgetGroup._GROUPS.append(self)
    def add(self, w):
        """
        Adds widget w to this group.

        @param w:
        @return:
        """
        if w is None: return
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
    def executeCommand(self, cmd:str, *args, ignoreErrors=False):
        for w in self._widgets:
            try:
                if cmd == "@custom":
                    args[0](w)
                else:
                    getattr(w, cmd)(*args)
            except Exception as e:
                if ignoreErrors: continue
                raise Exception(f"Error while execute '{cmd}' command on [{len(self._widgets)}].\nType: {type(w)}, Error: {e}")

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
    """
    Places widgets:

    Use as following example:

    xPlacer = Placer(50)

    .place(0, xPlacer.get(), 100, 50)
    .place(0, xPlacer.get(), 100, 50)
    .place(0, xPlacer.get(), 100, 50)
    .place(0, xPlacer.get(), 100, 50)


    """
    def __init__(self, ySpace, yStart=0):
        self._ySpace = ySpace
        self._yStart = yStart
    def get(self):
        x = self._yStart
        self._yStart += self._ySpace
        return x
class StyleBuilder:
    _STYLE = None
    def __init__(self):
        if StyleBuilder._STYLE is None: StyleBuilder._STYLE = _ttk.Style
        self._id = "".join([str(_randint(0,9)) for _ in range(15)])
        self._settings = {}

    def TProcessbar(self):
        pass

        return self

    def build(self)->str:
        StyleBuilder._STYLE.theme_create(self._id, parent="alt", settings=self._settings)
        return self._id

    @staticmethod
    def applyTheme(id_:str):
        assert StyleBuilder._STYLE is not None, "There is no Style created yet!"
        StyleBuilder._STYLE.theme_use(id_)
class State:
    """
    Use as following example:

    state = State()
    frame.bind(state.set, EventType.ENTER)
    frame.bind(state.unset, EventType.LEAVE)
    """
    def __init__(self, default=False):
        self._state = default
    def set(self):
        self._state = True
    def unset(self):
        self._state = False
    def get(self):
        return self._state
    def __bool__(self):
        return self._state
    def __eq__(self, other):
        return self._state == other
    def __ne__(self, other):
        return self._state != other
class Toggler:
    """
    calls hook with value.
    toggles that value on each call.

    Use as following example:

    toggler = Toggler(print, initial=True)
    .bind(toggler, ...)

        True
        False
        ...

    """
    def __init__(self, func:Callable, initial=False):
        self._func = func
        self._state = initial
    def __call__(self, *args, **kwargs):
        self._state = not self._state
        return self._func(self._state)
class CustomRunnable:
    """
    Custom Runnable.
    It forces to pass exactly the augments that are given to the __init__.

    Use as following example:

    runnable = CustomRunnable(print, "hello")

    runnable() or .bind(runnable, ...)

        'hello'
    """
    def __init__(self, command, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.command = command
    def __call__(self, *args, **kwargs):
        self.command(*self.args, **self.kwargs)
