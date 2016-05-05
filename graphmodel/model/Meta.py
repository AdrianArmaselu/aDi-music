from collections import OrderedDict
from graphmodel import defaults
from graphmodel.utils import MidiUtils

__author__ = 'Adisor'


# TODO: events should have tick set to 0
class TranscriptMeta:
    """
    """

    def __init__(self, midiformat=defaults.FORMAT, resolution=defaults.RESOLUTION, key_signature_event=None,
                 time_signature_event=None):
        self.format = midiformat
        self.resolution = resolution
        self.key_signature_event = key_signature_event
        self.time_signature_event = time_signature_event
        self.tempo_dict = OrderedDict()
