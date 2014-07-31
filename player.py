# encoding: utf8

"""基于 GStreamer 的音频播放器，兼容 gst0.1 和 gst1.0"""

try:
    from gi.repository import Gst

    Gst.init(None)

    def make_playbin():
        return Gst.ElementFactory.make('playbin', None)

    STATE_NULL = Gst.State.NULL
    STATE_PLAYING = Gst.State.PLAYING
    STATE_PAUSED = Gst.State.PAUSED
    MESSAGE_EOS = Gst.MessageType.EOS
except ImportError:
    import gst

    def make_playbin():
        return gst.element_factory_make('playbin', None)

    STATE_NULL = gst.STATE_NULL
    STATE_PLAYING = gst.STATE_PLAYING
    STATE_PAUSED = gst.STATE_PAUSED
    MESSAGE_EOS = gst.MESSAGE_EOS


class Player:
    def __init__(self):
        self.player = make_playbin()
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.message_handler)

    def message_handler(self, bus, message):
        if message.type == MESSAGE_EOS:
            self.stop()

            # 播放结束钩子
            if hasattr(self, 'on_eos'):
                self.on_eos()

    def set_volume(self, volume):
        """设置音量，取值 [0, 1]"""
        self.player.set_property('volume', volume)

    def set_uri(self, uri):
        """设置播放源，支持本地文件和 http"""
        self.player.set_property('uri', uri)

    def play(self):
        self.player.set_state(STATE_PLAYING)

    def pause(self):
        self.player.set_state(STATE_PAUSED)

    def stop(self):
        self.player.set_state(STATE_NULL)

    def get_state(self):
        """return: STATE_NULL or STATE_PLAYING or STATE_PAUSED"""
        return self.player.get_state(0)[1]
