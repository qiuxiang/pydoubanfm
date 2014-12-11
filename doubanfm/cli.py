from twisted.internet.protocol import ClientFactory
from twisted.internet import reactor
from .client.base import Protocol as BaseProtocol
from .utils import setting, reload_sys


class Protocol(BaseProtocol):
    def connectionMade(self):
        BaseProtocol.connectionMade(self)
        self.transport.write('user_info\nsong')


class Factory(ClientFactory):
    def buildProtocol(self, addr):
        return Protocol()

reload_sys()
reactor.connectTCP('127.0.0.1', setting.get('port'), Factory())
reactor.run()
