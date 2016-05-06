from os import listdir
from graphmodel import Generator
from graphmodel.NGram import MultiInstrumentNGram

from graphmodel.appio import reader, applogger
from graphmodel.appio.scheduling import PatternSchedule
from graphmodel.appio.writer import MidiFileWriter

__author__ = 'Adisor'

logger = applogger.logger
output_file = "../output/devrun.mid"
# file3 = "music/Eminem/thewayiam.mid"
# file3 = "music/cosifn2t.mid"
file1 = "music/mary.mid"
file2 = "music/bach.mid"
# input_file = "music/autumnno1allegro.mid"
ticks = 10000
nsize = 20
logger.info("Starting Application...")


def reproduce():
    transcript = reader.load_transcript("music/Eminem/forgotaboutdre.mid")
    ngram = MultiInstrumentNGram(nsize)
    ngram.build_from_transcript(transcript)
    scheduled_tracks = Generator.generate_multi_instrument_tracks(ngram, ticks)
    return PatternSchedule(scheduled_tracks=scheduled_tracks, meta=transcript.get_transcript_meta())


def remixing():
    in_transcript = reader.load_transcript(file1)
    in_transcript2 = reader.load_transcript(file2)
    ngram = MultiInstrumentNGram(nsize)
    ngram.build_from_transcript(in_transcript)
    ngram.build_from_transcript(in_transcript2)
    scheduled_tracks = Generator.generate_multi_instrument_tracks(ngram, ticks)
    return PatternSchedule(scheduled_tracks=scheduled_tracks, meta=in_transcript.get_transcript_meta())


def run_from_eminem_music():
    files = listdir("music/Eminem")
    ignored = ["music/Eminem/business.mid", "music/Eminem/forgotaboutdre.mid", "music/Eminem/purple pills.mid"]
               # "music/Eminem/Under_The_Influence.mid"]
    ngram = MultiInstrumentNGram(nsize)
    last_transcript = None
    for file in files:
        path = "music/Eminem/" + file
        if path not in ignored:
            print path
            transcript = reader.load_transcript(path)
            ngram.build_from_transcript(transcript)
            last_transcript = transcript
    scheduled_tracks = Generator.generate_multi_instrument_tracks(ngram, ticks)
    return PatternSchedule(scheduled_tracks=scheduled_tracks, meta=last_transcript.get_transcript_meta())


# pattern_schedule = reproduce()
pattern_schedule = run_from_eminem_music()
MidiFileWriter(pattern_schedule).save_to_file(output_file)
reader.play_music(output_file)
