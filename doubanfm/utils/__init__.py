# coding: utf-8
import os
import json
import socket
import requests
import eyeD3

from gi.repository import Notify
Notify.init('pydoubanfm')


class path:
    root = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + '/'
    local = os.path.expanduser('~/.pydoubanfm/')
    album_cover = local + 'album_cover/'
    setting = local + 'setting.json'
    channels = local + 'channels.json'
    user = local + 'user.json'
    cookies = local + 'cookies.txt'


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
