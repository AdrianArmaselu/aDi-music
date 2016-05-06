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
        """
        Updates the ngram with the data from the track

        The ngram is updated by creating frames from the sequences of notes and updating their statistical data

        The tempo_dict parameter is used in constructing frame components
        :param track: instrument track
        :param tempo_dict: a dict that maps tempo events to times
        :return: updated ngram
        """
        times = track.times()
        # used to construct the frames
        frames = OrderedFrames(self.frame_size)
        # used to set the tempo of each frame component
        tempo_event_iterator = DictIterator(tempo_dict)
        for time_index in range(0, len(times), 1):
            start_time = times[time_index]
            tempo_event = None
            if not tempo_event_iterator.is_empty():
                # update tempo iterator so that we get the most recent tempo event
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
        """
        :return: sort frames and indexes them for faster generation
        """
        self.indexer.index_frames()

    def get_first_frame(self):
        return self.frame_distribution.keys()[0]

    def get_random_frame(self):
        index = randint(0, len(self.frame_distribution) - 1)
        return self.frame_distribution.keys()[index]

    def get_next_best_frame(self, sound_event):
        """
        :param sound_event: represents context information from last frame
        :return: the next best frame based on the indexer evaluation function
        """
        return self.indexer.get_best_frame(sound_event)

    def __str__(self):
        string = "NGram:\n"
        for frame in self.frame_distribution:
            string += str(self.frame_distribution[frame]) + ": " + str(frame) + "\n"
        return string


class SoundEventFrameIndexer(object):
    def __init__(self, frame_dict):
        # maps statistical data to frames
        self.frame_dict = frame_dict
        # maps frames to the sound events that are first in the frame
        self.first_sound_event_frames = defaultdict(lambda: [])

    def index_frames(self):
        """
        Maps the frames that have s as their starting sound event to s
        The mapped frames are sorted based on the evaluation function of the statistical data object
        """
        for item in self.frame_dict.items():
            self.index_frame_dict_item(item)
        for sound_event in self.first_sound_event_frames:
            self.first_sound_event_frames[sound_event] = sorted(self.first_sound_event_frames[sound_event],
                                                                key=operator.itemgetter(1))

    def index_frame_dict_item(self, item):
        """
        Maps the frame from the item to the sound event which is its start
        :param item: dict key,value pair
        """
        (frame, data) = item
        self.first_sound_event_frames[frame.first()].append(item)

    def get_frames_that_start_with_sound_event(self, sound_event):
        return self.first_sound_event_frames[sound_event]

    def get_best_frame(self, sound_event):
        if len(self.first_sound_event_frames[sound_event]) > 0:
            (frame, data) = self.first_sound_event_frames[sound_event][-1]
            return frame
        return None


class MultiInstrumentNGram(object):
    """
    Builds ngram for each instrument
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

    def get_ngram(self, instrument):
        """
        :param instrument: instrument number
        :return: the ngram object
        """
        return self.instrument_ngrams[instrument]

    def get_instruments(self):
        """
        :return: list of instrument integers
        """
        return self.instrument_ngrams.keys()


class OrderedFrames(object):
    """
    Used for constructing the NGram

    Contains consecutive frames - consecutive based on timeline tick
    """

    def __init__(self, frame_size):
        # corresponds to the nsize of the ngram
        self.frame_size = frame_size
        # list of consecutive frames
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
    Object that encapsulates a tuple of Frame Components, and represents a progression of notes
    """

    def __init__(self, max_size=0):
        self.max_size = max_size
        self.components = ()
        self.hash = None

    def get_components(self):
        """
        :return: the tuple of frame components
        """
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
    """
    Encapsulates the sound event object and data regarding timing
    """
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
    """
    Encapsulates statistical data about its respective frame

    It is crucial in the generation process as next frames are selected based on the comparison
    algorithm of this class
    """
    def __init__(self):
        # number of times the frame associated with this data has appeared before
        self.count = 0
        # indicates how many events have elapsed since this frame has been selected by the generator
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
