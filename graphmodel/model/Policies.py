__author__ = 'Adisor'


class PolicyConfiguration:
    """
    Maps values to policies
    """

    def __init__(self, channel_mixing_policy, frame_selection_policy, metadata_resolution_policy):
        self.channel_mixing_policy = channel_mixing_policy
        self.selection_policy = frame_selection_policy
        self.metadata_resolution_policy = metadata_resolution_policy


class ChannelMixingPolicy:
    def __init__(self):
        pass

    # means that the count of a frame will not increase if it has notes in another channel
    NO_MIX = 0

    # means that the count of a frame will increase if it has notes in another channel
    MIX = 1


class FrameSelectionPolicy:
    def __init__(self):
        pass

    HIGHEST_COUNT = 0
    RANDOM = 1
    PROB = 2 # Probabilistic 


class MetadataResolutionPolicy:
    """
    Resolution Events:
    TimeSignatureEvent, TempoChangeEvent, KeySignatureEvent, ControlChangeEvent, PortEvent, ProgramChangeEvent
    """

    def __init__(self):
        pass

    # apply the metadata events to the final song from the first song
    FIRST_SONG_RESOLUTION = 0

    # apply the metadata events to the final song from the second song
    SECOND_SONG_RESOLUTION = 1
