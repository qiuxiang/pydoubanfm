# coding: utf-8
import os
import json
import cookielib

from gi.repository import Notify
Notify.init(__name__)

from .proxy import Proxy, LoginError
from .. import Hooks, GstPlayer
from ...utils import setting, download, json_dump, notify, Path as path, stars


class Player:
    def __init__(self):
        self.hooks = Hooks()
        self.song = {'sid': -1}
        self.playlist_count = 0
        self.player = GstPlayer()
        self.player.hooks.register('eos', self.on_player_eos)

        self.proxy = Proxy()
        self.proxy.set_kbps(setting.get('kbps'))
        self.proxy.session.cookies = \
            cookielib.LWPCookieJar(path.cookies)

        try:
            self.proxy.session.cookies.load()
            self.user = json.load(open(path.user))
            self.proxy.set_auth(self.user)
        except IOError:
            pass

        if os.path.isfile(path.channels):
            self.channels = json.load(open(path.channels))
        else:
            self.update_channels()

    def update_channels(self):
        self.channels = self.proxy.get_channels()
        self.channels.insert(0, {'name': '红心兆赫', 'channel_id': -3})
        json_dump(self.channels, path.channels)

    def update_playlist(self, operation_type):
        self.playlist = self.proxy.get_playlist(
            setting.get('channel'), operation_type, self.song['sid'])['song']
        self.proxy.session.cookies.save()

    def set_kbps(self, kbps):
        self.proxy.set_kbps(kbps)
        setting.set('kbps', kbps)
        self.hooks.dispatch('kbps_change')

    def login(self, email, password):
        """:return: 登录成功返回用户信息，失败则返回异常"""
        try:
            self.user = self.proxy.login(email, password)
            self.proxy.session.cookies.save()
            self.hooks.dispatch('login_success')
            json_dump(self.user, path.user)
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
        os.remove(path.user)
        if setting.get('channel') == -3:
            self.select_channel(0)

    def play(self):
        self.song = self.playlist[self.playlist_count]
        self.save_album_cover()
        self.player.set_uri(self.song['url'])
        self.player.play()
        self.song_notify()
        self.hooks.dispatch('play')

    def song_notify(self):
        notify('%s %s' % (self.song['title'], ['♡', '♥'][self.song['like']]),
               '%s <%s>\n%s' % (
                   self.song['artist'],
                   self.song['albumtitle'],
                   stars(self.song['rating_avg'])),
               self.song['picture_file'])

    def next(self, operation_type='n'):
        """播放下一曲"""
        self.update_playlist(operation_type)
        self.playlist_count = 0
        self.player.stop()
        self.play()

    def select_channel(self, channel_id):
        setting.set('channel', channel_id)
        self.hooks.dispatch('channel_change')
        self.next('n')

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

    def on_player_eos(self):
        """当前歌曲播放完毕后的处理"""
        if len(self.playlist) == self.playlist_count + 1:
            self.update_playlist('p')
            self.playlist_count = 0
        else:
            self.playlist_count += 1

        self.proxy.get_playlist(
            setting.get('channel'), 'e', self.song['sid'])
        self.play()

    def run(self):
        self.update_playlist('n')
        self.play()

    def remove(self):
        """不再播放当前的歌曲"""
        self.hooks.dispatch('remove')
        self.next('b')

    def skip(self):
        """跳过当前的歌曲"""
        self.hooks.dispatch('skip')
        self.next('s')

    def set_volume(self, value):
        self.player.set_volume(value)
        self.hooks.dispatch('volume_change')

    def save_album_cover(self):
        self.song['picture_file'] = \
            path.album_cover + self.song['picture'].split('/')[-1]
        if not os.path.isfile(self.song['picture_file']):
            download(self.song['picture'], self.song['picture_file'])
