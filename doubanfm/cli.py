#!/usr/bin/env python
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from doubanfm.client.base import Protocol as BaseProtocol
from doubanfm.utils import run_client


class Protocol(BaseProtocol):
    def __init__(self):
        BaseProtocol.__init__(self)

    def connectionMade(self):
        BaseProtocol.connectionMade(self)
        self.transport.write(
            'user\nstate\nvolume\nkbps\nchannel\nchannels\nsong')

run_client(Protocol())
