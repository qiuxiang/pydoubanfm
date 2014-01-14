#!/usr/bin/env python
# encoding: utf8

import os
import json
import requests
from gi.repository import Gtk, Notify
from doubanfm import Doubanfm
from player import *

class DoubanfmPlayer:
    def __init__(self):
        self.initPath()
        self.initBuilder()
        self.initWidget()
        self.initDoubanfm()
        self.initPlayer()
        self.initNotify()

    def initPath(self):
        self.__dir__ = os.path.abspath(os.path.dirname(__file__))
        self.dataDir = os.path.expanduser('~/.pydoubanfm/')
        self.albumCoverDir = self.dataDir + 'albumCover/'
        self.configPath = self.dataDir + 'config.json'

        if not os.path.isdir(self.dataDir):
            os.mkdir(self.dataDir)

        if not os.path.isdir(self.albumCoverDir):
            os.mkdir(self.albumCoverDir)

        if os.path.isfile(self.configPath):
            self.config = json.load(open(self.configPath))
        else:
            self.config = {
                'channel': 0,
                'email': '',
                'password': ''}

    def initBuilder(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.__dir__ + '/doubanfm.glade')
        self.builder.connect_signals(self)
        self.builder.get_object('window-player').show_all()

    def initWidget(self):
        self.buttonPalyback = self.builder.get_object('button-playback')
        self.buttonRate = self.builder.get_object('button-rate')
        self.imagePlay = self.builder.get_object('image-play')
        self.imagePause = self.builder.get_object('image-pause')
        self.imageAlbumCover = self.builder.get_object('image-album-cover')

    def initDoubanfm(self):
        self.doubanfm = Doubanfm()
        self.playCount = 0
        self.song = {'sid': None}
        self.channel = self.config['channel']

        if self.config['email'] and self.config['password']:
            self.login(self.config['email'], self.config['password'])

    def initPlayer(self):
        self.player = Player()
        self.player.onEos = self.onEos

    def initNotify(self):
        Notify.init('pydoubanfm')
        self.notify = Notify.Notification.new('', '', '')

    def updateNotify(self):
        self.notify.update(
            self.song['title'], self.song['artist'], self.albumCoverPath)
        self.notify.show()

    def login(self, email, password):
        try:
            self.doubanfm.login(email, password)
        except Exception, error:
            dialog = Gtk.MessageDialog(None, 0,
                Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, '登录失败')
            dialog.format_secondary_text(error)
            dialog.run()
            dialog.destroy()

    def run(self):
        self.updatePlaylist('n')
        self.play()
        Gtk.main()

    def onEos(self):
        if len(self.playlist) == self.playCount + 1:
            self.updatePlaylist('p')
            self.playCount = 0
        else:
            self.playCount += 1

        self.endReport()
        self.play()

    def play(self):
        self.song = self.playlist[self.playCount]
        self.player.setUri(self.song['url'])
        self.player.play()
        self.setAlbumCover()
        self.setRateState()
        self.updateNotify()

    def endReport(self):
        self.doubanfm.getPlaylist(self.channel, 'e', self.song['sid'])

    def updatePlaylist(self, type):
        self.playlist = self.doubanfm.getPlaylist(
            self.channel, type, self.song['sid'])['song']

    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)
        self.config['channel'] = self.channel
        json.dump(self.config, open(self.configPath, 'w'), indent=2)

    def onPlayback(self, button):
        if self.player.getState() == STATE_PLAYING:
            self.player.pause()
            self.buttonPalyback.set_image(self.imagePlay)
            self.buttonPalyback.set_tooltip_text('播放')
        else:
            self.player.play()
            self.buttonPalyback.set_image(self.imagePause)
            self.buttonPalyback.set_tooltip_text('暂停')

    def onRate(self, button):
        self.playCount = 0
        if self.buttonRate.get_active():
            self.updatePlaylist('r')
            self.buttonRate.set_tooltip_text('取消喜欢')
        else:
            self.buttonRate.set_tooltip_text('喜欢')

    def onDelete(self, button):
        self.next('b')

    def onSkip(self, button):
        self.next('s')

    def next(self, type):
        self.updatePlaylist(type)
        self.playCount = 0
        self.player.stop()
        self.play()

    def setAlbumCover(self):
        self.albumCoverPath = \
            self.albumCoverDir + self.song['picture'].split('/')[-1];
        open(self.albumCoverPath, 'wb') \
            .write(requests.get(self.song['picture']).content)
        self.imageAlbumCover.set_from_file(self.albumCoverPath)
        self.imageAlbumCover.set_tooltip_text(
            '标题：%s\n艺术家：%s\n专辑：%s' % (
                self.song['title'],
                self.song['artist'],
                self.song['albumtitle']))

    def setRateState(self):
        if self.song['like']:
            self.buttonRate.set_active(True)
        else:
            self.buttonRate.set_active(False)

if __name__ == '__main__':
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')

    DoubanfmPlayer().run()
