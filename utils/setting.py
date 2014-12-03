import os
import json
from utils import json_dump


def update_file():
    json_dump(setting, setting_file)


def get(name):
    return setting[name]


def put(name, value):
    setting[name] = value
    update_file()

local_dir = os.path.expanduser('~/.pydoubanfm/')
album_cover_dir = local_dir + 'album_cover/'
setting_file = local_dir + 'setting.json'
channels_file = local_dir + 'channels.json'
user_file = local_dir + 'user.json'
cookies_file = local_dir + 'cookies.txt'

if not os.path.isdir(local_dir):
    os.mkdir(local_dir)

if not os.path.isdir(album_cover_dir):
    os.mkdir(album_cover_dir)

if os.path.isfile(setting_file):
    setting = json.load(open(setting_file))
else:
    setting = {'channel': 0, 'kbps': 192, 'port': 1234}
    update_file()
