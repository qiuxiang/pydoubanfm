import requests


class Proxy:
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
        self.params.update({
            'channel': channel,
            'type': operation_type,
            'sid': sid})
        return self.request(
            'get', 'radio/people', params=self.params).json()

    def login(self, email, password):
        response = self.request('post', 'login', data={
            'email': email,
            'password': password,
            'app_name': self.app_name,
            'version': self.version}).json()
        if response['err'] == 'ok':
            self.set_auth(response)
            return response
        else:
            raise LoginError(response['err'])

    def get_channels(self):
        return self.request('get', 'radio/channels').json()['channels']

    def set_kbps(self, kbps):
        """:param kbps: 64 or 128 or 192"""
        self.params['kbps'] = kbps

    def set_auth(self, data):
        self.params['user_id'] = data['user_id']
        self.params['expire'] = data['expire']
        self.params['token'] = data['token']
        self.logged = True

    def logout(self):
        self.params.pop('user_id', None)
        self.params.pop('expire', None)
        self.params.pop('token', None)
        self.logged = True

    def get_liked_songs(self, count=20):
        self.params['count'] = count
        return self.request(
            'get', 'radio/liked_songs', params=self.params).json()['songs']


class LoginError(BaseException):
    """Login error exception"""