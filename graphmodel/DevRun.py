import logging
import midi
import pygame
from graphmodel.Generator import SingleChannelGenerator, MultiChannelGenerator
from graphmodel.MidiConverter import to_midi_pattern
from graphmodel.MidiIO import MidiIO
from graphmodel.Model import MusicTranscript, Note
from graphmodel.NGram import SingleChannelNGram, MultiChannelNGram
from graphmodel.Policies import PolicyConfiguration, ChannelMixingPolicy, FrameSelectionPolicy, MetadataResolutionPolicy

__author__ = 'Adisor'

Note.SHOW_CONTEXT_INFO = True
FORMAT = '%(asctime)-12s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger()
# logger.setLevel(logging.WARN)
logger.setLevel(logging.INFO)


def run_single_channel():
    # construct the ngram
    ngram = SingleChannelNGram(2)
    ngram.build_from_transcript(transcript)
    # print ngram
    logger.info("Created NGram")

    # construct the generator and generate a sequence of sound events
    generator = SingleChannelGenerator(ngram, num_sound_events, policy_configuration)
    generator.generate(0)
    logger.info("Generated Transcript")
    return generator.transcript


def run_multi_channel():
    # construct the ngram
    ngram = MultiChannelNGram(2)
    ngram.build_from_transcript(transcript)
    logger.info("Created NGram")

    # construct the generator and generate a sequence of sound events
    generator = MultiChannelGenerator(ngram, num_sound_events, policy_configuration)
    generator.generate()
    logger.info("Generated Transcript")

    return generator.transcript


# define properties
midi_file = "music/Eminem/thewayiam.mid"
# midi_file = "music/mary.mid"
# midi_file = "music/bach.mid"
num_sound_events = 100
policy_configuration = PolicyConfiguration(ChannelMixingPolicy.MIX,
                                           FrameSelectionPolicy.RANDOM,
                                           MetadataResolutionPolicy.FIRST_SONG_RESOLUTION)
logger.info("Starting Application...")
data = MidiIO(midi_file)
logger.info(data)
logger.info("Loaded data from file")

# get the notes table
table = data.notes_table
logger.info(data.notes_table)

# build the musical transcript
transcript = MusicTranscript()
transcript.add_tracks(table)
logger.info("Created MusicalTranscript")

transcript = run_multi_channel()
pattern = to_midi_pattern(transcript)
logger.info("Converted Transcript")

midi.write_midifile("devrun.mid", pattern)
logger.info("Saved to File")

pattern = midi.read_midifile("devrun.mid")
logger.info(pattern)

#play the music
pygame.init()
pygame.mixer.music.load("devrun.mid")
pygame.mixer.music.play()
#
while pygame.mixer.music.get_busy():
    pygame.time.wait(1000)
