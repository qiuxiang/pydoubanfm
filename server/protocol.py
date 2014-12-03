import json
from twisted.internet import protocol
from .handler import Handler


class Protocol(protocol.Protocol):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.factory.clients.append(self)

    def connectionLost(self, reason=protocol.connectionDone):
        self.factory.clients.remove(self)

    def dataReceived(self, data):
        Handler(self, data)

    def send(self, *data):
        self.transport.write(json.dumps(data))
