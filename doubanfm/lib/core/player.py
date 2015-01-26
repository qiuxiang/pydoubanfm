# coding: utf-8
import os
import json
import cookielib

from gi.repository import Notify
Notify.init(__name__)

from .proxy import Proxy, LoginError
from .. import Hooks, GstPlayer
from ...utils import Setting, download, json_dump, notify, Path, stars


class Player:
    def __init__(self):
        self.hooks = Hooks()
        self.song = {'sid': -1}
        self.playlist_count = 0
        self.player = GstPlayer()
        self.player.hooks.register('eos', self.next)

        self.proxy = Proxy()
        self.proxy.set_kbps(Setting.get('kbps'))
        self.proxy.session.cookies = \
            cookielib.LWPCookieJar(Path.cookies)

        try:
            self.proxy.session.cookies.load()
            self.user = json.load(open(Path.user))
            self.proxy.set_auth(self.user)
        except IOError:
            pass

        if os.path.isfile(Path.channels):
            self.channels = json.load(open(Path.channels))
        else:
            self.update_channels()

    def update_channels(self):
        self.channels = self.proxy.get_channels()
        self.channels.insert(0, {'name': '红心兆赫', 'channel_id': -3})
        json_dump(self.channels, Path.channels)

    def update_playlist(self, operation_type):
        self.playlist = self.proxy.get_playlist(
            Setting.get('channel'), operation_type, self.song['sid'])['song']
        self.hooks.dispatch('playlist_change')
        self.proxy.session.cookies.save()

    def set_kbps(self, kbps):
        self.proxy.set_kbps(kbps)
        Setting.set('kbps', kbps)
        self.hooks.dispatch('kbps_change')

    def login(self, email, password):
        """:return: 登录成功返回用户信息，失败则返回异常"""
        try:
            self.user = self.proxy.login(email, password)
            self.proxy.session.cookies.save()
            self.hooks.dispatch('login_success')
            json_dump(self.user, Path.user)
            notify('登录成功',
                   self.user['user_name'] + ' <' +
                   self.user['email'] + '>')
            return self.user
        except LoginError as e:
            return e

    def logout(self):
        self.proxy.logout()
        self.user = None
        self.hooks.dispatch('logout')
        os.remove(Path.user)
        if Setting.get('channel') == -3:
            self.select_channel(0)

    def play(self, index=-1):
        if index == -1:
            index = self.playlist_count
        else:
            self.playlist_count = index

        if 0 <= index < len(self.playlist):
            self.song = self.playlist[index]
            self.song['index'] = index + 1
            self.save_album_cover(self.song)
            self.player.stop()
            self.player.set_uri(self.song['url'])
            self.player.play()
            self.song_notify()
            self.hooks.dispatch('play')

    def song_notify(self):
        notify('%s %s' % (self.song['title'], ['♡', '♥'][self.song['like']]),
               '%s《%s》\n%s' % (
                   self.song['artist'],
                   self.song['albumtitle'],
                   stars(self.song['rating_avg'])),
               self.song['picture_file'])

    def update(self, operation_type='n'):
        """播放下一曲，同时进行反馈"""
        self.update_playlist(operation_type)
        self.playlist_count = 0
        self.player.stop()
        self.play()

    def select_channel(self, channel_id):
        Setting.set('channel', channel_id)
        self.hooks.dispatch('channel_change')
        self.update('n')

    def pause(self):
        self.player.pause()
        self.hooks.dispatch('pause')

    def resume(self):
        self.player.play()
        self.hooks.dispatch('resume')

    def like(self):
        self.update_playlist('r')
        self.song['like'] = True
        self.playlist_count = 0
        self.hooks.dispatch('like')
        self.song_notify()

    def unlike(self):
        self.update_playlist('u')
        self.song['like'] = False
        self.playlist_count = 0
        self.hooks.dispatch('unlike')
        self.song_notify()

    def next(self, report=True):
        """当前歌曲播放完毕后的处理"""
        if len(self.playlist) == self.playlist_count + 1:
            self.update_playlist('p')
            self.playlist_count = 0
        else:
            self.playlist_count += 1

        if report:
            self.proxy.get_playlist(
                Setting.get('channel'), 'e', self.song['sid'])

        self.play()

    def run(self):
        self.update_playlist('n')
        self.play()

    def remove(self):
        """不再播放当前的歌曲"""
        self.hooks.dispatch('remove')
        self.update('b')

    def skip(self):
        """跳过当前的歌曲"""
        self.hooks.dispatch('skip')
        self.update('s')

    def set_volume(self, value):
        self.player.set_volume(value)
        self.hooks.dispatch('volume_change')

    @staticmethod
    def save_album_cover(song):
        song['picture_file'] = \
            Path.album_cover + song['picture'].split('/')[-1]
        if not os.path.isfile(song['picture_file']):
            download(song['picture'], song['picture_file'])
