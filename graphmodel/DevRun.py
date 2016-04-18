import logging
import midi
from graphmodel.Generator import MusicGenerator
from graphmodel.MidiIO import MidiIO, to_midi_pattern
from graphmodel.Model import MusicalTranscript
from graphmodel.NGram import NGram
from graphmodel.Policies import PolicyConfiguration, ChannelMixingPolicy, FrameSelectionPolicy, MetadataResolutionPolicy

__author__ = 'Adisor'

FORMAT = '%(asctime)-12s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# define properties
# midi_file = "music/Eminem/thewayiam.mid"
# midi_file = "music/mary.mid"
midi_file = "music/bach.mid"
number_of_notes = 20
policy_configuration = PolicyConfiguration(ChannelMixingPolicy.MIX,
                                           FrameSelectionPolicy.RANDOM,
                                           MetadataResolutionPolicy.FIRST_SONG_RESOLUTION)

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
midi.write_midifile("devrun.mid", pattern)
logger.info("Saved to File")

pattern = midi.read_midifile("devrun.mid")
print pattern

# play the music
# pygame.init()
# pygame.mixer.music.load("output.mid")
# pygame.mixer.music.play()

# while pygame.mixer.music.get_busy():
#     pygame.time.wait(1000)

