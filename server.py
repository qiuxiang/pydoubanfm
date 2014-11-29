# encoding: utf-8
import json
from twisted.internet import reactor, protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from doubanfm_player import DoubanfmPlayer


class Handler:
    def __init__(self, protocol_, data):
        self.protocol = protocol_
        self.data = json.loads(data)
        print(self.data)

class Protocol(protocol.Protocol):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.factory.clients.append(self)

    def connectionLost(self, reason=protocol.connectionDone):
        self.factory.clients.remove(self)

    def dataReceived(self, data):
        Handler(self, data)

    def broadcast(self, data):
        for client in self.factory.clients:
            client.transport.write(data)


class Factory(protocol.Factory):
    def __init__(self):
        self.clients = []
        self.doubanfm_player = DoubanfmPlayer()
        self.doubanfm_player.run()

    def buildProtocol(self, addr):
        return Protocol(self)

if __name__ == '__main__':
    TCP4ServerEndpoint(reactor, 1234).listen(Factory())
    reactor.run()