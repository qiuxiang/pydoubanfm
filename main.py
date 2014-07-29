#!/usr/bin/env python
# encoding: utf8

import os
import json
import requests
from gi.repository import Gtk, Notify, GdkPixbuf, AppIndicator3
from doubanfm import Doubanfm
from player import *


class DoubanfmPlayer:
    def __init__(self):
        self.init_path()
        self.init_builder()
        self.init_widget()
        self.init_doubanfm()
        self.init_player()
        self.init_notify()
        self.init_indicator()

    def init_path(self):
        self.__dir__ = os.path.abspath(os.path.dirname(__file__))
        self.data_dir = os.path.expanduser('~/.pydoubanfm/')
        self.album_cover_dir = self.data_dir + 'albumcover/'
        self.config_path = self.data_dir + 'config.json'

        if not os.path.isdir(self.data_dir):
            os.mkdir(self.data_dir)

        if not os.path.isdir(self.album_cover_dir):
            os.mkdir(self.album_cover_dir)

        if os.path.isfile(self.config_path):
            self.config = json.load(open(self.config_path))
        else:
            self.config = {
                'channel': 0,
                'email': '',
                'password': ''}

    def init_builder(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.__dir__ + '/doubanfm.glade')
        self.builder.connect_signals(self)
        self.builder.get_object('window-player').show_all()

    def init_widget(self):
        self.button_playback = self.builder.get_object('button-playback')
        self.button_rate = self.builder.get_object('button-rate')
        self.image_play = self.builder.get_object('image-play')
        self.image_pause = self.builder.get_object('image-pause')
        self.image_album_cover = self.builder.get_object('image-album-cover')
        self.indicator_menu = self.builder.get_object('indicator-menu')
        self.menuitem_playback = self.builder.get_object('menuitem-playback')
        self.menuitem_rate = self.builder.get_object('menuitem-rate')
        self.menuitem_title = self.builder.get_object('menuitem-title')

    def init_doubanfm(self):
        self.doubanfm = Doubanfm()
        self.play_count = 0
        self.song = {'sid': None}
        self.channel = self.config['channel']
        if self.config['email'] and self.config['password']:
            self.login(self.config['email'], self.config['password'])

    def init_player(self):
        self.player = Player()
        self.player.on_eos = self.on_eos

    def init_notify(self):
        Notify.init('pydoubanfm')
        self.notify = Notify.Notification.new('', '', '')

    def init_indicator(self):
        self.indicator = AppIndicator3.Indicator.new(
            'pydoubanfm', 'applications-multimedia',
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_icon(self.__dir__ + '/icon.png')
        self.indicator.set_menu(self.indicator_menu)

    def update_notify(self):
        self.notify.update(
            self.song['title'], self.song['artist'], self.album_cover_path)
        self.notify.show()

    def update_title(self):
        self.menuitem_title.set_label(
            self.song['title'] + ' - ' + self.song['artist'])

    def login(self, email, password):
        try:
            self.doubanfm.login(email, password)
        except Exception as error:
            dialog = Gtk.MessageDialog(
                None, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, '登录失败')
            dialog.format_secondary_text(error)
            dialog.run()
            dialog.destroy()

    def run(self):
        self.update_playlist('n')
        self.play()
        Gtk.main()

    def on_eos(self):
        if len(self.playlist) == self.play_count + 1:
            self.update_playlist('p')
            self.play_count = 0
        else:
            self.play_count += 1

        self.end_report()
        self.play()

    def play(self):
        self.song = self.playlist[self.play_count]
        self.player.set_uri(self.song['url'])
        self.player.play()
        self.set_album_cover()
        self.set_rate_state()
        self.update_notify()
        self.update_title()

    def end_report(self):
        self.doubanfm.get_playlist(self.channel, 'e', self.song['sid'])

    def update_playlist(self, type):
        self.playlist = self.doubanfm.get_playlist(
            self.channel, type, self.song['sid'])['song']

    def on_exit(self, *args):
        Gtk.main_quit(*args)
        self.config['channel'] = self.channel
        json.dump(self.config, open(self.config_path, 'w'), indent=2)

    def on_playback(self, widget):
        if self.player.get_state() == STATE_PLAYING:
            self.player.pause()
            self.button_playback.set_image(self.image_play)
            self.button_playback.set_tooltip_text('播放')
            self.menuitem_playback.set_label('播放')
        else:
            self.player.play()
            self.button_playback.set_image(self.image_pause)
            self.button_playback.set_tooltip_text('暂停')
            self.menuitem_playback.set_label('暂停')

    def on_rate(self, widget):
        if (type(widget) == Gtk.ToggleButton and self.button_rate.get_active()) or \
           (type(widget) == Gtk.MenuItem and not self.button_rate.get_active()):
            self.button_rate.set_tooltip_text('取消喜欢')
            self.menuitem_rate.set_label('取消喜欢')
            if self.song['like'] == 0:
                self.update_playlist('r')
                self.song['like'] = True
                self.play_count = 0
                self.button_rate.set_active(True)
        else:
            self.button_rate.set_tooltip_text('喜欢')
            self.menuitem_rate.set_label('喜欢')
            if self.song['like'] == 1:
                self.update_playlist('u')
                self.song['like'] = False
                self.play_count = 0
                self.button_rate.set_active(False)

    def on_delete(self, widget):
        self.next('b')

    def on_skip(self, widget):
        self.next('s')

    def on_volume_changed(self, widget, value):
        self.player.set_volume(value)

    def next(self, type):
        self.update_playlist(type)
        self.play_count = 0
        self.player.stop()
        self.play()

    def on_open_album(self, widget, event=None):
        # 限定只有在图片范围内点击才会触发
        if event:
            size = widget.size_request()
            if event.x < 0 or event.x > size.width or event.y < 0 or event.y > size.height:
                return
        os.system('sensible-browser http://music.douban.com' + self.song['album'])

    def set_album_cover(self):
        self.album_cover_path = \
            self.album_cover_dir + self.song['picture'].split('/')[-1]
        open(self.album_cover_path, 'wb') \
            .write(requests.get(self.song['picture']).content)
        self.image_album_cover.set_from_pixbuf(
            GdkPixbuf.Pixbuf.new_from_file_at_scale(
                self.album_cover_path, 240, -1, True))
        self.image_album_cover.set_tooltip_text(
            '标题：%s\n艺术家：%s\n专辑：%s' % (
                self.song['title'],
                self.song['artist'],
                self.song['albumtitle']))

    def set_rate_state(self):
        if self.song['like']:
            self.button_rate.set_active(True)
        else:
            self.button_rate.set_active(False)

if __name__ == '__main__':
    import sys
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')

    DoubanfmPlayer().run()
