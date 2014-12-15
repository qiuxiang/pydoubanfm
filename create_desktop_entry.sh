#!/bin/bash

echo "
[Desktop Entry]
Name=豆瓣FM
Type=Application
Categories=Audio;Music;Player;AudioVideo;
Exec=`pwd`/doubanfm/gtk.py
Icon=`pwd`/doubanfm/res/icon.png
Actions=Skip;Like;Unlike;Remove;

[Desktop Action Skip]
Name=跳过
Exec=`pwd`/doubanfm/cmd.py skip
OnlyShowIn=Unity;

[Desktop Action Like]
Name=喜欢
Exec=`pwd`/doubanfm/cmd.py like
OnlyShowIn=Unity;

[Desktop Action Unlike]
Name=不再喜欢
Exec=`pwd`/doubanfm/cmd.py unlike
OnlyShowIn=Unity;

[Desktop Action Remove]
Name=不再播放
Exec=`pwd`/doubanfm/cmd.py remove
OnlyShowIn=Unity;
" > ~/.local/share/applications/pydoubanfm.desktop