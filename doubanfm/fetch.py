#!/usr/bin/env python
# coding: utf-8

import os
import sys
import json
from gi.repository import GLib
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from doubanfm.lib.core import Player
from doubanfm.utils import add_tag, download, safe_filename, reload_sys, Color

reload_sys()
player = Player()
fetch_path = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_MUSIC) + '/doubanfm/'
songs_file = fetch_path + 'songs.json'

if not os.path.isdir(fetch_path):
    os.mkdir(fetch_path)

if os.path.isfile(songs_file):
    songs = json.load(open(songs_file))
else:
    print('正在下载收藏列表……')
    songs = player.proxy.get_liked_songs(1024)
    json.dump(songs, open(songs_file, 'w'))

for song in songs:
    filename = fetch_path + safe_filename(song['title']) + '.mp3'
    if not os.path.isfile(filename):
        print('→ %s《%s》' % (
            Color.yellow(song['artist']), Color.green(song['title'])))
        download(song['url'], filename)
        player.save_album_cover(song)
        add_tag(filename, song)
