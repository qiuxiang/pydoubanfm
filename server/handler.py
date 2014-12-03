# coding=utf-8
import json
from doubanfm import LoginError
from utils import setting


class Handler:
    def __init__(self, _protocol, data):
        self.protocol = _protocol
        self.doubanfm = _protocol.factory.doubanfm
        try:
            self.data = json.loads(data)
            getattr(self, 'action_' + self.data[0])()
        except Exception as e:
            print('请求出错：' + e.message)

    def action_channels(self):
        self.protocol.send('channels', self.doubanfm.channels)

    def action_song(self):
        self.protocol.send('song', self.doubanfm.song)

    def action_skip(self):
        self.doubanfm.skip()

    def action_rate(self):
        self.doubanfm.rate()

    def action_pause(self):
        self.doubanfm.pause()

    def action_resume(self):
        self.doubanfm.resume()

    def action_set_kbps(self):
        self.doubanfm.set_kbps(self.data[1])

    def action_get_kbps(self):
        self.protocol.send('kbps', setting.get('kbps'))

    def action_set_channel(self):
        self.doubanfm.select_channel(self.data[1])

    def action_get_channel(self):
        self.protocol.send('channel', setting.get('channel'))

    def action_playlist(self):
        self.protocol.send('playlist', self.doubanfm.playlist)

    def action_playlist_count(self):
        self.protocol.send('playlist_count', self.doubanfm.playlist_count)

    def action_login(self):
        result = self.doubanfm.login(
            self.data[1]['email'], self.data[1]['password'])
        if type(result) is LoginError:
            self.protocol.send('login_failed', result.message)
