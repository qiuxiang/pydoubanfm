#!/bin/bash
# coding: utf-8

projPath=`pwd`
echo $projPath
cp -rf $projPath $HOME/.pydoubanfm

desktop="[Desktop Entry]\n
Name=DouBanFM\n
Name[zh_CN]=豆瓣FM\n
Comment=douban fm\n
Comment[zh_CN]=在线播放fm\n
GenericName=Music Player\n
Type=Application\n
Categories=AudioVideo;Player;GTK;\n
StartupNotify=true\n
Exec=$HOME/.pydoubanfm/doubanfm.py\n
Icon=$HOME/.pydoubanfm/DoubanRadio.png\n"

#echo -e $desktop
echo -e $desktop>$HOME/Desktop/doubanfm.desktop
chmod a+x $HOME/Desktop/doubanfm.desktop

