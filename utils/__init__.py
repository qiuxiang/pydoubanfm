# coding: utf-8
import os
import requests
import socket
import json

from gi.repository import Notify
import subprocess

Notify.init(__name__)

__root__ = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

resources = {
    'icon': __root__ + '/resources/icon.png',
    'glade': __root__ + '/resources/doubanfm.glade',
}

_notify = Notify.Notification.new('', '', '')


def notify(title, content, picture=resources['icon']):
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
    subprocess.call([
        'eyeD3',
        '--artist', tags['artist'],
        '--album', tags['albumtitle'],
        '--title', tags['title'],
        '--year', tags['public_time'],
        '--set-encoding=utf8',
        '--add-image=%s:FRONT_COVER' % tags['picture_file'],
        '--to-v2.4',
        filename])
