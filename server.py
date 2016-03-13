import asyncio
import json
import importlib
import copy
from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

from exceptions import NotAllowedException, NotFoundException

class KommandozentraleServerFactory(WebSocketServerFactory):
    config = {"switchModule":"switch_classes","switches": {}}
    def __init__(self, url, config="config.json"):
        WebSocketServerFactory.__init__(self, url)
        self.clients = []
        with open(config) as configfile:
            self.config.update(json.load(configfile))
        self.config['switchModule'] = importlib.import_module(self.config['switchModule'])
        for name in self.config["switches"]:
            switch_config = self.config['switches'][name]
            switch_class = switch_config['class']
            initial_data = switch_config
            switch = getattr(self.config["switchModule"], switch_class)(initial_data=initial_data, name=name, factory=self)
            self.config['switches'][name]['class'] = switch


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

    def getSwitch(self, name):
        if name in self.config['switches']:
            switch_config = self.config['switches'][name]
            switch_class = switch_config['class']
            return switch_class
        else:
            raise NotFoundException("Switch with name {0} not found".format(name))

class KommandozentraleServerProtocol(WebSocketServerProtocol):

    def onOpen(self):
        self.factory.register(self)

    def onClose(self, *args, **kwargs):
        WebSocketServerProtocol.onClose(self, *args, **kwargs)
        self.factory.unregister(self)

    def getClientConfig(self):
        client_config = {}
        for switch, data in self.factory.config["switches"].items():
            switch_class = self.factory.getSwitch(switch)
            methods = switch_class.getMethods()
            metadata = switch_class.getMetaData()
            state = switch_class.getState()
            client_config[switch] = {"methods":methods, "metadata":metadata, "state":state}
        return client_config

    def callMethod(self, req):
        switch = self.factory.getSwitch(req['switch'])
        method = getattr(switch, req['method'])
        if hasattr(method, "is_public") and method.is_public:
            if "data" in req:
                return method(req["data"])
            else:
                return method()
        else:
            raise NotAllowedException('Method "{0}" of switch "{1}" is not public'.format(req['method'], req['switch']))

    def getState(self, switch_name):
        switch = self.factory.getSwitch(switch_name)
        state = switch.getState()
        metadata = switch.getMetaData()
        res = {"result":"state", "switch":switch_name, "state":state, "metadata":metadata}
        return res
    @asyncio.coroutine
    def onMessage(self, payload, isBinary):
        """ Handle messages """
        if not isBinary:
            res = None
            try:
                req = json.loads(payload.decode('utf8'))
                if isinstance(req, dict):
                    if req["action"] == "call_method":
                        try:
                            state = self.callMethod(req)
                            new_state = self.getState(req["switch"])
                            res = copy.copy(new_state)
                            res["return_value"] = state
                            res["methods"] = req["method"]
                            res["result"] = "return_method"

                            self.factory.broadcast(new_state)
                        except (NotAllowedException, NotFoundException) as e:
                            error = str(e)
                            res = {"result":"error", "error":error}

                    elif req["action"] == "get_config":
                        client_config = self.getClientConfig()
                        res = {"result":"config", "config":client_config}

                    elif req["action"] == "get_state":
                        res = self.getState(req["switch"])

                    else:
                        res = {"result":"error", "error":"Action not found"}
                else:
                    res = {"result":"error", "error":"Decoded payload is no dict"}

            except json.decoder.JSONDecodeError as e:
                res = {"result":"error", "error":"Couldn't decode payload"}
            except Exception as e:
                res = {"result":"error", "error":repr(e)}
            if res:
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
