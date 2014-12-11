# coding: utf-8
import os
import json
import socket
import threading
import subprocess
import requests
import eyeD3
from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory
from gi.repository import Notify
from .lib import Daemon

Notify.init('pydoubanfm')


class path:
    root = os.path.abspath(os.path.dirname(__file__)) + '/'
    local = os.path.expanduser('~/.pydoubanfm/')
    album_cover = local + 'album_cover/'
    setting = local + 'setting.json'
    channels = local + 'channels.json'
    user = local + 'user.json'
    cookies = local + 'cookies.txt'
    pid = '/var/tmp/doubanfm.pid'


class res:
    icon = path.root + 'res/icon.png'
    glade = path.root + 'res/doubanfm.glade'


_notify = Notify.Notification.new('', '', '')
def notify(title, content, picture=res.icon):
    _notify.update(title, content, picture)
    _notify.show()


def json_dump(data, filename):
    json.dump(data, open(filename, 'w'), indent=2, ensure_ascii=False)


def json_dumps(data):
    return json.dumps(data, indent=2, ensure_ascii=False)


def download(url, filename):
    open(filename, 'wb').write(requests.get(url).content)


def port_is_open(port):
    return socket.socket(
        socket.AF_INET, socket.SOCK_STREAM).connect_ex(('127.0.0.1', port)) == 0


def reload_sys():
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')


def stars(rating):
    rating_round = int(round(rating))
    result = ''
    for i in range(0, 5):
        if rating_round > i:
            result += '★'
        else:
            result += '☆'
    return result + ' ' + str(rating)


def second2time(second):
    return '%d:%d' % (second / 60, second % 60)


def add_tag(filename, tags):
    tag = eyeD3.Tag()
    tag.link(filename)
    tag.header.setVersion(eyeD3.ID3_ANY_VERSION)
    tag.setTextEncoding(eyeD3.UTF_8_ENCODING)
    tag.setTitle(tags['title'])
    tag.setAlbum(tags['albumtitle'])
    tag.setArtist(tags['artist'])
    tag.setDate(tags['public_time'])
    tag.addImage(eyeD3.frames.ImageFrame.FRONT_COVER, tags['picture_file'])
    tag.update()


class setting:
    @staticmethod
    def update_file():
        json_dump(setting.data, path.setting)

    @staticmethod
    def get(name):
        return setting.data[name]

    @staticmethod
    def set(name, value):
        setting.data[name] = value
        setting.update_file()

    if not os.path.isdir(path.local):
        os.mkdir(path.local)

    if not os.path.isdir(path.album_cover):
        os.mkdir(path.album_cover)

    if os.path.isfile(path.setting):
        data = json.load(open(path.setting))
    else:
        data = {'channel': 0, 'kbps': 192, 'port': 1234}
        update_file()


class Factory(ReconnectingClientFactory):
    def __init__(self, protocol):
        self.protocol = protocol

    def buildProtocol(self, addr):
        return self.protocol

    def clientConnectionLost(self, connector, reason):
        print('失去连接，正在尝试重新连接……')
        self.retry(connector)

    def clientConnectionFailed(self, connector, reason):
        if self.retries:
            print('连接失败，正在尝试重新连接……')
        self.retry(connector)


class ServerDaemon(Daemon):
    def run(self):
        subprocess.call(path.root + 'srv.py')


def run_client(protocol):
    port = setting.get('port')
    server = ServerDaemon(path.pid)
    if not port_is_open(port):
        if os.path.isfile(path.pid):
            os.remove(path.pid)
        thread = threading.Thread(target=server.start)
        thread.setDaemon(True)
        thread.start()
    reload_sys()
    reactor.connectTCP('127.0.0.1', port, Factory(protocol))
    reactor.run()
