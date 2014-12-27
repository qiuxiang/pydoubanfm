from twisted.internet import reactor
from ..lib.core import LoginError
from ..utils import Setting


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
            print('error: %s' % e.message)

    def action_user(self):
        if hasattr(self.doubanfm, 'user'):
            self.protocol.send('user', self.doubanfm.user)
        else:
            self.protocol.send('user', None)

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

    def action_next(self):
        self.doubanfm.next(report=False)

    def action_goto(self, index):
        """start from 1"""
        self.doubanfm.play(int(index) - 1)

    def action_pause(self):
        self.doubanfm.pause()

    def action_resume(self):
        self.doubanfm.resume()

    def action_kbps(self, kbps=None):
        if kbps:
            self.doubanfm.set_kbps(int(kbps))
        else:
            self.protocol.send('kbps', Setting.get('kbps'))

    def action_channel(self, channel_id=None):
        if channel_id:
            self.doubanfm.select_channel(int(channel_id))
        else:
            self.protocol.send('channel', Setting.get('channel'))

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

    def action_logout(self):
        self.doubanfm.logout()

    def action_exit(self):
        reactor.stop()

    def action_song_notify(self):
        self.doubanfm.song_notify()

    def action_play(self):
        if self.doubanfm.player.get_state() == 'paused':
            self.doubanfm.resume()
        else:
            self.doubanfm.pause()

    def action_rate(self):
        if self.doubanfm.song['like']:
            self.doubanfm.unlike()
        else:
            self.doubanfm.like()

    def action_volume(self, volume=None):
        if volume:
            self.doubanfm.set_volume(float(volume))
        else:
            self.protocol.send('volume', self.doubanfm.player.get_volume())
