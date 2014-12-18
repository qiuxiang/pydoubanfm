#!/usr/bin/env python
from twisted.internet import gtk3reactor
gtk3reactor.install()

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from doubanfm.client.gtk import Protocol
from doubanfm.utils import run_client
run_client(Protocol())
