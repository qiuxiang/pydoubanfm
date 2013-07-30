#!/usr/bin/python
# coding: utf-8

import sys
import os
import threading
import time
import json
import getopt
import getpass
import requests
import pynotify
import keybinder
import gst
import gtk


# 基础类
class DoubanfmBase:
    def __init__(self, email='', password='', onStart=None):
        self.app_name = 'radio_desktop_win'
        self.version = '100'
        self.requests = requests.Session()
        self.projPath = os.path.realpath(sys.path[0])
        self.pictureDir = self.projPath + '/picture/'
        self.params = {
            'app_name': self.app_name,
            'version': self.version,
            'user_id': '',
            'expire': '',
            'token': '',
            'channel': 0,
            'type': 'n'}
        self.player = gst.element_factory_make('playbin', 'player')
        self.event = threading.Event()
        self.playing = False
        self.isLogin = False
        self.onStart = onStart
        self.channels = self.getChannels()

        pynotify.init(self.app_name)
        self.notify = pynotify.Notification('')
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.on_message)

        if email != '' and password != '':
            self.login(email, password)


    # gst 消息处理
    def on_message(self, bus, message):
        if message.type == gst.MESSAGE_EOS:
            self.next()


    # 登录
    def login(self, email, password):
        response = json.loads(self.requests.post(
            'http://www.douban.com/j/app/login',
            data={
                'email': email,
                'password': password,
                'app_name': self.app_name,
                'version': self.version}).content)
        if response['err'] == 'ok':
            self.params['user_id'] = response['user_id']
            self.params['expire'] = response['expire']
            self.params['token'] = response['token']
            self.isLogin = True
            print  '“%s”登录成功' % response['user_name']
            return True
        else:
            print 'login failed: %s' % response['err']
            return False


    # 选择频道
    def setChannel(self, channel):
        self.params['channel'] = channel
        print '当前频道：' + str(channel)


    # 添加/移除红心
    def like(self):
        params = self.params
        params['sid'] = self.song['sid']
        if self.song['like'] == 0:
            params['type'] = 'r'
            self.song['like'] = 1
            print '喜欢这首歌'
        else:
            params['type'] = 'u'
            self.song['like'] = 0
            print '取消喜欢'
        self.requests.get(
            'http://www.douban.com/j/app/radio/people',
            params=params)


    # 不再播放
    def remove(self):
        params = self.params
        params['sid'] = self.song['sid']
        params['type'] = 'b'
        self.requests.get(
            'http://www.douban.com/j/app/radio/people',
            params=params)
        self.next()
        print '不再播放'


    # 获取播放列表
    def playlist(self):
        if hasattr(self, 'song'):
            params = self.params
            params['sid'] = self.song['sid']
            params['type'] = 's'
        return json.loads(self.requests.get(
            'http://www.douban.com/j/app/radio/people',
            params=self.params).content)


    # 保存专辑封面
    def save(self, url):
        file = open(self.song['picturePath'], 'wb')
        file.write(requests.get(url).content)
        file.close()


    # 获取频道列表
    def getChannels(self):
        channels = json.loads(requests.get(
            'http://www.douban.com/j/app/radio/channels').content)['channels']
        # 由于红心兆赫没有出现在获取的播放列表里，需要手动添加
        channels.append({
            'name_en': 'Favorite Radio',
            'seq_id': len(channels),
            'abbr_en': 'Favorite',
            'name': '红心兆赫',
            'channel_id': -3})
        return channels


    # 主线程函数，循环播放
    def mainloop(self):
        while True:
            self.song = self.playlist()['song'][0]
            self.song['picturePath'] = \
                self.pictureDir + self.song['picture'].split('/')[-1]
            self.save(self.song['picture'])

            # 发送桌面通知
            self.notify.update(
                self.song['title'],
                self.song['artist'] + '\n' + self.song['albumtitle'],
                self.song['picturePath'])
            self.notify.show()

            self.player.set_property('uri', self.song['url'])
            self.player.set_state(gst.STATE_PLAYING)
            self.playing = True

            print '%s：%s《%s》' % (
                self.song['title'],
                self.song['artist'],
                self.song['albumtitle'])

            if self.onStart != None:
                self.onStart()

            # 让线程进入等待状态，等待激活信号
            self.event.wait()
            self.event.clear()


    # 播放/暂停
    def pause(self):
        if self.playing:
            self.player.set_state(gst.STATE_PAUSED)
            self.playing = False
            print '暂停'
        else:
            self.player.set_state(gst.STATE_PLAYING)
            self.playing = True
            print '继续播放'


    # 下一首
    def next(self):
        self.player.set_state(gst.STATE_NULL)
        self.event.set()


    # 开启主播放线程
    def run(self):
        self.thread = threading.Thread(target=self.mainloop)
        self.thread.start()


    # 销毁播放器，目前尚未找到结束播放线程的方法
    def destroy(self):
        self.thread._Thread__stop()



