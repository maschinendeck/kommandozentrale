from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

import asyncio
import json
import importlib
class KommandozentraleServerProtocol(WebSocketServerProtocol):
    config = {"switchModule":"switch_classes","switches": {}}
    def __init__(self, config="config.json"):
        super().__init__()
        with open(config) as configfile:
            self.config.update(json.load(configfile))
        self.config['switchModule'] = importlib.import_module(self.config['switchModule'])

    @asyncio.coroutine
    def onMessage(self, payload, isBinary):
        if not isBinary:
            req = json.loads(payload.decode('utf8'))
            if req["action"] == "call_method":
                switch_class = self.config['switches'][req['switch']]['class']
                if "initial_data" in self.config['switches'][req['switch']]:
                    switch = getattr(self.config["switchModule"], switch_class)(self.config['switches'][req['switch']]['initial_data'], name=req['switch'])
                else:
                    switch = getattr(self.config["switchModule"], switch_class)(name=req['switch'])
                method = getattr(switch, req['method'])
                if "data" in req:
                    method(req["data"])
                else:
                    method()
                res = {"result":"state", "switch":req["switch"], "state":switch.getState()}
                self.sendMessage(json.dumps(res).encode("utf8"))
                print("New State of",req["switch"],"is ",switch.getState())
            elif req["action"] == "get_config":
                # TODO: send better config (client doesn't need class names etc)
                msg = {"result":"config", "config":self.config}
                self.sendMessage(json.dumps(msg).encode("utf8"))
            else:
                msg = {"result":"error", "error":"Action not found"}
                self.sendMessage(json.dumps(msg).encode("utf8"))


if __name__ == '__main__':

    factory = WebSocketServerFactory(u"ws://localhost:9000")
    factory.protocol = KommandozentraleServerProtocol

    loop = asyncio.get_event_loop()
    server = loop.create_server(factory, 'localhost', 9000)
    ruc = loop.run_until_complete(server)
    print("Started")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        ruc.close()
        loop.close()
