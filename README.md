# kommandozentrale
Das hier wird die Steuereinheit des Maschinendecks!

## Extending

To add new switches to your kommandozentrale, simply add a new one to `config.json`. Every switch in config.json (attribute `switches`) needs to have at least a `class`-attribute, telling it which of `switch_classes.py`s classes is uses. It can also have `initial_data`-attribute, giving information to the switch, for example GPIO-Pins etc. If your switch doesn't match the ones already defined in `switch_classes.py`, you can easily add one. Each switch must:

- have an `__init__` function, which accepts the argument `initial_data` and any keyword arguments.
- have a `getModules` function, returning a list of tuples of all functions which should be advertised to the clients and a dict of information for the client
- have a `getState` function, which returns the current state
- store its state, if it can't get it easily, because the class is reinitilized on every call (might change in the future)

`switch_classes.py` contains a `SwitchClass` which contains some convenience methods for creating new switch classes. It provides an `__init__`, `getState` and `getModules` function which satify the above. `getModules` returns all functions which have an attribute `is_public` which is set to `True` (`decorators.py` contains a `publicMethod` which you can use. `getModules` loads the client infomation from `switch.client_information`. `SwitchClass` also contains a `setState` which sets `self.state` to the passed state and stores the state in a shelve-store named `kommanozentrale.db`. In it there is a `loadState` function which gets the current state from the shelve-store, too.

## Licence

This project is under a GPL license (see LICENSE), unless otherwise indicated in the file.