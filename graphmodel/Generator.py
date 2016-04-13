import logging
from random import randint
import midi
import pygame
from graphmodel.MidiIO import MidiIO, to_midi_pattern
from graphmodel.Model import MusicalTranscript, Frame
from graphmodel.NGram import NGram
from graphmodel.Policies import FrameSelectionPolicy, PolicyConfiguration, ChannelMixingPolicy, \
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
    """

    def __init__(self, ngram, song_duration, policy_configuration):
        self.ngram = ngram
        # measured in number of notes
        self.frame_distribution = ngram.frame_distribution
        self.song_duration = song_duration
        self.policies = policy_configuration
        self.sequence = []

    def generate(self):
        # first frame
        frame = self.frame_distribution.keys()[0]
        for i in range(0, self.song_duration, 1):
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
            frame = self.ngram.indexed_frames[index]
            count = self.frame_distribution[frame]
            if frame.first() == last_sound_event and (count > max_count):
                max_count = count
                next_frame = frame
        # this means we reached the end of the samples, pick a random next frame
        if next_frame is None:
            next_frame = self.get_random_frame()
        return next_frame

    def get_random_next_frame(self, last_sound_event):
        # this may cause bugs because some sound events have no indexes
        print "last", last_sound_event
        if self.ngram.has_index(last_sound_event):
            indexes = self.ngram.get_sound_event_indexes(last_sound_event)
            key = randint(0, len(indexes) - 1)
            index = indexes[key]
            frame = self.ngram.indexed_frames[index]
        else:
            frame = self.get_random_frame()
        return frame

    def get_random_frame(self):
        index = randint(0, len(self.frame_distribution) - 1)
        return self.frame_distribution.keys()[index]

    def print_sequence(self):
        print "SEQUENCE:"
        for item in self.sequence:
            print item


def log(current, delta):
    print "time: %d, %d" % (current, delta)


# define properties
# midi_file = "music/Eminem/thewayiam.mid"
# midi_file = "music/mary.mid"
midi_file = "music/bach.mid"
number_of_notes = 20
policy_configuration = PolicyConfiguration(ChannelMixingPolicy.MIX,
                                           FrameSelectionPolicy.RANDOM,
                                           MetadataResolutionPolicy.FIRST_SONG_RESOLUTION)
FORMAT = '%(asctime)-12s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info("Starting Application...")
# load file
data = MidiIO(midi_file)
logger.info(data)
logger.info("Loaded data from file")

# get the notes table
table = data.table
print data.table

# build the musical transcript
musical_transcript = MusicalTranscript(table)
# print musical_transcript
logger.info("Created MusicalTranscript")

# construct the ngram
ngram = NGram(musical_transcript, 2, policy_configuration)
# print ngram
logger.info("Created NGram")

# construct the generator and generate a sequence of sound events
generator = MusicGenerator(ngram, number_of_notes, policy_configuration)
generator.generate()
generator.print_sequence()
logger.info("Created Sequence")

pattern = to_midi_pattern(generator.sequence)
logger.info("Converted Sequence")

# save to file
midi.write_midifile("output.mid", pattern)
logger.info("Saved to File")

# play the music
pygame.init()
pygame.mixer.music.load("output.mid")
pygame.mixer.music.play()

while pygame.mixer.music.get_busy():
    pygame.time.wait(1000)
