# coding: utf-8
import json
import threading
from twisted.internet.protocol import Protocol as TwistedProtocol
from ..utils import stars, second2time, music_symbol


class Protocol(TwistedProtocol):
    def __init__(self):
        self.input_thread = threading.Thread(target=self.input)
        self.input_thread.setDaemon(True)

    def connectionMade(self):
        print('connected')
        if not self.input_thread.isAlive():
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
                    print('message error: %s' % e.message)

    def on_error(self, message):
        print('server error: %s' % message)

    def on_user_info(self, user_info):
        if user_info:
            print('user\n  %s <%s>' % (user_info['user_name'], user_info['email']))
        else:
            print('☻')

    def on_song(self, song):
        print('%s\n  %s - %s（%s）%s\n  %s（%s）\n  %s, %s\n  %s' % (
            music_symbol(),
            song['artist'],
            song['title'],
            second2time(song['length']),
            ['♡', '♥'][song['like']],
            song['albumtitle'],
            'http://music.douban.com' + song['album'],
            song['company'],
            song['public_time'],
            stars(song['rating_avg']),
        ))

    def on_play(self, song):
        self.on_song(song)

    def on_skip(self):
        print('skip')

    def on_like(self):
        print('♥')

    def on_unlike(self):
        print('♡')

    def on_remove(self):
        print('remove')

    def on_pause(self):
        print('pause')

    def on_resume(self):
        print('resume')

    def on_login_success(self, user_info):
        print('login success')
        self.on_user_info(user_info)

    def on_login_failed(self, message):
        print('login failed: %s' % message)

    def on_kbps(self, kbps):
        print('%s kbps' % kbps)

    def on_channel(self, channel_id):
        print('%s Hz' % channel_id)

    def on_channels(self, channels):
        print('channels: ')
        for channel in channels:
            print('  %s（%s）' % (channel['name'], channel['channel_id']))

    def on_playlist(self, playlist):
        print('playlist: ')
        for song in playlist:
            print('  %s - %s <%s>' % (song['artist'], song['title'], song['albumtitle']))

    def on_state(self, state):
        print(state)

    def on_logout(self):
        print('logout')

    def on_volume(self, volume):
        print('%s%% volume' % (float(volume) * 100))
