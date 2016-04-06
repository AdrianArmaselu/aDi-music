__author__ = 'Adisor'


class ChannelMixingPolicy:
    def __init__(self):
        pass

    # means that the count of a tuple will not increase if it has notes in another channel
    NO_MIX = 0

    # means that the count of a tuple will increase if it has notes in another channel
    MIX = 1


class SoundEventTupleSelectionPolicy:
    def __init__(self):
        pass

    HIGHEST_COUNT = 0


# Resolution Events:
# TimeSignatureEvent, TempoChangeEvent, KeySignatureEvent, ControlChangeEvent, PortEvent, ProgramChangeEvent
class MetadataResolutionPolicy:
    def __init__(self):
        pass

    # apply the metadata events to the final song from the first song
    FIRST_SONG_RESOLUTION = 0

    # apply the metadata events to the final song from the second song
    SECOND_SONG_RESOLUTION = 1
