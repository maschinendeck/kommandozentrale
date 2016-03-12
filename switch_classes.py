import shelve
from decorators import publicMethod
from mpd import MPDClient

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
                client_information = self.getMethodClientInformation(method)
                methods.append((method_name,client_information))
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

    def getMetaData(self):
        metadata = {}
        if hasattr(self, "metadata"):
            metadata = self.metadata
        if hasattr(self, "class_metadata"):
            metadata.update(self.class_metadata)
        return metadata

    def getMethodClientInformation(self, method):
        if hasattr(method, "client_information"):
            return method.client_information
        else:
            return {}

class ExampleOnOffSwitch(SwitchClass):
    class_metadata = {"type":"bool"}
    @publicMethod
    def on(self):
        self.setState(True)
        return self.state

    @publicMethod
    def off(self):
        self.setState(False)
        return self.state

class LightSwitch(SwitchClass):
    class_metadata = {"type":"bool"}
    @publicMethod
    def on(self):
        self.setState(True)
        return self.state

    @publicMethod
    def off(self):
        self.setState(False)
        return self.state


class MPDSwitch(SwitchClass):
    class_metadata = {"type":"music"}
    client = None
    state = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.getMPDClient()
        self.poll()

    def getMPDClient(self):
        if self.client == None:
            self.client = MPDClient()
            self.client.connect("localhost", 6600)
        else:
            try:
                self.client.ping()
            except ConnectionError as e:
                self.client = None
                self.getMPDClient()

    def poll(self):
        """ This function calls itself every second to check for config changes """
        self.getMPDClient()
        state = self.getState()
        if self.state != state:
            self.state = state
            state = self.getState()
            metadata = self.getMetaData()
            res = {"result":"state", "switch":self.name, "state":state, "metadata":metadata}
            self.factory.broadcast(res)

        self.factory.loop.call_later(1, self.poll)


    def close(self):
        self.client.close()
        self.client.disconnect()

    def getCurrentSong(self):
        song = self.client.currentsong()
        song_str = "{artist} - {album}: {title}".format(**song)
        return song_str

    def getState(self):
        self.getMPDClient()
        state = self.getCurrentSong()
        return state

    @publicMethod
    def next(self):
        self.getMPDClient()
        self.client.next()
        return self.getState()

    @publicMethod
    def stop(self):
        self.getMPDClient()
        self.client.stop()
        return self.getState()


    @publicMethod
    def previous(self):
        self.getMPDClient()
        self.client.previous()
        return self.getState()

    @publicMethod
    def pause(self):
        self.getMPDClient()
        self.client.pause()
        return self.getState()

    @publicMethod
    def play(self):
        self.getMPDClient()
        self.client.play()
        return self.getState()