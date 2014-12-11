# coding: utf-8
import json
import threading
from twisted.internet.protocol import Protocol as TwistedProtocol
from ..utils import stars, second2time


class Protocol(TwistedProtocol):
    def __init__(self):
        self.input_thread = threading.Thread(target=self.input)
        self.input_thread.setDaemon(True)

    def connectionMade(self):
        print('连接成功')
        if hasattr(self, 'input_thread') and not self.input_thread.isAlive():
            self.input_thread.start()

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
                    print('消息处理出错：' + e.message)

    def on_error(self, message):
        print('服务端错误: %s' % message)

    def on_user_info(self, user_info):
        if user_info:
            print('用户：%s <%s>' % (user_info['user_name'], user_info['email']))
        else:
            print('用户：None')

    def on_song(self, song):
        print('当前播放：\n  %s - %s（%s）\n  %s（%s）\n  %s发布于%ss\n  评分：%s\n  %s' % (
            song['artist'],
            song['title'],
            second2time(song['length']),
            song['albumtitle'],
            'http://music.douban.com' + song['album'],
            song['company'],
            song['public_time'],
            stars(song['rating_avg']),
            ['未收藏', '已收藏'][song['like']],
        ))

    def on_play(self, song):
        self.on_song(song)

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
        print('登录成功')
        self.on_user_info(user_info)

    def on_login_failed(self, message):
        print('登录失败：%s' % message)

    def on_kbps(self, kbps):
        print('当前码率：%skbps' % kbps)

    def on_channel(self, channel_id):
        print('当前频道：%s' % channel_id)

    def on_channels(self, channels):
        print('频道列表：')
        for channel in channels:
            print('  - %s（%s）' % (channel['name'], channel['channel_id']))

    def on_playlist(self, playlist):
        print('播放列表：')
        for song in playlist:
            print('  %s - %s <%s>' % (song['artist'], song['title'], song['albumtitle']))

    def on_state(self, state):
        print(state)
