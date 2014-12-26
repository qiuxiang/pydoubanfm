# coding: utf-8
import json
import threading
from twisted.internet.protocol import Protocol as TwistedProtocol
from ..utils import stars, second2time, music_symbol, Color as color


class Protocol(TwistedProtocol):
    def __init__(self):
        print('Starting...')
        self.input_thread = threading.Thread(target=self.input)
        self.input_thread.setDaemon(True)

    def connectionMade(self):
        print(color.green('Connected'))
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
                    print(color.red('%sMessage processing failed: %s' % e.message))

    def on_error(self, message):
        print(color.red('Server error: %s' % message))

    def on_user(self, user):
        if user:
            print('%s <%s>' % (color.cyan(user['user_name']), user['email']))
        else:
            print('☺')

    def on_song(self, song):
        self.song = song
        print('%s%s - %s（%s）%s\n  %s（%s）\n  %s, %s\n  %s' % (
            music_symbol() + ' ',
            color.yellow(song['artist']),
            color.green(song['title']),
            second2time(song['length']),
            color.red(['♡', '♥'][song['like']]),
            color.cyan(song['albumtitle']),
            'http://music.douban.com' + song['album'],
            song['company'],
            song['public_time'],
            color.magenta(stars(song['rating_avg'])),
        ))

    def on_play(self, song):
        self.on_song(song)

    def on_skip(self):
        print(color.yellow('Skip'))

    def on_like(self):
        print(color.red('♥'))

    def on_unlike(self):
        print(color.white('♡'))

    def on_remove(self):
        print(color.red('Remove'))

    def on_pause(self):
        print(color.blue('Pause'))

    def on_resume(self):
        print(color.green('Resume'))

    def on_login_success(self, user):
        print(color.green('Login success'))
        self.on_user(user)

    def on_login_failed(self, message):
        print(color.red('Login failed: %s' % message))

    def on_kbps(self, kbps):
        print(color.magenta('%sKBps' % kbps))

    def on_channel(self, channel_id):
        self.channel_id = int(channel_id)
        if hasattr(self, 'channels'):
            for channel in self.channels:
                if channel_id == channel['channel_id']:
                    print(color.magenta(channel['name']))
                    return

    def on_channels(self, channels):
        self.channels = channels
        print(color.yellow('Channels:'))
        for channel in channels:
            active = color.cyan
            if hasattr(self, 'channel_id') and channel['channel_id'] == self.channel_id:
                active = color.magenta
            print('  %s（%s）' % (active(channel['name']), channel['channel_id']))

    def on_playlist(self, playlist):
        print(color.cyan('Playlist:'))
        for song in playlist:
            current = ' '
            if hasattr(self, 'song') and self.song == song:
                current = '>'
            print('%s %s - %s <%s>' % (
                current,
                color.yellow(song['artist']),
                color.green(song['title']),
                song['albumtitle']))

    def on_state(self, state):
        if state == 'playing':
            print(color.green('Playing'))

        if state == 'paused':
            print(color.yellow('Paused'))

        if state == 'null':
            print(color.red('Stoped'))

        if state == 'ready':
            print(color.cyan('Ready'))

    def on_logout(self):
        print(color.yellow('Logout'))

    def on_volume(self, volume):
        print('Volume %s' % color.magenta(str(float(volume) * 100) + '%'))
