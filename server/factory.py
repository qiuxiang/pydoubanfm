# coding=utf-8
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
            'no_longer_play': self.on_no_longer_play,
            'login_success':  self.on_login_success,
            })
        self.doubanfm.run()

    def on_play_new(self):
        self.broadcast('new', self.doubanfm.song)
        print('开始播放：' + json_dumps(self.doubanfm.song))

    def on_pause(self):
        self.broadcast('pause')
        print('暂停播放')

    def on_play(self):
        self.broadcast('play')
        print('恢复播放')

    def on_login_success(self):
        self.broadcast('login_success', self.doubanfm.user_info)
        print('登录成功：' + json_dumps(self.doubanfm.user_info))

    def on_kbps_change(self):
        self.broadcast('kbps', setting.get('kbps'))
        print('设置收听码率为：%skbps' % setting.get('kbps'))

    def on_channel_change(self):
        self.broadcast('channel', setting.get('channel'))
        print('设置收听频道为：' + setting.get('channel'))

    def on_skip(self):
        self.broadcast('skip')
        print('跳过')

    def on_no_longer_play(self):
        self.broadcast('no_longer_play')
        print('不再播放')

    def on_rate(self):
        if self.doubanfm.song['like'] == 0:
            self.broadcast('like')
            print('喜欢')
        else:
            self.broadcast('unlike')
            print('不喜欢')

    def broadcast(self, *data):
        for client in self.clients:
            client.send(data)

    def buildProtocol(self, addr):
        return Protocol(self)
