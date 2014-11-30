# encoding: utf-8
import json
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from twisted.internet import gireactor
gireactor.install()
from twisted.internet import reactor, protocol
from twisted.internet.endpoints import TCP4ServerEndpoint

from doubanfm import LoginError
from doubanfm_player import DoubanfmPlayer
import utils
import setting


class Handler:
    def __init__(self, _protocol, data):
        self.protocol = _protocol
        self.doubanfm_player = self.protocol.factory.doubanfm_player
        try:
            self.data = json.loads(data)
            getattr(self, 'action_' + self.data[0])()
        except Exception as e:
            print('请求出错：' + e.message)

    def action_channels(self):
        self.protocol.send('channels', self.doubanfm_player.channels)

    def action_song(self):
        self.protocol.send('song', self.doubanfm_player.song)

    def action_skip(self):
        self.doubanfm_player.skip()

    def action_rate(self):
        self.doubanfm_player.rate()

    def action_pause(self):
        self.doubanfm_player.pause()

    def action_set_kbps(self):
        self.doubanfm_player.set_kbps(self.data[1])

    def action_get_kbps(self):
        self.protocol.send('kbps', setting.get('kbps'))

    def action_set_channel(self):
        self.doubanfm_player.select_channel(self.data[1])

    def action_get_channel(self):
        self.protocol.send('channel', setting.get('channel'))

    def action_playlist(self):
        self.protocol.send('playlist', self.doubanfm_player.playlist)

    def action_playlist_count(self):
        self.protocol.send('playlist_count', self.doubanfm_player.playlist_count)

    def action_login(self):
        result = self.doubanfm_player.login(
            self.data[1]['email'], self.data[1]['password'])
        if type(result) is LoginError:
            self.protocol.send('login_failed', result.message)


class Protocol(protocol.Protocol):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.factory.clients.append(self)

    def connectionLost(self, reason=protocol.connectionDone):
        self.factory.clients.remove(self)

    def dataReceived(self, data):
        Handler(self, data)

    def send(self, *data):
        self.transport.write(json.dumps(data))


class Factory(protocol.Factory):
    def __init__(self):
        self.clients = []
        self.doubanfm_player = DoubanfmPlayer()
        self.doubanfm_player.on_play_new = self.on_play_new
        self.doubanfm_player.on_pause = self.on_pause
        self.doubanfm_player.on_play = self.on_play
        self.doubanfm_player.on_kbps_change = self.on_kbps_change
        self.doubanfm_player.on_channel_change = self.on_channel_change
        self.doubanfm_player.on_skip = self.on_skip
        self.doubanfm_player.on_no_longer_play = self.on_no_longer_play
        self.doubanfm_player.on_login_success = self.on_login_success
        self.doubanfm_player.run()

    def on_play_new(self):
        self.broadcast('play_new', self.doubanfm_player.song)
        print('开始播放：' + utils.json_dumps(self.doubanfm_player.song))

    def on_pause(self):
        self.broadcast('pause')
        print('暂停播放')

    def on_play(self):
        self.broadcast('play')
        print('恢复播放')

    def on_login_success(self):
        self.broadcast('login_success', self.doubanfm_player.user_info)
        print('登录成功：' + utils.json_dumps(self.doubanfm_player.user_info))

    def on_kbps_change(self):
        self.broadcast('kbps', setting.get('kbps'))
        print('设置收听码率为：%skbps' % setting.get('kbps'))

    def on_channel_change(self):
        self.broadcast('channel', setting.get('channel'))
        print('设置收听频道为：' + setting.get('channel'))

    def on_skip(self):
        self.broadcast('skip')
        print('跳过')

    def on_no_longer_play(self):
        self.broadcast('no_longer_play')
        print('不再播放')

    def on_rate(self):
        if self.doubanfm_player.song['like'] == 0:
            self.broadcast('like')
            print('喜欢')
        else:
            self.broadcast('unlike')
            print('不喜欢')

    def broadcast(self, *data):
        for client in self.clients:
            client.send(data)

    def buildProtocol(self, addr):
        return Protocol(self)

if __name__ == '__main__':
    TCP4ServerEndpoint(reactor, setting.get('port')).listen(Factory())
    reactor.run()
