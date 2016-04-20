import logging
from random import randint
import midi
from MidiIO import MidiIO
from Model import MusicTranscript, Frame
from NGram import SingleChannelNGram
from Policies import FrameSelectionPolicy, PolicyConfiguration, ChannelMixingPolicy, \
    MetadataResolutionPolicy
from graphmodel.MidiConverter import to_midi_pattern

__author__ = 'Adisor'


# TODO: GENERATE AND PLAY MULTIPLE CHANNELS
# TODO: BREAK REPEATING LOOPS IN GENERATION
# TODO: Add metadata resolution
# TODO: test for trigrams, quadgrams, pentagrams, etc
# TODO: OPTIMIZE NGRAM, CONVERTER (TAKES A LONG TIME FOR LARGE N FOR NGRAMS)
# TODO: INSTEAD OF GENERATED_TRACK, HAVE MUSICAL TRANSCRIPT
class SingleChannelGenerator(object):
    """
    This class generates music. Currently, it takes the sound event data from an ngram, but that can change

    IMPORTANT: REFRAIN FROM ACCESSING INTERNAL ATTRIBUTES OF NGRAM CLASS TO REDUCE COUPLING

    """

    def __init__(self, singlechannel_ngram, song_duration, policy_configuration):
        self.ngram = singlechannel_ngram
        # measured in number of notes
        self.song_duration = song_duration
        self.policies = policy_configuration
        self.transcript = MusicTranscript()

    def generate(self, channel):
        """
        Generates a track and adds it to the transcript on the specific channel
        :return:
        """
        generated_track = []
        # first frame
        frame = self.ngram.get_first_frame()
        while len(generated_track) < self.song_duration:
            for sound_event in frame.sound_events:
                generated_track.append(sound_event)
            frame = self.next_frame(frame.last_sound_event())
            # we are only concerned about elements after the first one
            frame = Frame(self.ngram.frame_size, frame.sound_events[1:])
        self.transcript.add_track(channel, generated_track)

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


class MultiChannelGenerator:
    def __init__(self, multichannel_ngram, song_duration, policy_configuration):
        self.multichannel_ngram = multichannel_ngram
        self.song_duration = song_duration
        self.policies = policy_configuration
        # Used for final output
        self.transcript = MusicTranscript()

    def generate(self):
        channels = self.multichannel_ngram.get_channels()
        for channel in channels:
            # TODO: SONG DURATION DOES NOT HAVE TO BE self.song_duration FOR THIS GENERATOR
            single_channel_generator = SingleChannelGenerator(self.multichannel_ngram.get_ngram(channel),
                                                              self.song_duration, self.policies)
            single_channel_generator.generate(channel)
            self.transcript.add_track(channel, single_channel_generator.transcript.get_track(channel))


FORMAT = '%(asctime)-12s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def generate(input_file, num_sound_events, folder='default'):
    policy_configuration = PolicyConfiguration(ChannelMixingPolicy.MIX,
                                               FrameSelectionPolicy.RANDOM,
                                               MetadataResolutionPolicy.FIRST_SONG_RESOLUTION)
    data = MidiIO("%s/%s" % (folder, input_file))
    musical_transcript = MusicTranscript()
    musical_transcript.add_tracks(data.notes_table)
    ngram = SingleChannelNGram(2)
    ngram.build_from_transcript(musical_transcript)
    generator = SingleChannelGenerator(ngram, num_sound_events, policy_configuration)
    generator.generate(0)
    pattern = to_midi_pattern(generator.transcript)
    name = input_file.split('.')[0]
    midi.write_midifile("%s/output-%s.mid" % (folder, name), pattern)
