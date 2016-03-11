import asyncio
import json
import importlib

from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

from exceptions import NotAllowedException, NotFoundException

class KommandozentraleServerFactory(WebSocketServerFactory):

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)
        self.clients = []

    def register(self, client):
        if client not in self.clients:
            self.clients.append(client)

    def unregister(self, client):
        if client in self.clients:
            self.clients.remove(client)

    def broadcast(self, msg):
        if not isinstance(msg, str):
            msg = json.dumps(msg)
        msg = msg.encode("utf8")
        for c in self.clients:
            c.sendMessage(msg)


class KommandozentraleServerProtocol(WebSocketServerProtocol):
    config = {"switchModule":"switch_classes","switches": {}}


    def __init__(self, config="config.json"):
        super().__init__()
        with open(config) as configfile:
            self.config.update(json.load(configfile))
        self.config['switchModule'] = importlib.import_module(self.config['switchModule'])

    def onOpen(self):
        self.factory.register(self)

    def onClose(self, *args, **kwargs):
        WebSocketServerProtocol.onClose(self, *args, **kwargs)
        self.factory.unregister(self)


    def getSwitch(self, name):
        if name in self.config['switches']:
            switch_config = self.config['switches'][name]
            switch_class = switch_config['class']
            initial_data = switch_config
            switch = getattr(self.config["switchModule"], switch_class)(initial_data=initial_data, name=name)
            return switch
        else:
            raise NotFoundException("Switch with name {0} not found".format(name))

    def getClientConfig(self):
        client_config = {}
        for switch, data in self.config["switches"].items():
            switch_class = self.getSwitch(switch)
            methods = switch_class.getMethods()
            metadata = switch_class.getMetaData()
            state = switch_class.getState()
            client_config[switch] = {"methods":methods, "metadata":metadata, "state":state}
        return client_config

    def callMethod(self, req):
        switch = self.getSwitch(req['switch'])
        method = getattr(switch, req['method'])
        if hasattr(method, "is_public") and method.is_public:
            if "data" in req:
                method(req["data"])
            else:
                method()
            return switch.getState()
        else:
            raise NotAllowedException('Method "{0}" of switch "{1}" is not public'.format(req['method'], req['switch']))


    @asyncio.coroutine
    def onMessage(self, payload, isBinary):
        """ Handle messages """
        if not isBinary:
            try:
                req = json.loads(payload.decode('utf8'))
                if req["action"] == "call_method":
                    try:
                        state = self.callMethod(req)
                        res = {"result":"state", "switch":req["switch"], "state":state}
                        self.factory.broadcast(res)
                    except (NotAllowedException, NotFoundException) as e:
                        error = str(e)
                        res = {"result":"error", "error":error}

                elif req["action"] == "get_config":
                    client_config = self.getClientConfig()
                    res = {"result":"config", "config":client_config}

                elif req["action"] == "get_state":
                    switch = self.getSwitch(req['switch'])
                    state = switch.getState()
                    metadata = switch.getMetaData()
                    res = {"result":"state", "switch":req["switch"], "state":state, "metadata":metadata}

                else:
                    res = {"result":"error", "error":"Action not found"}


            except json.decoder.JSONDecodeError as e:
                res = {"result":"error", "error":"Couldn't decode payload"}
            self.sendMessage(json.dumps(res).encode("utf8"))



if __name__ == '__main__':

    factory = KommandozentraleServerFactory(u"ws://localhost:9000")
    factory.protocol = KommandozentraleServerProtocol

    loop = asyncio.get_event_loop()
    server = loop.create_server(factory, 'localhost', 9000)
    ruc = loop.run_until_complete(server)
    print("Started, listening on port 9000")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        ruc.close()
        loop.close()
