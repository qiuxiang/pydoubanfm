# coding: utf-8
import json
import threading
from twisted.internet.protocol import Protocol as TwistedProtocol
from ..utils import stars, second2time, music_symbol, Color


class Protocol(TwistedProtocol):
    def __init__(self):
        print('Starting...')
        self.input_thread = threading.Thread(target=self.input)
        self.input_thread.setDaemon(True)

    def connectionMade(self):
        print(Color.green('Connected'))
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
                    print(Color.red('Message processing failed: %s' % e.message))

    def on_error(self, message):
        print(Color.red('Server error: %s' % message))

    def on_user(self, user):
        if user:
            print('%s <%s>' % (Color.cyan(user['user_name']), user['email']))
        else:
            print('☺')

    def on_song(self, song):
        self.song = song
        print('%s%s - %s（%s）%s\n  %s（%s）\n  %s, %s\n  %s' % (
            music_symbol() + ' ',
            Color.yellow(song['artist']),
            Color.green(song['title']),
            second2time(song['length']),
            Color.red(['♡', '♥'][song['like']]),
            Color.cyan(song['albumtitle']),
            'http://music.douban.com' + song['album'],
            song['company'],
            song['public_time'],
            Color.magenta(stars(song['rating_avg'])),
        ))

    def on_play(self, song):
        self.on_song(song)

    def on_skip(self):
        print(Color.yellow('Skip'))

    def on_like(self):
        print(Color.red('♥'))

    def on_unlike(self):
        print(Color.white('♡'))

    def on_remove(self):
        print(Color.red('Remove'))

    def on_pause(self):
        print(Color.blue('Pause'))

    def on_resume(self):
        print(Color.green('Resume'))

    def on_login_success(self, user):
        print(Color.green('Login success'))
        self.on_user(user)

    def on_login_failed(self, message):
        print(Color.red('Login failed: %s' % message))

    def on_kbps(self, kbps):
        print(Color.magenta('%sKBps' % kbps))

    def on_channel(self, channel_id):
        self.channel_id = int(channel_id)
        if hasattr(self, 'channels'):
            for channel in self.channels:
                if channel_id == int(channel['channel_id']):
                    print(Color.magenta(channel['name']))
                    return

    def on_channels(self, channels):
        self.channels = channels
        print('Channels:')
        for channel in channels:
            active = Color.cyan
            if hasattr(self, 'channel_id') and int(channel['channel_id']) == self.channel_id:
                active = Color.magenta
            print('  %s（%s）' % (active(channel['name']), channel['channel_id']))

    def on_playlist(self, playlist):
        print('Playlist:')
        for index, song in enumerate(playlist):
            current = ' '
            if hasattr(self, 'song') and self.song == song:
                current = '>'
            print('%s %s. %s - %s <%s>' % (
                Color.red(current),
                index + 1,
                Color.yellow(song['artist']),
                Color.green(song['title']),
                song['albumtitle']))

    def on_state(self, state):
        if state == 'playing':
            print(Color.green('Playing'))

        if state == 'paused':
            print(Color.yellow('Paused'))

        if state == 'null':
            print(Color.red('Stoped'))

        if state == 'ready':
            print(Color.cyan('Ready'))

    def on_logout(self):
        print(Color.yellow('Logout'))

    def on_volume(self, volume):
        print('Volume %s' % Color.magenta(str(float(volume) * 100) + '%'))
