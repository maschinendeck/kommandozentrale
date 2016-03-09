import shelve
from decorators import publicMethod
class SwitchClass():
    state = None

    def __init__(self, initial_data={}, **kwargs):
        initial_data.update(kwargs)
        for k,v in initial_data.items():
            setattr(self, k, v)
        self.state = self.loadState()

    def loadState(self):
        # get state from cache
        state = self.getFromDatabase(self.name)

        if state == None:
            self.setState(False)
        else:
            return state

    def getState(self):
        return self.state

    def setState(self, state):
        self.saveToDatabase(self.name, state)
        self.state = state

    def getMethods(self):
        methods = []
        for method_name in dir(self):
            method = getattr(self, method_name)
            if hasattr(method, "is_public") and method.is_public:
                if hasattr(method, "client_information"):
                    methods.append((method_name,method.client_information))
                else:
                    methods.append((method_name,{}))
        return methods

    def getFromDatabase(self, key, file="kommandozentrale.db", default=None):
        with shelve.open(file) as db:
            if key in db:
                return db[key]
            else:
                return default

    def saveToDatabase(self, key, value, file="kommandozentrale.db"):
        with shelve.open(file) as db:
            db[key] = value

class ExampleOnOffSwitch(SwitchClass):
    @publicMethod
    def on(self):
        self.setState(True)
        return self.state

    @publicMethod
    def off(self):
        self.setState(False)
        return self.state

class LightSwitch(SwitchClass):
    @publicMethod
    def on(self):
        self.setState(True)
        return self.state

    @publicMethod
    def off(self):
        self.setState(False)
        return self.state



