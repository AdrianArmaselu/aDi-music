from collections import defaultdict
from random import randint
import time

__author__ = 'Adisor'

"""
TODO: Methods for increasing distribution counts:
    velocity tolerance
    ticks tolerance
    duration tolerance
    pitch offset from other song
    pitch tolerance
"""


# TODO: SOME FRAMES HAVE LONG DISTANCES BETWEEN NOTES
# TODO: BUILD NGRAMS WITH PAUSES INCLUDED IN FRAMES, SEE WHAT HAPPENS
# TODO: ADD A LIMIT TO THE SIZE OF THE NGRAM TO BE LESS THAN THE SIZE OF THE SONG ITSELF - MAYBE ADD A RATION
# TODO: SOME NOTES GO INTO LOWER VOLUME DURING PLAY
# TODO: REGENERATING ON EACH CHANNEL DOES NOT YIELD A PLEASANT SOUND
# TODO: TEMPO EVENTS MUST BE PLACED IN A SPECIFIC WAY OTHERWISE IT SOUNDS BAD
# TODO: DO NOT KNOW IF THE NOTES ARE PLACED INTO CHANNELS APPROPRIATELY
# TODO: SPREAD FRAMES ACROSS MULTIPLE INSTRUMENTS
class SingleChannelNGram(object):
    """
    This class builds a statistical model from an input transcript. The statistical model is used by the generator for
    making music

    The statistical model is build as follows:
        The class counts the number of unique same sized consecutive sequences of sound events in a
        transcript's track/channel. Each sequence's size is determined during object instantiation
    """

    def __init__(self, n):
        self.frame_size = n
        self.frame_distribution = defaultdict(int)
        self.indexer = FrameIndexer()

    def build_from_transcript(self, music_transcript):
        for track in music_transcript.get_tracks():
            self.build_from_track(track)

    def build_from_track(self, track):
        frames = OrderedFrames(self.frame_size)
        for sound_event in track.get_sound_events():
            frames.add(sound_event)
            # update the count with the first frame
            if frames.is_first_frame_full():
                frame = frames.remove_first()
                self.frame_distribution[frame] += 1
                self.indexer.index_frame(frame)

    def get_first_frame(self):
        return self.frame_distribution.keys()[0]

    def get_frame_count(self, frame):
        return self.frame_distribution[frame]

    def get_random_frame(self):
        index = randint(0, len(self.frame_distribution) - 1)
        return self.frame_distribution.keys()[index]

    def get_frames_that_start_with_sound_event(self, sound_event):
        return self.indexer.get_frames_that_start_with_sound_event(sound_event)

    def __str__(self):
        string = "NGram:\n"
        for frame in self.frame_distribution:
            string += str(self.frame_distribution[frame]) + ": " + str(frame) + "\n"
        return string


class FrameIndexer:
    def __init__(self):
        # maps frames to the sound events that are first in the frame
        self.first_sound_event_frames = []

    def index_frame(self, frame):
        self.first_sound_event_frames[frame.first()].append(frame)

    def get_frames_that_start_with_sound_event(self, sound_event):
        return self.first_sound_event_frames[sound_event]


class MultiChannelNGram:
    """
    Builds ngram for each channel
    """

    def __init__(self, size):
        self.channel_ngrams = {}
        self.size = size

    def build_from_transcript(self, music_transcript):
        for track in music_transcript.get_tracks():
            self.add_channel_track(channel, music_transcript.get_track(channel))

    def add_channel_track(self, channel, sound_events):
        if channel not in self.channel_ngrams:
            self.channel_ngrams[channel] = SingleChannelNGram(self.size)
        self.channel_ngrams[channel].build_from_track(sound_events)

    def get_channels(self):
        return self.channel_ngrams.keys()

    def get_ngram(self, channel):
        return self.channel_ngrams[channel]


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

    def reset(self):
        self.frames = []

    def __sizeof__(self):
        return len(self.frames)


class Frame(object):
    """
    Object that encapsulates a tuple of SoundEvent objects
    """

    def __init__(self, max_size, sound_events=None):
        self.max_size = max_size
        if sound_events is None:
            self.sound_events = ()
        else:
            self.sound_events = sound_events
        self.hash = None

    def add(self, sound_event):
        self.sound_events += (sound_event,)

    def is_full(self):
        return self.__sizeof__() == self.max_size

    def first(self):
        return self.sound_events[0]

    def last_sound_event(self):
        return self.sound_events[-1]

    def __sizeof__(self):
        return len(self.sound_events)

    def __hash__(self):
        if not self.hash:
            self.hash = hash(self.sound_events)
        return self.hash

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __str__(self):
        string = "Frame:\n"
        for sound_event in self.sound_events:
            string += str(sound_event) + "\n"
        return string
