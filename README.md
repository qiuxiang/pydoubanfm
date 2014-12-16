# pydoubanfm
python 实现的豆瓣电台播放器

## 目的
尽管官方豆瓣FM没有开发 Linux 客户端，却不乏第三方的豆瓣FM客户端。
如 [zonyitoo](https://github.com/zonyitoo) 的 [doubanfm-qt](https://github.com/zonyitoo/doubanfm-qt)
（感谢 zonyitoo 整理的文档）。那么我为什么还要重复造轮呢？

- 我需要一个能完全模拟豆瓣FM行为，能与 linux 桌面整合，简单的豆瓣FM客户端
- 出于学习的目的，我想自己能亲自设计并实现一个豆瓣FM客户端

## 特性
- 集成通知中心，系统托盘，Launcher
- 完全模拟豆瓣FM行为
- 支持下载
- 支持登录
- 支持频道选择
- 支持码率设置（暂不支持实时生效，设置后从下一首歌开始生效）
- 多终端支持，提供 Gtk、命令行客户端

## 依赖
- python-requests
- python-eyed3
- python-twisted
- python-gst-1.0

作者常用的操作系统是 Ubuntu 最新版，当然，其他 Linux 发行版也基本可以保证支持（主要是解决依赖）。
至于 OS X，原则上是可以支持的，关键是 pygtk3 和 gst1.0 的安装。Windows 同理，但依赖的解决更为困难。
以 Ubuntu 为例，运行以下命令：

```sh
$ sudo apt-get install python-requests python-eyed3 python-twisted python-gst-1.0
```

## 运行
在项目目录下运行 `create_desktop_entry.sh` 会创建启动项，这样，你就可以在所有程序里启动豆瓣FM。
你也可以直接从命令行启动，运行 `./doubanfm/gtk.py` 或 `python -m doubanfm.gtk`
