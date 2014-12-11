from twisted.internet import protocol
from .protocol import Protocol
from ..lib.core import Player
from ..utils import json_dumps, setting


class Factory(protocol.Factory):
    def __init__(self):
        self.clients = []
        self.doubanfm = Player()
        self.doubanfm.hooks.register({
            'play':           self.on_play,
            'pause':          self.on_pause,
            'resume':         self.on_resume,
            'kbps_change':    self.on_kbps_change,
            'channel_change': self.on_channel_change,
            'skip':           self.on_skip,
            'remove':         self.on_remove,
            'like':           self.on_like,
            'unlike':         self.on_unlike,
            'login_success':  self.on_login_success,
        })
        self.doubanfm.run()

    def on_play(self):
        self.broadcast('play', self.doubanfm.song)
        print('play: ' + json_dumps(self.doubanfm.song))

    def on_pause(self):
        self.broadcast('pause')
        print('pause')

    def on_resume(self):
        self.broadcast('resume')
        print('resume')

    def on_login_success(self):
        self.broadcast('login_success', self.doubanfm.user_info)
        print('login success: ' + json_dumps(self.doubanfm.user_info))

    def on_kbps_change(self):
        self.broadcast('kbps', setting.get('kbps'))
        print('kbps: %skbps' % setting.get('kbps'))

    def on_channel_change(self):
        self.broadcast('channel', setting.get('channel'))
        print('channel: %s' % setting.get('channel'))

    def on_skip(self):
        self.broadcast('skip')
        print('skip')

    def on_remove(self):
        self.broadcast('remove')
        print('remove')

    def on_like(self):
        self.broadcast('like')
        print('like')

    def on_unlike(self):
        self.broadcast('unlike')
        print('unlike')

    def broadcast(self, *data):
        for client in self.clients:
            client.send(*data)

    def buildProtocol(self, addr):
        return Protocol(self)