# 主播放图形界面
class DoubanfmMain(gtk.Window):
    def __init__(self):
        super(DoubanfmMain, self).__init__()
        self.likeText = '★'
        self.unlikeText = '☆'
        self.channel_seq = 0

        '''
        self.doubanfm = DoubanfmBase(
            'username', 'password', onStart=self.onStart)
        '''
        self.doubanfm = DoubanfmBase(onStart=self.onStart)
        self.doubanfm.run()

        self.set_title('豆瓣电台')
        self.set_size_request(180, 210)
        self.set_resizable(False)
        self.set_position(gtk.WIN_POS_CENTER)
        self.createInterior()
        self.show_all()
        self.connect('key-press-event', self.onKeypress)
        self.connect('destroy', self.destroy)


    # 创建主界面
    def createInterior(self):
        fixed = gtk.Fixed()
        self.add(fixed)

        # 专辑封面
        self.picture = gtk.Image()
        self.picture.set_size_request(160, 160)
        fixed.put(self.picture, 10, 10)

        # 播放/暂停按钮
        self.pauseImage = gtk.Image()
        self.pauseImage.set_from_stock(
            gtk.STOCK_MEDIA_PAUSE, gtk.ICON_SIZE_BUTTON)
        self.pauseButton = gtk.Button()
        self.pauseButton.add(self.pauseImage)
        self.pauseButton.connect('clicked', self.pause)
        self.pauseButton.set_relief(gtk.RELIEF_NONE)
        self.pauseButton.set_can_focus(False)
        self.pauseButton.set_tooltip_text('暂停')
        fixed.put(self.pauseButton, 24, 170)

        # 下一首按钮
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_MEDIA_NEXT, gtk.ICON_SIZE_BUTTON)
        button = gtk.Button()
        button.add(image)
        button.connect('clicked', self.next)
        button.set_relief(gtk.RELIEF_NONE)
        button.set_can_focus(False)
        button.set_tooltip_text('下一首')
        fixed.put(button, 50, 170)

        # 收藏按钮
        self.likeButton = gtk.Button(self.unlikeText)
        self.likeButton.set_size_request(26, 26)
        self.likeButton.set_relief(gtk.RELIEF_NONE)
        self.likeButton.set_can_focus(False)
        self.likeButton.connect('clicked', self.like)
        fixed.put(self.likeButton, 76, 170)

        # 不再播放按钮
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_DELETE, gtk.ICON_SIZE_BUTTON)
        button = gtk.Button()
        button.add(image)
        button.set_relief(gtk.RELIEF_NONE)
        button.set_can_focus(False)
        button.connect('clicked', self.remove)
        button.set_tooltip_text('不再播放')
        fixed.put(button, 102, 170)

        # 播放列表按钮
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_BUTTON)
        button = gtk.Button()
        button.add(image)
        button.set_relief(gtk.RELIEF_NONE)
        button.set_can_focus(False)
        button.set_tooltip_text('播放列表')
        button.connect('clicked', self.showChannelsDialog)
        fixed.put(button, 128, 170)


    # 频道选择对话框
    def showChannelsDialog(self, widget):
        self.channelsDialog = gtk.Dialog(
            title='频道选择',
            parent=self,
            flags=gtk.DIALOG_MODAL)

        # 载入频道选项
        listStore = gtk.ListStore(str)
        for item in self.doubanfm.channels:
            listStore.append([item['name']])

        treeView = gtk.TreeView(listStore)
        treeView.set_headers_visible(False)
        treeView.append_column(
            gtk.TreeViewColumn('name', gtk.CellRendererText(), text=0))
        treeView.connect('row-activated', self.onSelected)
        treeView.set_cursor((self.channel_seq,))

        scrollBox = gtk.ScrolledWindow()
        scrollBox.set_size_request(120, 200)
        scrollBox.add(treeView)
        self.channelsDialog.vbox.pack_start(scrollBox)
        self.channelsDialog.show_all()
        result = self.channelsDialog.run()
        self.channelsDialog.destroy()


    # 频道被选中
    def onSelected(self, tree, path, colum):
        self.doubanfm.setChannel(
            self.doubanfm.channels[path[0]]['channel_id'])
        self.channel_seq = path[0]
        self.doubanfm.next()
        self.channelsDialog.destroy()


    # 开始播放时处理
    def onStart(self):
        self.picture.set_from_file(self.doubanfm.song['picturePath'])
        self.picture.set_tooltip_text(
            '标题：%s\n艺术家：%s\n专辑：%s' % (
                self.doubanfm.song['title'],
                self.doubanfm.song['artist'],
                self.doubanfm.song['albumtitle']))
        self.changeLikeStatus()


    # 在浏览器中查看专辑信息
    def viewAlbum(self, widget):
        pass


    # 退出
    def destroy(self, widget):
        self.doubanfm.destroy()
        gtk.main_quit()


    # 播放/暂停
    def pause(self, widget):
        self.doubanfm.pause()
        if self.doubanfm.playing:
            self.pauseImage.set_from_stock(
                gtk.STOCK_MEDIA_PAUSE, gtk.ICON_SIZE_BUTTON)
            self.pauseButton.set_tooltip_text('暂停')
        else:
            self.pauseImage.set_from_stock(
                gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_BUTTON)
            self.pauseButton.set_tooltip_text('播放')


    # 添加/移除红心
    def like(self, widget):
        self.doubanfm.like()
        self.changeLikeStatus()


    # 不再播放
    def remove(self, widget):
        self.doubanfm.remove()


    # 下一首
    def next(self, widget):
        self.doubanfm.next()


    # 改变红心状态
    def changeLikeStatus(self):
        if self.doubanfm.song['like'] == 0:
            self.likeButton.set_label(self.unlikeText)
            self.likeButton.set_tooltip_text('喜欢这首歌')
        else:
            self.likeButton.set_label(self.likeText)
            self.likeButton.set_tooltip_text('取消喜欢')


    # 按键处理
    def onKeypress(self, widget, event):
        # 下一首
        if event.keyval == gtk.keysyms.n \
            or event.keyval == gtk.keysyms.Right:
            self.next(widget)
        # 暂停
        elif event.keyval == gtk.keysyms.space \
            or event.keyval == gtk.keysyms.p:
            self.pause(widget)


if __name__ == '__main__':
    gtk.threads_init()
    DoubanfmMain()
    gtk.main()
