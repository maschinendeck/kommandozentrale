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
        with shelve.open('kommandozentrale.db') as db:
            if self.name in db:
                return db[self.name]
            else:
                self.setState(False)

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


<<<<<<< HEAD
class LightSwitch(SwitchClass):
=======
class ExampleOnOffSwitch(SwitchClass):
>>>>>>> dc2309be361e4f4e70cb56286a4e38e9c0145600
    @publicMethod
    def on(self):
        self.setState(True)
        return self.state

    @publicMethod
    def off(self):
        self.setState(False)
        return self.state



