from twisted.internet import reactor
from ..lib.core import LoginError
from ..utils import setting


class Handler:
    def __init__(self, _protocol, data):
        self.protocol = _protocol
        self.doubanfm = _protocol.factory.doubanfm
        try:
            for row in data.split('\n'):
                if row:
                    data = [item.strip() for item in row.split(' ')]
                    if len(data) == 1:
                        getattr(self, 'action_' + data[0])()
                    elif len(data) == 2:
                        getattr(self, 'action_' + data[0])(data[1])
                    else:
                        getattr(self, 'action_' + data[0])(data[1:])
        except Exception as e:
            self.protocol.send('error', e.message)
            print('error: ' + e.message)

    def action_user_info(self):
        if hasattr(self.doubanfm, 'user_info'):
            self.protocol.send('user_info', self.doubanfm.user_info)
        else:
            self.protocol.send('user_info', None)

    def action_channels(self):
        self.protocol.send('channels', self.doubanfm.channels)

    def action_song(self):
        self.protocol.send('song', self.doubanfm.song)

    def action_like(self):
        self.doubanfm.like()

    def action_unlike(self):
        self.doubanfm.unlike()

    def action_remove(self):
        self.doubanfm.remove()

    def action_skip(self):
        self.doubanfm.skip()

    def action_pause(self):
        self.doubanfm.pause()

    def action_resume(self):
        self.doubanfm.resume()

    def action_set_kbps(self, kbps):
        self.doubanfm.set_kbps(int(kbps))

    def action_get_kbps(self):
        self.protocol.send('kbps', setting.get('kbps'))

    def action_set_channel(self, channel_id):
        self.doubanfm.select_channel(int(channel_id))

    def action_get_channel(self):
        self.protocol.send('channel', setting.get('channel'))

    def action_state(self):
        self.protocol.send('state', self.doubanfm.player.get_state())

    def action_playlist(self):
        self.protocol.send('playlist', self.doubanfm.playlist)

    def action_count(self):
        self.protocol.send('count', self.doubanfm.playlist_count)

    def action_login(self, data):
        result = self.doubanfm.login(data[0], data[1])
        if type(result) is LoginError:
            self.protocol.send('login_failed', result.message)

    def action_exit(self):
        reactor.stop()
