#!/usr/bin/env python
from twisted.internet import gtk3reactor
gtk3reactor.install()
from twisted.internet import reactor

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from doubanfm.client.base import Factory
from doubanfm.client.gtk import Protocol
from doubanfm.utils import setting, reload_sys

reload_sys()
reactor.connectTCP('127.0.0.1', setting.get('port'), Factory(Protocol()))
reactor.run()
