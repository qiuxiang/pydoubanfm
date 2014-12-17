# encoding: utf-8
from gi.repository import Gst
Gst.init(None)

from .hooks import Hooks


class GstPlayer:
    status = {
        Gst.State.NULL: 'null',
        Gst.State.PLAYING: 'playing',
        Gst.State.PAUSED: 'paused',
        Gst.State.READY: 'ready',
    }

    def __init__(self):
        self.hooks = Hooks()
        self.player = Gst.ElementFactory.make('playbin', None)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.message_handler)

    def message_handler(self, bus, message):
        if message.type == Gst.MessageType.EOS:
            self.stop()
            self.hooks.dispatch('eos')

    def set_volume(self, volume):
        self.player.set_property('volume', volume)

    def set_uri(self, uri):
        self.player.set_property('uri', uri)

    def play(self):
        self.player.set_state(Gst.State.PLAYING)

    def pause(self):
        self.player.set_state(Gst.State.PAUSED)

    def stop(self):
        self.player.set_state(Gst.State.NULL)

    def get_state(self):
        return self.status[self.player.get_state(0)[1]]
