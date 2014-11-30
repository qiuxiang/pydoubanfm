# encoding: utf-8
import os
import json
import utils


def update_file():
    utils.json_dump(setting, setting_file)

def get(name):
    return setting[name]

def set(name, value):
    setting[name] = value
    update_file()

# 本地存储目录
local_dir = os.path.expanduser('~/.pydoubanfm/')
# 专辑封面目录
album_cover_dir = local_dir + 'albumcover/'
# “设置文件”路径
setting_file = local_dir + 'setting.json'
# 频道列表缓存文件路径
channels_file = local_dir + 'channels.json'

if not os.path.isdir(local_dir):
    os.mkdir(local_dir)

if not os.path.isdir(album_cover_dir):
    os.mkdir(album_cover_dir)

if os.path.isfile(setting_file):
    setting = json.load(open(setting_file))
else:
    setting = {'channel': 0, 'kbps': 192, 'port': 1234}
    update_file()
