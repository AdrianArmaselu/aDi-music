import logging
from random import randint
import midi
# import pygame
from MidiIO import MidiIO, to_midi_pattern
from Model import MusicalTranscript, Frame
from NGram import NGram
from Policies import FrameSelectionPolicy, PolicyConfiguration, ChannelMixingPolicy, \
    MetadataResolutionPolicy

__author__ = 'Adisor'


# TODO: GENERATE AND PLAY MULTIPLE CHANNELS
# TODO: BREAK REPEATING LOOPS IN GENERATION
# TODO: Add metadata resolution
# TODO: test for trigrams, quadgrams, pentagrams, etc
# TODO: OPTIMIZE NGRAM, CONVERTER (TAKES A LONG TIME FOR LARGE N FOR NGRAMS)
class MusicGenerator(object):
    """
    This class generates music. Currently, it takes the sound event data from an ngram, but that can change

    IMPORTANT: REFRAIN FROM ACCESSING INTERNAL ATTRIBUTES OF NGRAM CLASS TO REDUCE COUPLING

    """

    def __init__(self, ngram, song_duration, policy_configuration):
        self.ngram = ngram
        # measured in number of notes
        self.song_duration = song_duration
        self.policies = policy_configuration
        self.sequence = []

    def generate(self):
        # first frame
        frame = self.ngram.get_first_frame()
        while len(self.sequence) < self.song_duration:
            for sound_event in frame.sound_events:
                self.sequence.append(sound_event)
            frame = self.next_frame(frame.last_sound_event())
            # we are only concerned about elements after the first one
            frame = Frame(self.ngram.frame_size, frame.sound_events[1:])

    # find the frame with the maximum count that starts with last_sound_event
    def next_frame(self, last_sound_event):
        next_frame = None
        if self.policies.selection_policy is FrameSelectionPolicy.HIGHEST_COUNT:
            next_frame = self.get_next_highest_count_frame(last_sound_event)
        if self.policies.selection_policy is FrameSelectionPolicy.RANDOM:
            next_frame = self.get_random_next_frame(last_sound_event)
        return next_frame

    def get_next_highest_count_frame(self, last_sound_event):
        next_frame = None
        max_count = 0
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

    def print_sequence(self):
        print "SEQUENCE:"
        for item in self.sequence:
            print item


FORMAT = '%(asctime)-12s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def generate(input_file, num_sound_events, folder='default'):
    policy_configuration = PolicyConfiguration(ChannelMixingPolicy.MIX,
                                               FrameSelectionPolicy.RANDOM,
                                               MetadataResolutionPolicy.FIRST_SONG_RESOLUTION)
    data = MidiIO("%s/%s" % (folder, input_file))
    musical_transcript = MusicalTranscript(data.notes_table)
    ngram = NGram(musical_transcript, 2)
    generator = MusicGenerator(ngram, num_sound_events, policy_configuration)
    generator.generate()
    pattern = to_midi_pattern(generator.sequence)
    name = input_file.split('.')[0]
    midi.write_midifile("%s/output-%s.mid" % (folder, name), pattern)
