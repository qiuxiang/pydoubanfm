# encoding: utf8

from gi.repository import Gst
Gst.init(None)

STATE_NULL = Gst.State.NULL
STATE_PLAYING = Gst.State.PLAYING
STATE_PAUSED = Gst.State.PAUSED


class Player:
    def __init__(self):
        self.player = Gst.ElementFactory.make('playbin',None)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.message_handler)
        self.bus = bus
        

    def message_handler(self,bus,message):
        if message.type == Gst.MessageType.EOS:
            self.stop()
            if hasattr(self, 'on_eos'):
                self.on_eos()

    def set_volume(self,volume):
        self.player.set_property('volume', volume)

    def set_uri(self, uri):
        self.player.set_property('uri', uri)

    def play(self):
        self.player.set_state(STATE_PLAYING)

    def pause(self):
        self.player.set_state(STATE_PAUSED)

    def stop(self):
        self.player.set_state(STATE_NULL)

    def get_state(self):
        return self.player.get_state(0)[1]

