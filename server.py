#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from twisted.internet import gireactor
gireactor.install()

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from server import Factory
from utils import setting, port_is_open

port = setting.get('port')
if not port_is_open(port):
    TCP4ServerEndpoint(reactor, port).listen(Factory())
    reactor.run()
