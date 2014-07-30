#!/bin/bash

echo "
[Desktop Entry]
Name=豆瓣FM
Type=Application
Categories=Audio;Music;Player;AudioVideo;
Exec=`pwd`/main.py
Icon=`pwd`/icon.png" > ~/.local/share/applications/pydoubanfm.desktop
