# encoding: utf8

import gst

STATE_NULL    = gst.STATE_NULL
STATE_PLAYING = gst.STATE_PLAYING
STATE_PAUSED  = gst.STATE_PAUSED

class Player:
    def __init__(self):
        self.player = gst.element_factory_make('playbin', 'player')

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.messageHandler)

    def messageHandler(self, bus, message):
        if message.type == gst.MESSAGE_EOS:
            self.stop()
            if hasattr(self, 'onEos'):
                self.onEos()

    def setUri(self, uri):
        self.player.set_property('uri', uri)

    def play(self):
        self.player.set_state(STATE_PLAYING)

    def pause(self):
        self.player.set_state(STATE_PAUSED)

    def stop(self):
        self.player.set_state(STATE_NULL)

    def getState(self):
        return self.player.get_state()[1]
