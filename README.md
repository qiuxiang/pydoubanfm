pydoubanfm
==========
python 实现的豆瓣FM客户端


目的
----
尽管官方豆瓣FM没有开发 Linux 客户端，却不乏第三方豆瓣FM解决方案。比如 [zonyitoo](https://github.com/zonyitoo) 的 [doubanfm-qt](https://github.com/zonyitoo/doubanfm-qt) （感谢 zonyitoo）。那么我为什么还要重复造轮呢？

- 我需要一个能完全模拟豆瓣FM行为，能与 ubuntu 结合，足够简单的豆瓣FM客户端
- 出于学习的目的，我想自己能亲自设计并实现一个豆瓣FM客户端
- 我想我可以设计出更好的结构，并且把代码复用做得更好


特性
----
- 集成 ubuntu 通知中心
- 完全模拟豆瓣FM行为
- 支持登录


截图
----
![截图](http://qiuxiang.qiniudn.com/pydoubanfm-0.1.0.png)


依赖
----
- requests 2.*
- gst


配置
----
~/.pydoubanfm/config.json
``` json
{
  "password": "",
  "email": "",
  "channel": 0
}
```
如果文件不存在，程序会自动创建


运行
----
运行 main.py 即可
