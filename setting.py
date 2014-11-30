# encoding: utf-8
import os
import json
import utils


def update_file():
    utils.json_dump(setting, setting_file)


def get(name):
    return setting[name]


def put(name, value):
    setting[name] = value
    update_file()

local_dir = os.path.expanduser('~/.pydoubanfm/')
albumcover_dir = local_dir + 'albumcover/'
setting_file = local_dir + 'setting.json'
channels_file = local_dir + 'channels.json'
cookies_file = local_dir + 'cookies.txt'

if not os.path.isdir(local_dir):
    os.mkdir(local_dir)

if not os.path.isdir(albumcover_dir):
    os.mkdir(albumcover_dir)

if os.path.isfile(setting_file):
    setting = json.load(open(setting_file))
else:
    setting = {'channel': 0, 'kbps': 192, 'port': 1234}
    update_file()
