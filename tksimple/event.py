from typing import Union, Callable

from .tkmath import Location2D
from .util import _isinstance, _checkMethod
from .const import TKExceptions, Key, EventType, Mouse



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
        if _isinstance(ins, "_Widget") or _isinstance(ins, "Tk") or _isinstance(ins, "CanvasObject"):
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
        if self.event is None: return
        def raiseError(err):
            info = f"""
\tCould not execute bound event method!
\t\tBoundTo:         '{"" if not hasattr(event["func"], "__self__") else event["func"].__self__.__class__.__name__ + "."}{event["func"] if not hasattr(event["func"], "__name__") else event["func"].__name__}' 
\t\tWidget:          '{type(event["widget"]).__name__}'
\t\tEventType:       '{event["eventType"]}'
\t\tpriority:        {event["priority"]}
\t\targs:            {event["args"]}
\t\tvalue:           {event["value"]}"""
            _max = max([len(i) for i in info.splitlines()])
            if _max < 111: _max = 111
            _info = ""
            for j, i in enumerate(info.splitlines()):
                _info += (i+ "\n")
            if type(err) == KeyError:
                print(_info)
            else:
                if len(err.args) > 0:
                    err.args = (str(_info)+str(err.args[0]),)
                else:
                    err.args = (str(_info),)

        args = args[0] if len(args) == 1 else list(args)
        event = None
        out = None
        if "widget" not in self.event._data.keys(): return #  event already dropped
        for event in self.event["widget"]._eventRegistry.getCallables(self.event["eventType"]): #TODO get only the output of the last called func. problem? maybe priorities
            func = event["func"]
            event["tkArgs"] = args
            if event["decryptValueFunc"] is not None:
                event["value"] = event["decryptValueFunc"](args, event) #TODO event in 'decryptValueFunc'
                #if event["eventType"] == "<<ListboxSelect>>":
                #    print(event._data)
                if event["value"] == "CANCEL":
                    return
            if not event["defaultArgs"]:
                if event["value"] is None:
                    if hasattr(args, "x") and hasattr(args, "y"):
                        event["pos"] = Location2D(args.x, args.y)
                args = event
            # call event
            try:
                if event["disableArgs"]:
                    out = func()
                else:
                    out = func(args)
            except Exception as e:
                raiseError(e)
                raise
            if not len(event._data): return False # destroyed
            if event["afterTriggered"] is not None: event["afterTriggered"](event, out)
        # After all events are processed
        if self.event["forceReturn"] is not None:
            return self.event["forceReturn"]
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
        @param defaultArgs: this bool decides if the 'Event' instance or the normal tkinter args are passed into the target function
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
        handler = obj._eventRegistry.addEvent(event, eventType)
        _checkMethod(func, event)
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
        handler = obj._eventRegistry.addEvent(event, "cmd")
        _checkMethod(func, event)
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
        handler = obj._eventRegistry.addEvent(event, "vcmd")
        _checkMethod(func, event)
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
        handler = obj._eventRegistry.addEvent(event, "trace")
        _checkMethod(func, event)
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
        _checkMethod(func, event)
        handler = obj._eventRegistry.addEvent(event, "runnable")
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
        handler = obj._eventRegistry.addEvent(event, eventType)
        eventType = eventType.value if hasattr(eventType, "value") else eventType
        event["handler"] = _EventHandler(event)
        _checkMethod(func, event)
        if eventType == "[relative_update]" or eventType == "[relative_update_after]":
            obj._relativePlaceData["handler"] = _EventHandler(event)


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
        handler = obj._eventRegistry.addEvent(event, eventType)
        _checkMethod(func, event)
        if handler is not None:
            obj._get().tag_bind(id_, eventType, handler)
        event["handler"] = _EventHandler(event)
