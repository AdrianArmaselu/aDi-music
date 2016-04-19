from random import randint
from Model import Frame

__author__ = 'Adisor'

"""
TODO: Methods for increasing distribution counts:
    velocity tolerance
    ticks tolerance
    duration tolerance
    pitch offset from other song
    pitch tolerance
"""


class NGram(object):
    """
    Builds a distribution map that counts the number of unique frames in the song. Key is frame, value is count
    """

    def __init__(self, musical_transcript, n):
        self.music_transcript = musical_transcript
        self.frame_size = n
        self.frame_distribution = {}
        # maps indexes to frames
        self.indexed_frames = {}
        # maps sound events to the index in frame_distribution where they start in a frame
        self.sound_event_indexes = {}
        self.__build__()

    def __build__(self):
        frames = OrderedFrames(self.frame_size)
        for track in self.music_transcript.tracks:
            for sound_event in self.music_transcript.get_sound_events(track):
                frames.add(sound_event)
                # update the count with the first frame
                if frames.is_first_frame_full():
                    frame = frames.remove_first()
                    if frame not in self.frame_distribution:
                        self.frame_distribution[frame] = 0
                    self.frame_distribution[frame] += 1
                    self.index_frame(frame)
            frames.reset()

    def index_frame(self, frame):
        key = hash(frame)
        self.indexed_frames[key] = frame
        first_event = frame.first()
        if first_event not in self.sound_event_indexes:
            self.sound_event_indexes[first_event] = []
        self.sound_event_indexes[first_event].append(key)

    def has_index(self, sound_event):
        return sound_event in self.sound_event_indexes

    def get_first_frame(self):
        return self.frame_distribution.keys()[0]

    def get_frame_count(self, frame):
        return self.frame_distribution[frame]

    def get_sound_event_indexes(self, sound_event):
        return self.sound_event_indexes[sound_event]

    def get_frame(self, index):
        return self.frame_distribution.keys()[index]

    def get_random_frame(self):
        index = randint(0, len(self.frame_distribution) - 1)
        return self.frame_distribution.keys()[index]

    def get_indexed_frame(self, index):
        return self.indexed_frames[index]

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

    def reset(self):
        self.frames = []

    def __sizeof__(self):
        return len(self.frames)
