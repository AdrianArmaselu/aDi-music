from collections import OrderedDict

from graphmodel import defaults

__author__ = 'Adisor'


# TODO: events should have tick set to 0
class TranscriptMeta(object):
    """
    Encapsulates metadata about the song
    """

    def __init__(self, midiformat=defaults.FORMAT, resolution=defaults.RESOLUTION, key_signature_event=None,
                 time_signature_event=None):
        # format of the midi file
        self.format = midiformat
        # used in timing measurements
        self.resolution = resolution
        # sets the overall pitch of the composition
        self.key_signature_event = key_signature_event
        # sets the overall timing
        self.time_signature_event = time_signature_event
        # maps tempo events to times
        self.tempo_dict = OrderedDict()
