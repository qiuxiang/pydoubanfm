pydoubanfm
==========

<p>Ubuntu下Python实现的豆瓣电台客户端</p>
<p>目前，该程序仅实现了客户端的基本功能，并未实现登录界面。如需登录，请修改DoubanfmMain::__init__里的self.doubanfm = DoubanfmBase('username', 'password', onStar=self.onStart)。</p>

###ubuntu安装步骤

$ git clone https://github.com/hanxi/pydoubanfm.git <br>
$ cd pydoubanfm<br>
$ ./install<br>

然后就可以看到豆瓣FM在桌面上了.
