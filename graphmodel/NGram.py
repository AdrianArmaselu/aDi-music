from graphmodel.Model import Frame
from graphmodel.Policies import ChannelMixingPolicy

__author__ = 'Adisor'

"""
TODO: Methods for increasing distribution counts:
    velocity tolerance
    ticks tolerance
    duration tolerance
    pitch offset from other song
    pitch tolerance
"""


def print_tuple(t):
    for event in t:
        print event, "----"


def has_notes(channel_notes):
    return channel_notes and len(channel_notes) > 0


class NGram(object):
    """
    Builds a distribution map that counts the number of unique frames in the song. Key is frame, value is count
    """

    def __init__(self, musical_transcript, n, policy_configuration):
        self.music_transcript = musical_transcript
        self.frame_size = n
        self.policies = policy_configuration
        self.frame_distribution = {}
        # maps indexes to frames
        self.indexed_frames = {}
        # maps sound events to the index in frame_distribution where they start in a frame
        self.sound_event_indexes = {}
        self.event_distribution = {0: {}}
        self.__build__()

    def __build__(self):
        frames = OrderedFrames(self.frame_size)

        if self.policies.channel_mixing_policy is ChannelMixingPolicy.NO_MIX:
            for track in self.music_transcript.tracks:
                for sound_event in self.music_transcript.get_sound_events(track):
                    frames.add(sound_event)
                    # for logging purposes
                    self.update_event_distribution(sound_event)
                    # update the count with the first frame
                    if frames.is_first_frame_full():
                        frame = frames.remove_first()
                        if frame not in self.frame_distribution:
                            self.frame_distribution[frame] = 0
                        self.frame_distribution[frame] += 1
                        self.index_frame(frame)
        # needs implementation
        if self.policies.channel_mixing_policy is ChannelMixingPolicy.MIX:
            pass

    def update_event_distribution(self, sound_event):
        if sound_event not in self.event_distribution:
            self.event_distribution[0][sound_event] = 1
        else:
            self.event_distribution[0][sound_event] += 1

    def index_frame(self, frame):
        key = hash(frame)
        self.indexed_frames[key] = frame
        first_event = frame.first()
        if first_event not in self.sound_event_indexes:
            self.sound_event_indexes[first_event] = []
        self.sound_event_indexes[first_event].append(key)

    def get_sound_event_indexes(self, sound_event):
        return self.sound_event_indexes[sound_event]

    def get_frame(self, index):
        return self.frame_distribution.keys()[index]

    def __str__(self):
        string = "NGram:\n"
        for frame in self.frame_distribution:
            string += str(self.frame_distribution[frame]) + ": " + str(frame) + "\n"
        return string


class OrderedFrames(object):
    """
    Used for constructing the NGram

    Contains consecutive frames - consecutive based on timeline tick
    """

    def __init__(self, frame_size):
        self.frame_size = frame_size
        self.frames = []

    def add(self, sound_event):
        # Adds sound event to all frames
        frame = Frame(self.frame_size)
        self.frames.append(frame)
        for frame in self.frames:
            frame.add(sound_event)

    def remove_first(self):
        frame = self.frames[0]
        del self.frames[0]
        return frame

    def is_first_frame_full(self):
        return self.frames[0].is_full()

    def __sizeof__(self):
        return len(self.frames)
