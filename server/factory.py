from twisted.internet import protocol
from doubanfm import Player
from utils import json_dumps, setting
from .protocol import Protocol


class Factory(protocol.Factory):
    def __init__(self):
        self.clients = []
        self.doubanfm = Player()
        self.doubanfm.hooks.register({
            'play_new':       self.on_play_new,
            'pause':          self.on_pause,
            'play':           self.on_play,
            'kbps_change':    self.on_kbps_change,
            'channel_change': self.on_channel_change,
            'skip':           self.on_skip,
            'remove':         self.on_remove,
            'login_success':  self.on_login_success,
        })
        self.doubanfm.run()

    def on_play_new(self):
        self.broadcast('new', self.doubanfm.song)
        print('play: ' + json_dumps(self.doubanfm.song))

    def on_pause(self):
        self.broadcast('pause')
        print('pause')

    def on_play(self):
        self.broadcast('play')
        print('resume')

    def on_login_success(self):
        self.broadcast('login_success', self.doubanfm.user_info)
        print('login success: ' + json_dumps(self.doubanfm.user_info))

    def on_kbps_change(self):
        self.broadcast('kbps', setting.get('kbps'))
        print('kbps: %skbps' % setting.get('kbps'))

    def on_channel_change(self):
        self.broadcast('channel', setting.get('channel'))
        print('channel: ' + setting.get('channel'))

    def on_skip(self):
        self.broadcast('skip')
        print('skip')

    def on_remove(self):
        self.broadcast('remove')
        print('remove')

    def on_rate(self):
        if self.doubanfm.song['like'] == 0:
            self.broadcast('like')
            print('like')
        else:
            self.broadcast('unlike')
            print('unlike')

    def broadcast(self, *data):
        for client in self.clients:
            client.send(data)

    def buildProtocol(self, addr):
        return Protocol(self)
