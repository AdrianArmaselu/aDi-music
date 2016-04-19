import logging
import midi
from graphmodel.Generator import MusicGenerator
from graphmodel.MidiIO import MidiIO, to_midi_pattern
from graphmodel.Model import MusicalTranscript, Note
from graphmodel.NGram import NGram
from graphmodel.Policies import PolicyConfiguration, ChannelMixingPolicy, FrameSelectionPolicy, MetadataResolutionPolicy

__author__ = 'Adisor'

Note.SHOW_CONTEXT_INFO = True
FORMAT = '%(asctime)-12s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger()
# logger.setLevel(logging.WARN)
logger.setLevel(logging.INFO)

# define properties
# midi_file = "music/Eminem/thewayiam.mid"
# midi_file = "music/mary.mid"
midi_file = "music/bach.mid"
num_sound_events = 2
policy_configuration = PolicyConfiguration(ChannelMixingPolicy.MIX,
                                           FrameSelectionPolicy.RANDOM,
                                           MetadataResolutionPolicy.FIRST_SONG_RESOLUTION)

logger.info("Starting Application...")

# load file
data = MidiIO(midi_file)
logger.info(data)
logger.info("Loaded data from file")

# get the notes table
table = data.notes_table
logger.info(data.notes_table)

# build the musical transcript
musical_transcript = MusicalTranscript(table)
# print musical_transcript
logger.info("Created MusicalTranscript")

# construct the ngram
ngram = NGram(musical_transcript, 2)
# print ngram
logger.info("Created NGram")

# construct the generator and generate a sequence of sound events
generator = MusicGenerator(ngram, num_sound_events, policy_configuration)
generator.generate()
generator.print_sequence()
logger.info("Created Sequence")

pattern = to_midi_pattern(generator.sequence)
logger.info("Converted Sequence")

# save to file
midi.write_midifile("devrun.mid", pattern)
logger.info("Saved to File")

pattern = midi.read_midifile("devrun.mid")
logger.info(pattern)
# print pattern

# play the music
# pygame.init()
# pygame.mixer.music.load("output.mid")
# pygame.mixer.music.play()

# while pygame.mixer.music.get_busy():
#     pygame.time.wait(1000)

