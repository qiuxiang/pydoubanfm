# coding: utf-8
import os
import json
import cookielib

from gi.repository import Notify
Notify.init(__name__)

from lib import Hooks, GstPlayer
from utils import setting, download, json_dump
from .proxy import Proxy, LoginError


class Player:
    def __init__(self):
        self.hooks = Hooks()
        self.notify = Notify.Notification.new('', '', '')
        self.song = {'sid': -1}
        self.playlist_count = 0
        self.player = GstPlayer()
        self.player.hooks.register('eos', self.on_player_eos)

        self.proxy = Proxy()
        self.proxy.set_kbps(setting.get('kbps'))
        self.proxy.session.cookies = \
            cookielib.LWPCookieJar(setting.cookies_file)

        try:
            self.proxy.session.cookies.load()
            self.user_info = json.load(open(setting.user_file))
            self.proxy.set_auth(self.user_info)
        except:
            pass

        if os.path.isfile(setting.channels_file):
            self.channels = json.load(open(setting.channels_file))
        else:
            self.update_channels()

    def show_notify(self, title='', content='', picture=''):
        if not title:
            title = self.song['title']
            content = self.song['artist']
            picture = self.song['picture_file']

        self.notify.update(title, content, picture)
        self.notify.show()

    def update_channels(self):
        self.channels = self.proxy.get_channels()
        self.channels.insert(0, {'name': '红心兆赫', 'channel_id': -3})
        json_dump(self.channels, setting.channels_file)

    def update_playlist(self, operation_type):
        self.playlist = self.proxy.get_playlist(
            setting.get('channel'), operation_type, self.song['sid'])['song']
        self.proxy.session.cookies.save()

    def set_kbps(self, kbps):
        self.proxy.set_kbps(kbps)
        setting.put('kbps', kbps)
        self.hooks.dispatch('kbps_change')

    def login(self, email, password):
        """:return: 登录成功返回用户信息，失败则返回异常"""
        try:
            self.user_info = self.proxy.login(email, password)
            self.proxy.session.cookies.save()
            self.hooks.dispatch('login_success')
            json_dump(self.user_info, setting.user_file)
            return self.user_info
        except LoginError as e:
            return e

    def play(self):
        self.song = self.playlist[self.playlist_count]
        self.save_album_cover()
        self.player.set_uri(self.song['url'])
        self.player.play()
        self.show_notify()
        self.hooks.dispatch('play')

    def next(self, operation_type='n'):
        """播放下一曲"""
        self.update_playlist(operation_type)
        self.playlist_count = 0
        self.player.stop()
        self.play()

    def select_channel(self, channel_id):
        setting.put('channel', channel_id)
        self.next('n')
        self.hooks.dispatch('channel_change')

    def pause(self):
        self.player.pause()
        self.hooks.dispatch('pause')

    def resume(self):
        self.player.play()
        self.hooks.dispatch('play')

    def like(self):
        self.update_playlist('r')
        self.song['like'] = True
        self.playlist_count = 0
        self.hooks.dispatch('like')

    def unlike(self):
        self.update_playlist('u')
        self.song['like'] = False
        self.playlist_count = 0
        self.hooks.dispatch('unlike')

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
        self.next('b')
        self.hooks.dispatch('remove')

    def skip(self):
        """跳过当前的歌曲"""
        self.next('s')
        self.hooks.dispatch('skip')

    def set_volume(self, value):
        self.player.set_volume(value)
        self.hooks.dispatch('volume_change')

    def save_album_cover(self):
        self.song['picture_file'] = \
            setting.album_cover_dir + self.song['picture'].split('/')[-1]
        if not os.path.isfile(self.song['picture_file']):
            download(self.song['picture'], self.song['picture_file'])

if __name__ == '__main__':
    from gi.repository import Gtk
    doubanfm_player = GstPlayer()
    doubanfm_player.run()
    Gtk.main()
