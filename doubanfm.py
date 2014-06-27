# encoding: utf8

import requests,time


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
        retry = 3
        while retry:                
            try:
                return self.session.request(method, self.base_url + url, **kwargs)
            except:
                retry-=1
                continue

    def get_playlist(self, channel, type='n', sid=None):
        self.params.update({
            'channel': channel,
            'type': type,
            'sid': sid})
        return self.request(
            'get', 'radio/people', params=self.params).json()

    def login(self, email, password):
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
            return response['user_name']
        else:
            raise Exception(response['err'])

    def get_channels(self):
        return self.request('get', 'radio/channels').json()['channels']

    def set_kbps(self, kbps):
        self.params['kbps'] = kbps

if __name__=="__main__":
    db = Doubanfm()
    print db.get_channels()
    
