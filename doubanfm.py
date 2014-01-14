# encoding: utf8

import sys
import requests

class Doubanfm:
    def __init__(self):
        self.app_name = 'radio_desktop_win'
        self.version  = '100'
        self.baseUrl  = 'http://www.douban.fm/j/app/'
        self.session  = requests.Session()
        self.logged   = False
        self.params   = {
            'app_name': self.app_name,
            'version':  self.version,
            'kbps':     192}

    def request(self, method, url, **kwargs):
        return self.session.request(method, self.baseUrl + url, **kwargs)

    def getPlaylist(self, channel, type='n', sid=None):
        self.params.update({
            'channel': channel,
            'type'   : type,
            'sid'    : sid})
        return self.request(
            'get', 'radio/people', params=self.params).json()

    def login(self, email, password):
        response = self.session.request('post',
            'http://www.douban.com/j/app/login',
            data={
                'email'   : email,
                'password': password,
                'app_name': self.app_name,
                'version' : self.version}).json()
        if response['err'] == 'ok':
            self.params['user_id'] = response['user_id']
            self.params['expire']  = response['expire']
            self.params['token']   = response['token']
            self.logged = True
        else:
            raise Exception(response['err'])

    def getChannels(self):
        return self.request('get', 'radio/channels').json()['channels']

    def setKbps(self, kbps):
        self.params['kbps'] = kbps
