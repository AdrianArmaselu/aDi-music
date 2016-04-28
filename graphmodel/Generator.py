import logging
from random import randint

import midi

from NGram import SingleChannelNGram, Frame
from graphmodel.io import loader
from graphmodel.model.Policies import FrameSelectionPolicy, PolicyConfiguration, ChannelMixingPolicy, \
    MetadataResolutionPolicy
from graphmodel.io.converter import to_midi_pattern
from graphmodel.model.Song import SongTranscript

__author__ = 'Adisor'


# TODO: BREAK REPEATING LOOPS IN GENERATION
# TODO: OPTIMIZE NGRAM, CONVERTER (TAKES A LONG TIME FOR LARGE N FOR NGRAMS)
# TODO: USE SEED FOR RANDOM GENERATOR TO REPRODUCE
# TODO: GENERATE NOTES INTO A SINGLE TRACK FOR SIMPLICITY IF IT IS WORTH IT
class SingleChannelGenerator(object):
    """
    This class generates music. Currently, it takes the sound event data from an ngram, but that can change
    """

    def __init__(self, singlechannel_ngram, song_duration, policy_configuration, song_meta):
        self.ngram = singlechannel_ngram
        # measured in number of notes
        self.song_duration = song_duration
        self.policies = policy_configuration
        # TODO: GET THE FORMAT AND RESOLUTION FROM NGRAM TRANSCRIPT
        self.transcript = SongTranscript(song_meta)

    def generate(self, channel):
        """
        Generates a track and adds it to the transcript on the specific channel
        :return:
        """
        generated_track = SimpleTrack()
        # first frame
        frame = self.ngram.get_first_frame()
        while len(generated_track) < self.song_duration:
            for sound_event in frame.sound_events:
                generated_track.add_sound_event(sound_event)
            frame = self.next_frame(frame.last_sound_event())
            # we are only concerned about elements after the first one
            frame = Frame(self.ngram.frame_size, frame.sound_events[1:])
        self.transcript.set_track(channel, generated_track)

    # find the frame with the maximum count that starts with last_sound_event
    def next_frame(self, last_sound_event):
        next_frame = None
        if self.policies.selection_policy is FrameSelectionPolicy.HIGHEST_COUNT:
            next_frame = self.get_next_highest_count_frame(last_sound_event)
        if self.policies.selection_policy is FrameSelectionPolicy.RANDOM:
            next_frame = self.get_random_next_frame(last_sound_event)
        if self.policies.selection_policy is FrameSelectionPolicy.PROB:
            next_frame = self.get_prob_next_frame(last_sound_event)
        return next_frame

    def get_next_highest_count_frame(self, last_sound_event):
        next_frame = None
        max_count = 0
        if not self.ngram.has_index(last_sound_event):
            return self.ngram.get_random_frame()
        indexes = self.ngram.get_sound_event_indexes(last_sound_event)
        for index in indexes:
            frame = self.ngram.get_indexed_frame(index)
            count = self.ngram.get_frame_count(frame)
            if frame.first() == last_sound_event and (count > max_count):
                max_count = count
                next_frame = frame
        # this means we reached the end of the samples, pick a random next frame
        if next_frame is None:
            next_frame = self.ngram.get_random_frame()
        return next_frame

    def get_prob_next_frame(self, last_sound_event):
        # Gets the next frame according to probability
        next_frame = None
        total_count = 0
        frame_list = []
        count_list = []
        if not self.ngram.has_index(last_sound_event):
            return self.ngram.get_random_frame()
        indexes = self.ngram.get_sound_event_indexes(last_sound_event)
        for index in indexes:
            frame = self.ngram.get_indexed_frame(index)
            count = self.ngram.get_frame_count(frame)
            if frame.first() == last_sound_event:
                total_count += count
                frame_list.append(frame)
                count_list.append(total_count)
        key = randint(0, total_count)
        for i, count in enumerate(count_list):
            if key <= count:
                next_frame = frame_list[i]
                break
        # this means we reached the end of the samples, pick a random next frame
        if next_frame is None:
            next_frame = self.ngram.get_random_frame()
        return next_frame

    def get_random_next_frame(self, last_sound_event):
        # this may cause bugs because some sound events have no indexes
        if self.ngram.has_index(last_sound_event):
            indexes = self.ngram.get_sound_event_indexes(last_sound_event)
            key = randint(0, len(indexes) - 1)
            index = indexes[key]
            frame = self.ngram.get_indexed_frame(index)
        else:
            frame = self.ngram.get_random_frame()
        return frame


class SimpleTrack:
    def __init__(self):
        self.sound_events = []

    def add_sound_event(self, sound_event):
        return self.sound_events.append(sound_event)

    def get_sound_events(self):
        return self.sound_events

    def __len__(self):
        return len(self.sound_events)


class MultiChannelGenerator:
    def __init__(self, multichannel_ngram, song_duration, policy_configuration, song_meta):
        self.multichannel_ngram = multichannel_ngram
        self.song_duration = song_duration
        self.policies = policy_configuration
        # Used for final output
        self.transcript = SongTranscript(song_meta)

    def generate(self):
        channels = self.multichannel_ngram.get_channels()
        for channel in channels:
            # TODO: SONG DURATION DOES NOT HAVE TO BE self.song_duration FOR THIS GENERATOR
            single_channel_generator = SingleChannelGenerator(self.multichannel_ngram.get_ngram(channel),
                                                              self.song_duration, self.policies,
                                                              self.transcript.get_song_meta())
            single_channel_generator.generate(channel)
            self.transcript.set_track(channel, single_channel_generator.transcript.get_track(channel))


FORMAT = '%(asctime)-12s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def generate(input_file, num_sound_events, folder='default'):
    policy_configuration = PolicyConfiguration(ChannelMixingPolicy.MIX,
                                                FrameSelectionPolicy.RANDOM,
                                               MetadataResolutionPolicy.FIRST_SONG_RESOLUTION)
    in_transcript = loader.load_transcript("%s/%s" % (folder, input_file))
    ngram = SingleChannelNGram(2)
    ngram.build_from_transcript(in_transcript)
    song_meta = in_transcript.get_song_meta()
    generator = SingleChannelGenerator(ngram, num_sound_events, policy_configuration, song_meta)
    generator.generate(0)
    pattern = to_midi_pattern(generator.transcript)
    name = input_file.split('.')[0]
    midi.write_midifile("%s/output-%s.mid" % (folder, name), pattern)
