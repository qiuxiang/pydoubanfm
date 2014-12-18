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

## 截图
运行 `create_desktop_entry.py` 可以生成启动菜单项，对于 unity 桌面可以直接通过右键菜单进行控制

![截图 - Desktop Action](https://cloud.githubusercontent.com/assets/1709072/5485876/4fdef1b0-86db-11e4-970b-62318f12f442.png)

提供面板指示器

![截图 - 指示器](https://cloud.githubusercontent.com/assets/1709072/5482934/957a9ed6-86a4-11e4-8057-b4f3e14d4959.png)

提供桌面通知

![截图 - 桌面通知](https://cloud.githubusercontent.com/assets/1709072/5482937/ab01bda2-86a4-11e4-9a5d-f34f8e4fdf25.png)

如果你是一个 geek，或许会喜欢命令行的纯粹

![截图 - 命令行](https://cloud.githubusercontent.com/assets/1709072/5482950/f36ee114-86a4-11e4-875c-392c88e9a59b.png)

我使用 C/S 模式隔离了播放服务和控制客户端，这使得多个不同的终端可以共存，甚至不使用客户端也是可以的

![截图 - 命令行与 gtk](https://cloud.githubusercontent.com/assets/1709072/5482948/f14bf390-86a4-11e4-8cd9-59bf1dffaf49.png)

不管在哪一端进行控制，所有的客户端都会得到反馈

![截图 - 命令行控制](https://cloud.githubusercontent.com/assets/1709072/5482952/f87c8760-86a4-11e4-9057-6db35576bec0.png)

下载的歌曲会写入完整的 mp3 标签

![截图 - mp3 标签](https://cloud.githubusercontent.com/assets/1709072/5482898/d8f610d8-86a3-11e4-82de-faf4cd68fdbb.png)

## 已知的问题
有一定几率出现启动后闪退，重新再启动即可，该 bug 无法稳定重现，调试起来比较麻烦。
