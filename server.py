# encoding: utf-8
import json
from twisted.internet import gireactor
gireactor.install()
from twisted.internet import reactor, protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from doubanfm_player import DoubanfmPlayer


class Handler:
    def __init__(self, _protocol, data):
        self.protocol = _protocol
        self.doubanfm_player = self.protocol.factory.doubanfm_player
        try:
            self.data = json.loads(data)
            getattr(self, 'action_' + self.data[0])(self.data)
        except Exception as e:
            print(e.message)

    def action_channels(self, data):
        self.protocol.send('channels', self.doubanfm_player.channels)

    def action_song(self, data):
        self.protocol.send('song', self.doubanfm_player.song)

    def action_next(self, data):
        self.doubanfm_player.next()

    def action_pause(self, data):
        self.doubanfm_player.pause()


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
        self.doubanfm_player.run()
        self.doubanfm_player.on_play_new = self.on_play_new
        self.doubanfm_player.on_pause = self.on_pause
        self.doubanfm_player.on_play = self.on_play

    def on_play_new(self):
        self.broadcast('play_new', self.doubanfm_player.song)

    def on_pause(self):
        self.broadcast('pause')

    def on_play(self):
        self.broadcast('play')

    def on_login_success(self):
        self.broadcast('login_success', self.doubanfm_player.user_info)

    def broadcast(self, *data):
        for client in self.clients:
            client.send(data)

    def buildProtocol(self, addr):
        return Protocol(self)

if __name__ == '__main__':
    TCP4ServerEndpoint(reactor, 1234).listen(Factory())
    reactor.run()