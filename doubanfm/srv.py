#!/usr/bin/env python
from twisted.internet import gireactor
gireactor.install()

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from doubanfm.server import Factory
from doubanfm.utils import Setting, port_is_open, reload_sys


reload_sys()
port = Setting.get('port')
if not port_is_open(port):
    TCP4ServerEndpoint(reactor, port).listen(Factory())
    reactor.run()
