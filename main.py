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
        self.widgets = {}
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.__dir__ + '/doubanfm.glade')
        self.builder.connect_signals(self)
        self.builder.get_object('window-player').show_all()

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
        self.indicator.set_menu(self.get_widget('indicator-menu'))

    def get_widget(self, name):
        if name not in self.widgets:
            self.widgets[name] = self.builder.get_object(name)
        return self.widgets[name]

    def update_notify(self):
        self.notify.update(
            self.song['title'], self.song['artist'], self.album_cover_path)
        self.notify.show()

    def update_title(self):
        self.get_widget('menuitem-title').set_label(
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
            self.get_widget('button-playback').set_image(self.get_widget('image-play'))
            self.get_widget('button-playback').set_tooltip_text('播放')
            self.get_widget('menuitem-playback').set_label('播放')
        else:
            self.player.play()
            self.get_widget('button-playback').set_image(self.get_widget('image-pause'))
            self.get_widget('button-playback').set_tooltip_text('暂停')
            self.get_widget('menuitem-playback').set_label('暂停')

    def on_rate(self, widget):
        if (type(widget) == Gtk.ToggleButton and self.get_widget('button-rate').get_active()) or \
           (type(widget) == Gtk.MenuItem and not self.get_widget('button-rate').get_active()):
            self.get_widget('button-rate').set_tooltip_text('取消喜欢')
            self.get_widget('menuitem-rate').set_label('取消喜欢')
            if self.song['like'] == 0:
                self.update_playlist('r')
                self.song['like'] = True
                self.play_count = 0
                self.get_widget('button-rate').set_active(True)
        else:
            self.get_widget('button-rate').set_tooltip_text('喜欢')
            self.get_widget('menuitem-rate').set_label('喜欢')
            if self.song['like'] == 1:
                self.update_playlist('u')
                self.song['like'] = False
                self.play_count = 0
                self.get_widget('button-rate').set_active(False)

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
        self.get_widget('image-album-cover').set_from_pixbuf(
            GdkPixbuf.Pixbuf.new_from_file_at_scale(
                self.album_cover_path, 240, -1, True))
        self.get_widget('image-album-cover').set_tooltip_text(
            '标题：%s\n艺术家：%s\n专辑：%s' % (
                self.song['title'],
                self.song['artist'],
                self.song['albumtitle']))

    def set_rate_state(self):
        if self.song['like']:
            self.get_widget('button-rate').set_active(True)
        else:
            self.get_widget('button-rate').set_active(False)

if __name__ == '__main__':
    import sys
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')

    DoubanfmPlayer().run()
