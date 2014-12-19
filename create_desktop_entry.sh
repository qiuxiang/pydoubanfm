#!/bin/sh

echo "
[Desktop Entry]
Name=豆瓣FM
Type=Application
Categories=Audio;Music;Player;AudioVideo;
Exec=`pwd`/doubanfm/gtk.py
Icon=`pwd`/doubanfm/res/icon.png
Actions=SongNotify;Play;Skip;Like;Unlike;Remove;ServerStart;ServerStop;

[Desktop Action SongNotify]
Name=♬\t当前歌曲
Exec=`pwd`/doubanfm/cmd.py song_notify
OnlyShowIn=Unity;

[Desktop Action Play]
Name=〓\t播放 / 暂停
Exec=`pwd`/doubanfm/cmd.py play
OnlyShowIn=Unity;

[Desktop Action Skip]
Name=→\t下一首
Exec=`pwd`/doubanfm/cmd.py skip
OnlyShowIn=Unity;

[Desktop Action Like]
Name=♥\t喜欢
Exec=`pwd`/doubanfm/cmd.py like
OnlyShowIn=Unity;

[Desktop Action Unlike]
Name=♡\t不再喜欢
Exec=`pwd`/doubanfm/cmd.py unlike
OnlyShowIn=Unity;

[Desktop Action Remove]
Name=✕\t不再播放
Exec=`pwd`/doubanfm/cmd.py remove
OnlyShowIn=Unity;

[Desktop Action ServerStart]
Name=●\t启动服务
Exec=`pwd`/doubanfm/srv.py
OnlyShowIn=Unity;

[Desktop Action ServerStop]
Name=○\t关闭服务
Exec=`pwd`/doubanfm/cmd.py exit
OnlyShowIn=Unity;
" > ~/.local/share/applications/pydoubanfm.desktop