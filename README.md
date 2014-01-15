pydoubanfm
==========
python 实现的豆瓣电台客户端


目的
----
尽管官方豆瓣电台没有开发 Linux 客户端，却不乏第三方豆瓣电台解决方案。比如 [zonyitoo](https://github.com/zonyitoo) 的 [doubanfm-qt](https://github.com/zonyitoo/doubanfm-qt) （感谢 zonyitoo）。那么我为什么还要重复造轮呢？

1. 我需要一个能完全模拟豆瓣电台行为，能与 ubuntu 结合，足够简单的豆瓣电台客户端
2. 出于学习的目的，我想自己能亲自设计并实现一个豆瓣电台客户端
3. 我想我可以设计出更好的结构，并且把代码复用做得更好


截图
----
![截图](http://qiuxiang.qiniudn.com/pydoubanfm.png)


依赖
----
* requests 2.*
* gst


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
