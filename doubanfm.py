# encoding: utf8

"""豆瓣FM API 的封装，提供登录、获取播放列表等功能"""

import requests


class Doubanfm:
    def __init__(self):
        self.app_name = 'radio_desktop_win'
        self.version = '100'
        self.base_url = 'http://www.douban.fm/j/app/'
        self.session = requests.Session()
        self.logged = False
        self.params = {
            'app_name': self.app_name,
            'version': self.version,
            'kbps': 192}

    def request(self, method, url, **kwargs):
        return self.session.request(method, self.base_url + url, **kwargs)

    def get_playlist(self, channel, operation_type='n', sid=None):
        """获取播放列表

        args:
          operation_type (str): 类型，详情请参考 https://github.com/qiuxiang/pydoubanfm/wiki/%E8%B1%86%E7%93%A3FM-API
          sid (int): 反馈给豆瓣FM的歌曲ID

        return:
          [
            {
              aid: "3110880"
              album: "/subject/3110880/"
              albumtitle: "花木兰"
              artist: "徐立"
              company: "乐海盛世"
              kbps: "192"
              length: 218
              like: 0
              picture: "http://img3.douban.com/lpic/s3137993.jpg"
              public_time: "2008"
              rating_avg: 3.28409
              sha256: "81568bcaf1ead8246751c09002927bc36792bae008280ffbc0697d2f6ce4c5fc"
              sid: "252867"
              songlists_count: 0
              ssid: "86d5"
              subtype: ""
              title: "天使的微笑"
              url: "http://mr3.douban.com/201408010036/05e9bc1187055e9027cb875f015413ba/view/song/small/p252867_192k.mp3"
            },
            ...
          ]
        """
        self.params.update({
            'channel': channel,
            'type': operation_type,
            'sid': sid})
        return self.request(
            'get', 'radio/people', params=self.params).json()

    def login(self, email, password):
        """登录豆瓣FM

        return:
           {
             user_id: 用户ID
             user_name: 用户名
             email: 邮箱
             token: 口令
             expire: 过期时间
           }
        """
        response = self.session.request(
            'post',
            'http://www.douban.com/j/app/login',
            data={
                'email': email,
                'password': password,
                'app_name': self.app_name,
                'version': self.version}).json()
        if response['err'] == 'ok':
            self.params['user_id'] = response['user_id']
            self.params['expire'] = response['expire']
            self.params['token'] = response['token']
            self.logged = True
            return response
        else:
            raise LoginError(response['err'])

    def get_channels(self):
        """获取频道列表

        return:
          [
            {
              seq_id: 序号
              channel_id: 频道ID
              name: 频道名
              name_en: 英文名
            },
            ...
          ]
        """
        return self.request('get', 'radio/channels').json()['channels']

    def set_kbps(self, kbps):
        """"设置码率，有效值为 64、128、192"""
        self.params['kbps'] = kbps


class LoginError(BaseException):
    """登录失败异常"""
