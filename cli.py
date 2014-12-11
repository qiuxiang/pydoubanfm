#!/usr/bin/env python
from twisted.internet.protocol import ClientFactory
from twisted.internet import reactor
from client import Protocol as BaseProtocol
from utils import setting, reload_sys


class Protocol(BaseProtocol):
    def connectionMade(self):
        BaseProtocol.connectionMade(self)
        self.transport.write('user_info\nsong')


class Factory(ClientFactory):
    def __init__(self):
        self.protocol = Protocol()

    def buildProtocol(self, addr):
        return self.protocol

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection. Reason:', reason
        reactor.stop()

if __name__ == '__main__':
    reload_sys()
    reactor.connectTCP('127.0.0.1', setting.get('port'), Factory())
    reactor.run()
