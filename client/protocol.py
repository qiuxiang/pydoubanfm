# coding: utf-8
import json
import threading
from twisted.internet.protocol import Protocol as TwistedProtocol
from utils import json_dumps


class Protocol(TwistedProtocol):
    def connectionMade(self):
        threading.Thread(target=self.input).start()

    def input(self):
        while True:
            self.transport.write(raw_input())

    def dataReceived(self, data):
        for row in data.split('\n'):
            if row:
                try:
                    data = json.loads(row)
                    if len(data) == 1:
                        getattr(self, 'on_' + data[0])()
                    else:
                        getattr(self, 'on_' + data[0])(data[1])
                except Exception as e:
                    print('error: ' + e.message)

    def on_error(self, message):
        print('error: ' + message)

    def on_user_info(self, user_info):
        print('当前用户：' + json_dumps(user_info))

    def on_song(self, song):
        print('当前播放：' + json_dumps(song))

    def on_play(self, song):
        print('当前播放：' + json_dumps(song))

    def on_skip(self):
        print('跳过')

    def on_like(self):
        print('喜欢')

    def on_unlike(self):
        print('不再喜欢')

    def on_remove(self):
        print('不再播放')

    def on_pause(self):
        print('暂停播放')

    def on_resume(self):
        print('恢复播放')

    def on_login_success(self, user_info):
        print('登录成功：' + json_dumps(user_info))

    def on_kbps(self, kbps):
        print('当前码率：' + kbps + 'kbps')

    def on_channel(self, channel_id):
        print('当前频道：' + channel_id)

    def on_channels(self, channels):
        print('频道列表：' + json_dumps(channels))

    def on_playlist(self, playlist):
        print('播放列表：' + json_dumps(playlist))

    def on_state(self, state):
        print('当前状态：' + state)
