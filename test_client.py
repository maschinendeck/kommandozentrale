import autobahn

from autobahn.asyncio.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

import sys
from tests import *
class TestClientProtocol(WebSocketClientProtocol):

    tests = [Config(), ExistingSwitch(), NotExistingSwitch(), PublicMethod(), PrivateMethod(), GetState()]

    def onOpen(self):
        print("Connected, running tests")
        self.sendTest()


    def onMessage(self, msg, isBinary):
        if not isBinary:
            for index,test in enumerate(self.tests):
                #print(test)
                if test.validateResponse(msg):
                    print("Test passed: {}".format(test.__class__.__name__))
                    self.tests.pop(index)
                    if len(self.tests) == 0:
                        print("Run tests")
                        sys.exit(0)
                    else:
                        self.sendTest()


    def sendTest(self):
        test = self.tests[-1]
        self.sendMessage(test.getPayload())

    def onClose(self, wasClean, code, reason):
        print("Connection to {url} closed: {error_message}".format(url=self.factory.url, error_message=reason))


if __name__ == '__main__':

    import asyncio

    factory = WebSocketClientFactory(u"ws://127.0.0.1:9000", useragent="Kommandozentrale TestClient 0.1")
    factory.protocol = TestClientProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, '127.0.0.1', 9000)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()
