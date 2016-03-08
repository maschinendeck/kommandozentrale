from autobahn.asyncio.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

import json
import random


class KommandozentraleClientProtocol(WebSocketClientProtocol):

    def onOpen(self):
        x = {"action":"call_method", "switch":"exampleSwitch","method":random.choice(["on", "off"])}
        self.sendMessage(json.dumps(x).encode('utf8'))
        if "data" in x:
            print('{switch}: {method}({data})'.format(**x))
        else:
            print('{switch}: {method}()'.format(**x))
        x = {"action":"get_config"}
        self.sendMessage(json.dumps(x).encode('utf8'))

    def onMessage(self, payload, isBinary):
        if not isBinary:
            res = json.loads(payload.decode('utf8'))
            if res["result"] == "state":
                print("State of {switch}: {state}".format(**res))
            elif res["result"] == "config":
                print(res)
                self.sendClose()

    def onClose(self, wasClean, code, reason):
        loop.stop()


if __name__ == '__main__':

    import asyncio

    factory = WebSocketClientFactory(u"ws://localhost:9000")
    factory.protocol = KommandozentraleClientProtocol

    loop = asyncio.get_event_loop()
    connection = loop.create_connection(factory, 'localhost', 9000)
    loop.run_until_complete(connection)
    loop.run_forever()
    loop.close()
