from graphmodel import Generator
from graphmodel.Generator import SingleInstrumentGenerator
from graphmodel.NGram import MultiInstrumentNGram
from graphmodel.appio import reader
from graphmodel.appio.scheduler import PatternSchedule
from graphmodel.appio.writer import MidiFileWriter

# constants
from graphmodel.model import Policies

nsize = 10
ticks = 10000
Policies.frame_selection_policy = Policies.FrameSelectionPolicy.RANDOM
input_midi_file_name = "music/bach.mid"
output_midi_file_name = "music/bach-out.mid"

# Create a transcript, this encapsulates the midi data into instrument tracks, where each track contains Note objects
transcript = reader.load_transcript(input_midi_file_name)

# Build the ngram from the track
ngram = MultiInstrumentNGram(nsize)
ngram.build_from_transcript(transcript)

# Generate tracks
scheduled_tracks = Generator.generate_multi_instrument_tracks(ngram, ticks)

# Create a Pattern Schedule
pattern_schedule = PatternSchedule(scheduled_tracks=scheduled_tracks, meta=transcript.get_transcript_meta())

# Convert the Pattern Schedule to an actual Midi Pattern and write it to file
MidiFileWriter(pattern_schedule).save_to_file(output_midi_file_name)

# Play the generated music
reader.play_music(output_midi_file_name)

Policies.FrameSelectionPolicy.PERFECT = "perfect"


class SingleInstrumentPerfectGenerator(SingleInstrumentGenerator):
    def __init__(self, ngram, duration, meta_track):
        super(SingleInstrumentPerfectGenerator, self).__init__(ngram, duration, meta_track)

    def next_perfect_frame(self):
        # Implement your perfect frame selection algorithm
        pass

    def next_frame(self, last_frame_component):
        super(SingleInstrumentPerfectGenerator, self).next_frame(last_frame_component)
        if Policies.frame_selection_policy == Policies.FrameSelectionPolicy.PERFECT:
            self.next_perfect_frame()
