import shelve
from decorators import publicMethod
class SwitchClass():
    state = None
    methods = []

    def __init__(self, initial_data={}, **kwargs):
        initial_data.update(kwargs)
        for k,v in initial_data.items():
            setattr(self, k, v)
        self.state = self.loadState()

    def loadState(self):
        # get state from cache
        state = None

        with shelve.open('kommandozentrale.db') as db:
            if self.name in db:
                state = db[self.name]

        if state == None:
            self.setState(False)
        else:
            return state

    def getState(self):
        return self.state

    def setState(self, state):
        with shelve.open('kommandozentrale.db') as db:
            db[self.name] = state
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



