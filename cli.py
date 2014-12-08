#!/usr/bin/env python
# coding: utf-8
import threading
from twisted.internet.protocol import ClientFactory
from twisted.internet import reactor
from client import Protocol
from utils import setting, reload_sys


class DoubanFmClientProtocol(Protocol):
    def connectionMade(self):
        threading.Thread(target=self.input).start()
        self.transport.write('user_info\nsong')

    def input(self):
        while True:
            self.transport.write(raw_input())


class DoubanFmFactory(ClientFactory):
    def buildProtocol(self, addr):
        return DoubanFmClientProtocol()

if __name__ == '__main__':
    reload_sys()
    reactor.connectTCP('127.0.0.1', setting.get('port'), DoubanFmFactory())
    reactor.run()
