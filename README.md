pydoubanfm
==========
python 实现的豆瓣FM客户端


目的
----
尽管官方豆瓣FM没有开发 Linux 客户端，却不乏第三方的豆瓣FM客户端。
如 [zonyitoo](https://github.com/zonyitoo) 的 [doubanfm-qt](https://github.com/zonyitoo/doubanfm-qt)
（感谢 zonyitoo 整理的文档）。那么我为什么还要重复造轮呢？

- 我需要一个能完全模拟豆瓣FM行为，能与 linux 桌面整合，简单的豆瓣FM客户端
- 出于学习的目的，我想自己能亲自设计并实现一个豆瓣FM客户端


特性
----
- 集成通知中心，系统托盘
- 完全模拟豆瓣FM行为
- 支持登录
- 支持频道选择
- 支持码率设置（暂不支持实时生效，设置后从下一首歌开始生效）


截图
----
![截图](http://qiuxiang.qiniudn.com/pydoubanfm.png?r=0.1645280309021473)


依赖
----
- requests 2.*
- gst


配置
----
~/.pydoubanfm/setting.json
``` json
{
  "password": "",
  "email": "",
  "channel": 0,
  "kbps": 192
}
```
如果文件不存在，程序会自动创建


运行
----
运行 doubanfm_player.py 即可
