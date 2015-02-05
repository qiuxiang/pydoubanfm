# coding: utf-8
import os
import json
import random
import socket
import requests
import eyeD3
import colorama
from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory

from gi.repository import Notify
Notify.init('pydoubanfm')
notifier = Notify.Notification.new('', '', '')


class Path:
    def __init__(self):
        pass

    root = os.path.abspath(os.path.dirname(__file__)) + '/'
    local = os.path.expanduser('~/.pydoubanfm/')
    album_cover = local + 'album_cover/'
    setting = local + 'setting.json'
    channels = local + 'channels.json'
    user = local + 'user.json'
    cookies = local + 'cookies.txt'
    pid = '/var/tmp/doubanfm.pid'


class Resource:
    def __init__(self):
        pass

    icon = Path.root + 'res/icon.png'
    glade = Path.root + 'res/doubanfm.glade'


def notify(title, content, picture=Resource.icon):
    notifier.update(title, content, picture)
    notifier.show()


def json_dump(data, filename):
    json.dump(data, open(filename, 'w'), indent=2, ensure_ascii=False)


def json_dumps(data):
    return json.dumps(data, indent=2, ensure_ascii=False)


def download(url, filename):
    open(filename, 'wb').write(requests.get(url).content)


def safe_filename(filename):
    return filename.replace('/', '-')


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
    return '%d:%02d' % (second / 60, second % 60)


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


def music_symbol():
    return random.choice(['♫', '♬', '♪', '♩'])


class Setting:
    @staticmethod
    def update_file(data):
        json_dump(data, Path.setting)

    @staticmethod
    def get(name):
        return Setting.data[name]

    @staticmethod
    def set(name, value):
        Setting.data[name] = value
        Setting.update_file()

    if not os.path.isdir(Path.local):
        os.mkdir(Path.local)

    if not os.path.isdir(Path.album_cover):
        os.mkdir(Path.album_cover)

    if os.path.isfile(Path.setting):
        data = json.load(open(Path.setting))
    else:
        data = {'channel': 0, 'kbps': 192, 'port': 1234}
        update_file.__func__(data)


class Factory(ReconnectingClientFactory):
    def __init__(self, protocol):
        self.protocol = protocol
        self.maxDelay = 1
        self.started = False

    def buildProtocol(self, address):
        self.started = True
        return self.protocol

    def clientConnectionLost(self, connector, reason):
        if not reactor._stopped:
            reactor.stop()

    def clientConnectionFailed(self, connector, reason):
        if self.started and self.retries:
            print('连接失败，正在尝试重新连接……')
        self.retry(connector)


def run_client(protocol):
    reload_sys()
    os.system('nohup ' + Path.root + 'srv.py' + ' > /dev/null &')
    reactor.connectTCP('127.0.0.1', Setting.get('port'), Factory(protocol))
    reactor.run()


class Color:
    def __init__(self):
        pass

    @staticmethod
    def wrap(text, color):
        return color + str(text) + colorama.Fore.RESET

    @staticmethod
    def red(text):
        return Color.wrap(text, colorama.Fore.RED)

    @staticmethod
    def green(text):
        return Color.wrap(text, colorama.Fore.GREEN)

    @staticmethod
    def black(text):
        return Color.wrap(text, colorama.Fore.BLACK)

    @staticmethod
    def yellow(text):
        return Color.wrap(text, colorama.Fore.YELLOW)

    @staticmethod
    def blue(text):
        return Color.wrap(text, colorama.Fore.BLUE)

    @staticmethod
    def magenta(text):
        return Color.wrap(text, colorama.Fore.MAGENTA)

    @staticmethod
    def cyan(text):
        return Color.wrap(text, colorama.Fore.CYAN)

    @staticmethod
    def white(text):
        return Color.wrap(text, colorama.Fore.WHITE)
