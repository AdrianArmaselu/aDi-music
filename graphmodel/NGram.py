from collections import defaultdict, Counter, OrderedDict
from random import randint
import time
import operator
from graphmodel.utils import MidiUtils
from graphmodel.utils.iterator import DictIterator

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
# TODO: SPREAD FRAMES ACROSS MULTIPLE INSTRUMENTS
class _SingleInstrumentNGram(object):
    """
    This class builds a statistical model from an input transcript. The statistical model is used by the generator for
    making music

    The statistical model is build as follows:
        The class counts the number of unique same sized consecutive sequences of sound events in a
        transcript's track/channel. Each sequence's size is determined during object instantiation
    """

    def __init__(self, n):
        self.frame_size = n
        self.frame_distribution = defaultdict(FrameStatisticalData)
        self.indexer = SoundEventFrameIndexer(frame_dict=self.frame_distribution)

    def build_from_transcript(self, music_transcript):
        for track in music_transcript.get_tracks():
            self.build_from_track(track, music_transcript.get_tempo_dict())

    def build_from_track(self, track, tempo_dict):
        times = track.times()
        frames = OrderedFrames(self.frame_size)
        tempo_event_iterator = DictIterator(tempo_dict)
        for time_index in range(0, len(times), 1):
            start_time = times[time_index]
            tempo_event = None
            if not tempo_event_iterator.is_empty():
                # update tempo iterator
                while tempo_event_iterator.has_next() and tempo_event_iterator.current_key() < start_time:
                    tempo_event_iterator.go_next()
                if tempo_event_iterator.has_previous() and tempo_event_iterator.current_key() > start_time:
                    tempo_event_iterator.go_previous()
                tempo_event = tempo_event_iterator.current_value()
            sound_event = track.get_sound_event(start_time)

            # update previous pause
            pause_to_previous_event = 0
            if time_index - 1 >= 0:
                pause_to_previous_event = start_time - times[time_index - 1]

            # update next pause
            pause_to_next_event = 0
            if time_index + 1 < len(times):
                pause_to_next_event = times[time_index + 1] - start_time

            # create frame and add it
            frame_component = FrameComponent(sound_event=sound_event, tempo_event=tempo_event,
                                             pause_to_previous_event=pause_to_next_event,
                                             pause_to_next_event=pause_to_previous_event)
            frames.add(frame_component)
            # update the count with the first frame
            if frames.is_first_frame_full():
                frame = frames.remove_first()
                self.frame_distribution[frame].count += 1

    def sort_and_index(self):
        self.indexer.index_frames()

    def get_first_frame(self):
        return self.frame_distribution.keys()[0]

    def get_random_frame(self):
        index = randint(0, len(self.frame_distribution) - 1)
        return self.frame_distribution.keys()[index]

    def get_next_best_frame(self, sound_event):
        return self.indexer.get_best_frame(sound_event)

    def __str__(self):
        string = "NGram:\n"
        for frame in self.frame_distribution:
            string += str(self.frame_distribution[frame]) + ": " + str(frame) + "\n"
        return string


class SoundEventFrameIndexer:
    def __init__(self, frame_dict):
        self.frame_dict = frame_dict
        # maps frames to the sound events that are first in the frame
        self.first_sound_event_frames = defaultdict(lambda: [])

    def index_frames(self):
        for item in self.frame_dict.items():
            self.index_frame_dict_item(item)
        for sound_event in self.first_sound_event_frames:
            self.first_sound_event_frames[sound_event] = sorted(self.first_sound_event_frames[sound_event],
                                                                key=operator.itemgetter(1))

    def index_frame_dict_item(self, item):
        (frame, data) = item
        self.first_sound_event_frames[frame.first()].append(item)

    def get_frames_that_start_with_sound_event(self, sound_event):
        return self.first_sound_event_frames[sound_event]

    def get_best_frame(self, sound_event):
        if len(self.first_sound_event_frames[sound_event]) > 0:
            (frame, data) = self.first_sound_event_frames[sound_event][-1]
            return frame
        return None


class MultiInstrumentNGram:
    """
    Builds ngram for each channel
    """

    def __init__(self, nsize=0):
        self.instrument_ngrams = {}
        self.nsize = nsize

    def build_from_transcript(self, music_transcript):
        for instrument in music_transcript.get_instruments():
            track = music_transcript.get_track(instrument)
            self.add_instrument_track(instrument, track, music_transcript.get_tempo_dict())

    def add_instrument_track(self, instrument, track, tempo_dict):
        if instrument not in self.instrument_ngrams:
            self.instrument_ngrams[instrument] = _SingleInstrumentNGram(self.nsize)
        self.instrument_ngrams[instrument].build_from_track(track, tempo_dict)
        self.instrument_ngrams[instrument].sort_and_index()

    def get_channels(self):
        return self.instrument_ngrams.keys()

    def get_ngram(self, channel):
        return self.instrument_ngrams[channel]

    def get_instruments(self):
        return self.instrument_ngrams.keys()


class OrderedFrames(object):
    """
    Used for constructing the NGram

    Contains consecutive frames - consecutive based on timeline tick
    """

    def __init__(self, frame_size):
        self.frame_size = frame_size
        self.frames = []

    def add(self, frame_component):
        # Adds sound event to all frames
        frame = Frame(self.frame_size)
        self.frames.append(frame)
        for frame in self.frames:
            frame.add(frame_component)

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

    def __init__(self, max_size=0):
        self.max_size = max_size
        self.components = ()
        self.hash = None

    def get_components(self):
        return self.components

    def add(self, frame_component):
        self.components += (frame_component,)

    def remove_first(self):
        self.components = self.components[1:]

    def is_full(self):
        return len(self.components) == self.max_size

    def first(self):
        return self.components[0]

    def last(self):
        return self.components[-1]

    def __sizeof__(self):
        return len(self.components)

    def __hash__(self):
        if not self.hash:
            self.hash = hash(self.components)
        return self.hash

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __str__(self):
        string = "Frame:"
        for component in self.components:
            string += str(component) + ","
        return string


class FrameComponent(object):
    def __init__(self, sound_event, tempo_event=None, pause_to_next_event=0, pause_to_previous_event=0):
        self.sound_event = sound_event
        self.tempo_event = tempo_event
        self.pause_to_next_event = pause_to_next_event
        self.pause_to_previous_event = pause_to_previous_event
        self.hash = None

    def get_sound_event(self):
        return self.sound_event

    def get_pause_to_next_component(self):
        return self.pause_to_next_event

    def get_tempo_event(self):
        return self.tempo_event

    def __hash__(self):
        if self.hash is None:
            self.hash = frame_component_hash_function(self)
        return self.hash

    def __str__(self):
        return "{}{}{}{}".format(self.sound_event, self.tempo_event, self.pause_to_next_event,
                                 self.pause_to_previous_event)


class FrameStatisticalData(object):
    def __init__(self):
        self.count = 0
        self.last_played_elapsed = 0

    def __cmp__(self, other):
        return frame_statistical_data_comparison_function(self, other)

    def __str__(self):
        return "count:{}, elapsed:{}".format(self.count, self.last_played_elapsed)


def prioritize_count_and_last_played_elapsed(frame_statistical_data1, frame_statistical_data2):
    return (frame_statistical_data1.count + frame_statistical_data1.last_played_elapsed) - \
           (frame_statistical_data2.count + frame_statistical_data2.last_played_elapsed)


def hash_sound_event(frame_component):
    return hash(frame_component.sound_event)


frame_statistical_data_comparison_function = prioritize_count_and_last_played_elapsed
frame_component_hash_function = hash_sound_event
