#!/usr/bin/env python
from twisted.internet.protocol import ClientFactory
from twisted.internet import reactor

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from doubanfm.client.base import Protocol as BaseProtocol
from doubanfm.utils import setting, reload_sys


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
