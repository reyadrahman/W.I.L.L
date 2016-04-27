import os
import sys
import importlib
from pydispatch import dispatcher
from collections import Iterable

# Events
EVT_INIT = "will_evt_init"
EVT_EXIT = "will_evt_exit"
EVT_ANY_INPUT = "will_evt_any_input"

_event_handlers = {}


def event(events):
    def subscribe(evt, func):
        dispatcher.connect(func, signal=evt)
        if event not in _event_handlers:
            _event_handlers[evt] = []
        _event_handlers[evt].append(func)

    def decorator(func):
        if not isinstance(events, str) and isinstance(events, Iterable):
            for evt in events:
                subscribe(evt, func)
        else:
            subscribe(events, func)
        return func

    return decorator


def load_plugin(path):
    file_path = os.path.abspath(path)
    lib_path = os.sep.join(file_path.split(os.sep)[:-1])

    if file_path.endswith('.py'):
        module_name = os.path.basename(file_path).split('.')[0]
    elif os.path.isdir(file_path):
        if not os.path.exists(os.path.join(file_path, '__init__.py')):
            return
        module_name = os.path.basename(file_path)
    else:
        return

    if lib_path not in sys.path:
        sys.path.append(lib_path)
    importlib.import_module(module_name)


def load_plugins(dir_path):
    dir_path = os.path.abspath(dir_path)
    map(
        lambda plugin: load_plugin(plugin),
        (os.path.join(dir_path, module_path) for module_path in os.listdir(dir_path))  # noqa
    )
    dispatcher.send(signal=EVT_INIT)


def unload_all():
    dispatcher.send(EVT_EXIT)

    # note, a copy of the _event_handlers[event] list is made here with the [:]
    # syntax as we are going to be removing event handlers from the list and
    # we can't do this while iterating over the same list.

    for event, handlers in _event_handlers.iteritems():
        for handler in handlers[:]:
            dispatcher.disconnect(handler, signal=event)
            _event_handlers[event].remove(handler)

