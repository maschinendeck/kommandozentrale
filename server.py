import asyncio
import json
import importlib

from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

from exceptions import NotAllowedException
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
        switch_config = self.config['switches'][name]
        switch_class = switch_config['class']
        initial_data = switch_config['initial_data'] if "initial_data" in switch_config else {}
        switch = getattr(self.config["switchModule"], switch_class)(initial_data=initial_data, name=name)
        return switch

    def getClientConfig(self):
        client_config = {}
        for switch, data in self.config["switches"].items():
            switch_class = self.getSwitch(switch)
            client_config[switch] = {"methods":switch_class.methods}
        return client_config

    def callMethod(self, req):
        switch = self.getSwitch(req['switch'])
        if req['method'] in switch.methods:
            method = getattr(switch, req['method'])
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
            req = json.loads(payload.decode('utf8'))

            if req["action"] == "call_method":
                try:
                    state = self.callMethod(req)
                    res = {"result":"state", "switch":req["switch"], "state":state}
                    self.factory.broadcast(res)
                except NotAllowedException as e:
                    error = repr(e)
                    res = {"result":"error", "error":error}
                self.sendMessage(json.dumps(res).encode("utf8"))

            elif req["action"] == "get_config":
                # TODO: send better config
                client_config = self.getClientConfig()
                msg = {"result":"config", "config":client_config}
                self.sendMessage(json.dumps(msg).encode("utf8"))

            elif req["action"] == "get_state":
                switch = self.getSwitch(req['switch'])
                state = switch.getState()
                res = {"result":"state", "switch":req["switch"], "state":state}
                self.sendMessage(json.dumps(res).encode("utf8"))

            else:
                msg = {"result":"error", "error":"Action not found"}
                self.sendMessage(json.dumps(msg).encode("utf8"))




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
