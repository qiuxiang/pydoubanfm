#!/usr/bin/env python
# encoding: utf8

import os
import json
import webbrowser
import requests
from gi.repository import Gtk, Notify, GdkPixbuf
from doubanfm import Doubanfm, LoginError
from player import *


class DoubanfmPlayer:
    def __init__(self):
        self.init_path()
        self.init_setting()
        self.init_builder()
        self.init_doubanfm()
        self.init_kbps()
        self.init_channels()
        self.init_player()
        self.init_notify()
        self.init_indicator()

    def init_path(self):
        """初始化路径，如果文件夹不存在则自动创建"""

        # 当前程序目录
        self.program_dir = os.path.abspath(os.path.dirname(__file__))
        # 图标路径
        self.icon_file = self.program_dir + '/icon.png'
        # 本地存储目录
        self.local_dir = os.path.expanduser('~/.pydoubanfm/')
        # 专辑封面目录
        self.album_cover_dir = self.local_dir + 'albumcover/'
        # “设置文件”路径
        self.setting_file = self.local_dir + 'setting.json'
        # 频道列表缓存文件路径
        self.channels_file = self.local_dir + 'channels.json'

        if not os.path.isdir(self.local_dir):
            os.mkdir(self.local_dir)

        if not os.path.isdir(self.album_cover_dir):
            os.mkdir(self.album_cover_dir)

    def init_setting(self):
        """从文件读取设置，如果文件不存在，使用默认配置，并创建"""
        if os.path.isfile(self.setting_file):
            self.setting = json.load(open(self.setting_file))
        else:
            self.setting = {
                'channel': 0,
                'email': '',
                'password': '',
                'kbps': 192}
            self.update_setting_file()

    def init_builder(self):
        self.widgets = {}
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.program_dir + '/doubanfm.glade')
        self.builder.connect_signals(self)
        self.builder.get_object('window-player').show_all()

    def init_doubanfm(self):
        self.doubanfm = Doubanfm()
        self.doubanfm.set_kbps(self.setting['kbps'])
        self.play_count = 0
        self.song = {'sid': None}
        if 'email' in self.setting and self.setting['email'] and \
           'password' in self.setting and self.setting['password']:
            self.login(self.setting['email'], self.setting['password'])

    def init_kbps(self):
        """创建码率设置菜单"""
        for kbps in ['64', '128', '192']:
            item = Gtk.CheckMenuItem(kbps + ' Kbps', visible=True)
            if str(self.setting['kbps']) == kbps:
                item.set_active(True)
                self.widget_kbps = item
            item.connect('activate', self.set_kbps, kbps)
            self.get_widget('menu-kbps').append(item)

    def init_channels(self):
        """创建频道选择菜单"""
        if os.path.isfile(self.channels_file):
            self.channels = json.load(open(self.channels_file))
        else:
            self.channels = self.doubanfm.get_channels()
            self.channels.insert(0, {'name': '红心兆赫', 'channel_id': -3})
            self.update_channels_file()

        for channel in self.channels:
            item = Gtk.CheckMenuItem(channel['name'], visible=True)
            if channel['channel_id'] == self.setting['channel']:
                item.set_active(True)
                self.widget_channel = item
            item.connect('activate', self.select_channel, channel['channel_id'])
            self.get_widget('menu-channels').append(item)

    def init_player(self):
        self.player = Player()
        self.player.on_eos = self.on_eos

    def init_notify(self):
        """初始化桌面通知"""
        Notify.init('pydoubanfm')
        self.notify = Notify.Notification.new('', '', '')

    def init_indicator(self):
        """初始化系统托盘"""
        try:
            from gi.repository import AppIndicator3

            self.indicator = AppIndicator3.Indicator.new(
                'pydoubanfm', 'applications-multimedia',
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            self.indicator.set_icon(self.program_dir + '/icon.png')
            self.indicator.set_menu(self.get_widget('indicator-menu'))
        except ImportError:
            pass

    def get_widget(self, name):
        """从 glade 中获取 gtk object，该方法实现了缓存

        args:
          name (str): opject id
        """
        if name not in self.widgets:
            self.widgets[name] = self.builder.get_object(name)
        return self.widgets[name]

    def update_notify(self, title='', content='', picture=''):
        """更新桌面通知显示当前歌曲信息"""
        if not title:
            title = self.song['title']
            content = self.song['artist']
            picture = self.album_cover_file

        self.notify.update(title, content, picture)
        self.notify.show()

    def update_indicator_title(self):
        """更新系统托盘中的歌曲信息"""
        self.get_widget('menu-item-title').set_label(
            self.song['title'] + ' - ' + self.song['artist'])

    def login(self, email, password):
        try:
            self.user_info = self.doubanfm.login(email, password)
            self.get_widget('menu-item-login').set_label('注销')
            self.get_widget('menu-item-popup-login').set_label('注销')
            return True
        except LoginError as error:
            self.alert(Gtk.MessageType.WARNING, '登录失败', error)
            return False

    def run(self):
        self.update_playlist('n')
        self.play()
        Gtk.main()

    def play(self):
        self.song = self.playlist[self.play_count]
        self.player.set_uri(self.song['url'])
        self.player.play()
        self.set_album_cover()
        self.set_rate_state()
        self.update_notify()
        self.update_indicator_title()

    def next(self, operation_type):
        """播放下一首
        
        args:
          operation_type (str): 操作类型，详情请参考 https://github.com/qiuxiang/pydoubanfm/wiki/%E8%B1%86%E7%93%A3FM-API
        """
        self.update_playlist(operation_type)
        self.play_count = 0
        self.player.stop()
        self.play()

    def end_report(self):
        """报告已播放完的歌曲"""
        self.doubanfm.get_playlist(self.setting['channel'], 'e', self.song['sid'])

    def update_playlist(self, operation_type):
        self.playlist = self.doubanfm.get_playlist(
            self.setting['channel'], operation_type, self.song['sid'])['song']

    def update_setting_file(self):
        json.dump(
            self.setting,
            open(self.setting_file, 'w'),
            indent=2, ensure_ascii=False)

    def update_channels_file(self):
        json.dump(
            self.channels,
            open(self.channels_file, 'w'),
            indent=2, ensure_ascii=False)

    def on_eos(self):
        """一首歌曲播放完毕的处理"""
        if len(self.playlist) == self.play_count + 1:
            self.update_playlist('p')
            self.play_count = 0
        else:
            self.play_count += 1

        self.end_report()
        self.play()

    def set_kbps(self, widget, kbps):
        # TODO: 点击相同菜单项时会出现 bug
        self.widget_kbps.set_active(False)
        self.widget_kbps = widget
        self.doubanfm.set_kbps(kbps)
        self.setting['kbps'] = kbps
        self.update_setting_file()

    def select_channel(self, widget, channel_id):
        # TODO: 点击相同菜单项时会出现 bug
        self.widget_channel.set_active(False)
        self.widget_channel = widget
        self.setting['channel'] = channel_id
        self.update_setting_file()
        self.next('n')

    def playback(self, widget):
        """播放/暂停"""
        if self.player.get_state() == STATE_PLAYING:
            self.player.pause()
            self.get_widget('button-playback').set_image(
                self.get_widget('image-play'))
            self.get_widget('button-playback').set_tooltip_text('播放')
            self.get_widget('menu-item-playback').set_label('播放')
        else:
            self.player.play()
            self.get_widget('button-playback').set_image(
                self.get_widget('image-pause'))
            self.get_widget('button-playback').set_tooltip_text('暂停')
            self.get_widget('menu-item-playback').set_label('暂停')

    def rate(self, widget):
        """喜欢/取消喜欢"""
        if (type(widget) == Gtk.ToggleButton and self.get_widget('button-rate').get_active()) or \
           (type(widget) == Gtk.MenuItem and not self.get_widget('button-rate').get_active()):
            self.get_widget('button-rate').set_tooltip_text('取消喜欢')
            self.get_widget('menu-item-rate').set_label('取消喜欢')
            if self.song['like'] == 0:
                self.update_playlist('r')
                self.song['like'] = True
                self.play_count = 0
                self.get_widget('button-rate').set_active(True)
        else:
            self.get_widget('button-rate').set_tooltip_text('喜欢')
            self.get_widget('menu-item-rate').set_label('喜欢')
            if self.song['like'] == 1:
                self.update_playlist('u')
                self.song['like'] = False
                self.play_count = 0
                self.get_widget('button-rate').set_active(False)

    def no_longer_play(self, widget):
        """不再播放当前的歌曲"""
        self.next('b')

    def skip(self, widget):
        """跳过当前的歌曲"""
        self.next('s')

    def set_volume(self, widget, value):
        self.player.set_volume(value)

    def open_album(self, widget):
        webbrowser.open('http://music.douban.com' + self.song['album'])

    def album_cover_clicked(self, widget, event):
        """点击专辑封面弹出右键菜单"""
        size = widget.size_request()
        if event.button == 3:
            self.get_widget('menu-popup').popup(
                None, None, None, None, event.button, event.time)

    def show_login_window(self, widget):
        if self.doubanfm.logged:
            # TODO: 实现注销登录功能
            self.alert(Gtk.MessageType.WARNING, 'TODO', '注销功能尚未实现')
        else:
            self.get_widget('window-login').show_all()

    def hide_login_window(self, widget, event):
        self.get_widget('window-login').hide()
        return True

    def do_login(self, widget):
        if (self.login(self.get_widget('entry-email').get_text(),
                       self.get_widget('entry-password').get_text())):
            self.get_widget('window-login').hide()
            self.update_notify('登录成功',
                               self.user_info['user_name'] + ', ' +
                               self.user_info['email'], self.icon_file)
            self.setting['email'] = self.get_widget('entry-email').get_text()
            self.setting['password'] = self.get_widget('entry-password').get_text()
            self.update_setting_file()

    def set_album_cover(self):
        """保存并更新专辑封面"""
        self.album_cover_file = \
            self.album_cover_dir + self.song['picture'].split('/')[-1]
        open(self.album_cover_file, 'wb') \
            .write(requests.get(self.song['picture']).content)
        self.get_widget('image-album-cover').set_from_pixbuf(
            GdkPixbuf.Pixbuf.new_from_file_at_scale(
                self.album_cover_file, 240, -1, True))
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

    @staticmethod
    def exit(*args):
        Gtk.main_quit(*args)

    @staticmethod
    def alert(alert_type, title, message):
        dialog = Gtk.MessageDialog(
            None, 0, alert_type, Gtk.ButtonsType.OK, title)
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()


if __name__ == '__main__':
    import sys

    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')

    DoubanfmPlayer().run()
