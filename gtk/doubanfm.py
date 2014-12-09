# coding: utf-8
import threading
import webbrowser
from gi.repository import GLib, Gtk, GdkPixbuf
from client import Protocol as BaseProtocol
from utils import __root__


class Protocol(BaseProtocol):
    def __init__(self):
        self.widgets = {}
        self.builder = Gtk.Builder()
        self.builder.add_from_file(__root__ + '/gtk/doubanfm.glade')
        self.builder.connect_signals(self)
        self.builder.get_object('window-player').show_all()
        self.init_indicator()

    def connectionMade(self):
        BaseProtocol.connectionMade(self)
        self.transport.write('state\nget_kbps\nget_channel\nchannels\nuser_info\nsong')

    def on_channel(self, channel):
        BaseProtocol.on_channel(self, channel)
        self.channel = int(channel)

    def on_user_info(self, user_info):
        BaseProtocol.on_user_info(self, user_info)
        self.user = user_info

    def on_kbps(self, kbps):
        BaseProtocol.on_kbps(self, kbps)
        for kbps_list in ['  64', '128', '192']:
            item = Gtk.CheckMenuItem(kbps_list + ' Kbps', visible=True)
            if str(kbps) == kbps_list.lstrip():
                item.set_active(True)
                self.widget_kbps = item
            item.connect('activate', self.set_kbps, kbps_list.lstrip())
            self.get_widget('menu-kbps').append(item)

    def on_channels(self, channels):
        BaseProtocol.on_channels(self, channels)
        for channel in channels:
            item = Gtk.CheckMenuItem(channel['name'], visible=True)
            if channel['channel_id'] == self.channel:
                item.set_active(True)
                self.widget_channel = item
            item.connect('activate', self.select_channel, channel['channel_id'])
            self.get_widget('menu-channels').append(item)

    def playback(self, widget):
        if self.get_widget('button-playback').get_tooltip_text() == '播放':
            self.transport.write('resume')
        else:
            self.transport.write('pause')

    def on_state(self, state):
        BaseProtocol.on_state(self, state)
        if state == 'playing':
            self.on_resume()
        else:
            self.on_pause()

    def rate(self, widget):
        pass

    def skip(self, widget):
        self.transport.write('skip')

    def on_skip(self):
        BaseProtocol.on_skip(self)

    def on_play(self, song):
        BaseProtocol.on_play(self, song)

    def on_song(self, song):
        BaseProtocol.on_song(self, song)
        self.song = song
        self.get_widget('image-album-cover').set_from_pixbuf(
            GdkPixbuf.Pixbuf.new_from_file_at_scale(
                song['picture_file'], 240, -1, True))
        self.get_widget('image-album-cover').set_tooltip_text(
            '标题：%s\n艺术家：%s\n专辑：%s' % (
                song['title'],
                song['artist'],
                song['albumtitle']))
        self.get_widget('menu-item-title').set_label(
            self.song['artist'] + ' - ' + self.song['title'])

        if song['like']:
            self.get_widget('button-rate').set_active(True)
        else:
            self.get_widget('button-rate').set_active(False)

    def on_like(self):
        BaseProtocol.on_like(self)
        self.get_widget('button-rate').set_tooltip_text('取消喜欢')
        self.get_widget('menu-item-rate').set_label('取消喜欢')
        self.get_widget('button-rate').set_active(True)

    def on_unlike(self):
        BaseProtocol.on_unlike(self)
        self.get_widget('button-rate').set_tooltip_text('喜欢')
        self.get_widget('menu-item-rate').set_label('喜欢')
        self.get_widget('button-rate').set_active(False)

    def on_pause(self):
        BaseProtocol.on_pause(self)
        self.get_widget('button-playback').set_image(
            self.get_widget('image-play'))
        self.get_widget('button-playback').set_tooltip_text('播放')
        self.get_widget('menu-item-playback').set_label('播放')

    def set_volume(self, widget, value):
        pass

    def on_resume(self):
        BaseProtocol.on_resume(self)
        self.get_widget('button-playback').set_image(
            self.get_widget('image-pause'))
        self.get_widget('button-playback').set_tooltip_text('暂停')
        self.get_widget('menu-item-playback').set_label('暂停')

    def select_channel(self, widget, channel_id):
        self.transport.write('set_channel ' + channel_id)

    def set_kbps(self, widget, kbps):
        self.transport.write('set_kbps ' + kbps)

    def open_album(self, widget):
        webbrowser.open('http://music.douban.com' + self.song['album'])

    def album_cover_clicked(self, widget, event):
        """点击专辑封面弹出右键菜单"""
        if event.button == 3:
            self.get_widget('menu-popup').popup(
                None, None, None, None, event.button, event.time)

    def open_download_dialog(self, widget):
        dialog = Gtk.FileChooserDialog('下载', None, Gtk.FileChooserAction.SAVE, (
            '取消', Gtk.ResponseType.CANCEL,
            '确定', Gtk.ResponseType.OK))
        dialog.set_current_name(
            self.song['title'] + ' - ' + self.song['artist'] + '.mp3')
        dialog.set_current_folder(
            GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOWNLOAD))
        if dialog.run() == Gtk.ResponseType.OK:
            threading.Thread(target=self.download, args=(
                self.song['url'], dialog.get_filename())).start()
        dialog.destroy()

    def show_login_window(self, widget):
        if self.user:
            # TODO: 实现注销登录功能
            self.alert(Gtk.MessageType.WARNING, 'TODO', '注销功能尚未实现')
        else:
            self.get_widget('window-login').show_all()

    def hide_login_window(self, widget, event):
        self.get_widget('window-login').hide()
        return True

    def do_login(self, widget):
        self.transport.write('login %s %s' % (
            self.get_widget('entry-email').get_text(),
            self.get_widget('entry-password').get_text()))

    def remove(self, widget):
        self.transport.write('remove')

    def on_login_success(self, user_info):
        BaseProtocol.on_login_success(self, user_info)
        self.get_widget('window-login').hide()
        self.update_notify(
            '登录成功',
            self.user_info['user_name'] + ', ' +
            self.user_info['email'], self.icon_file)

    def init_indicator(self):
        try:
            from gi.repository import AppIndicator3

            self.indicator = AppIndicator3.Indicator.new(
                __name__, 'applications-multimedia',
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            self.indicator.set_icon(__root__ + '/resources/icon.png')
            self.indicator.set_menu(self.get_widget('indicator-menu'))
        except ImportError:
            pass

    def get_widget(self, name):
        if name not in self.widgets:
            self.widgets[name] = self.builder.get_object(name)
        return self.widgets[name]

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
