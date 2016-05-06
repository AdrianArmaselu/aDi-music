import midi
import pygame

from graphmodel.appio import applogger
from graphmodel.appio.preprocessing import Analyzer
from graphmodel.model import instruments
from graphmodel.model.Meta import TranscriptMeta
from graphmodel.model.Song import SongTranscript, InstrumentTrack
from graphmodel.model.SongObjects import Note
from graphmodel.utils import MidiUtils

__author__ = 'Adisor'

"""
PROPER INPUT MIDI FILE FORMAT:
FILE FORMAT = 1
GLOBAL META EVENTS ARE IN THE FIRST TRACK
EACH TRACK HAS ONLY 1 CHANNEL AND 1 INSTRUMENT
"""

logger = applogger.logger


def load_transcript(midi_file_name):
    """
    Creates a transcript from the midi file and returns it
    First runs an analysis on the file to check for irregularities in the data
    """
    analyzer = Analyzer(midi_file_name=midi_file_name)
    analyzer.perform_analysis()
    loader = TranscriptLoader()
    loader.load(midi_file_name=midi_file_name)
    logger.debug(loader.transcript)
    return loader.transcript


def play_music(midi_file_name):
    """
    Loads and plays the midi music from the file
    :param midi_file_name: String path
    :return: plays the music
    """
    # play the music
    pygame.init()
    pygame.mixer.music.load(midi_file_name)
    pygame.mixer.music.play()

    # wait until finished
    while pygame.mixer.music.get_busy():
        pygame.time.wait(1000)


class TranscriptLoader(object):
    """
    Reads the data from the midi file notes and loads it into a transcript

    The class assumes the midi file is in the proper format(read above)
    """

    def __init__(self):
        self.pattern = None

        self.transcript = SongTranscript()

    def load(self, midi_file_name):
        """
        First load the context, then loop through each track and load the notes from the tracks
        """
        self.pattern = midi.read_midifile(midi_file_name)
        logger.debug("Loaded Pattern From File")
        logger.debug(self.pattern)
        self.load_meta()
        self.load_tracks()

    def load_meta(self):
        """
        Loads the metadata from the file into the transcript meta object which is then passed to the transcript object
        """
        transcript_meta = TranscriptMeta(midiformat=self.pattern.format, resolution=self.pattern.resolution)
        start_time = 0
        for event in self.pattern[0]:
            start_time += event.tick
            if MidiUtils.is_key_signature_event(event):
                transcript_meta.key_signature_event = event
            if MidiUtils.is_time_signature_event(event):
                transcript_meta.time_signature_event = event
            if MidiUtils.is_set_tempo_event(event):
                transcript_meta.tempo_dict[start_time] = event
        self.transcript.set_transcript_meta(transcript_meta)

    def load_tracks(self):
        """
        Loops through each track after the meta track (the first one), and checks to see if there are any
        notes in the track, and if there are, it proceeds forward to load them.
        """
        for track_index in range(1, len(self.pattern), 1):
            if MidiUtils.has_notes(self.pattern[track_index]):
                self.load_track(self.pattern[track_index])

    def load_track(self, miditrack):
        """
        The main method for converting the track data into sound events

        Loops sequentially through each event and does the following:
        1. Update the current time from the event
        2. If the event is a note on event, then create a new note and add it to the track
        3. If the event is a note off event, then compute its duration
        """
        present_time = 0
        on_notes = {}
        track = InstrumentTrack()
        for event_index in range(0, len(miditrack), 1):
            event = miditrack[event_index]
            present_time += event.tick
            if MidiUtils.is_new_note(event):
                note = Note(start_time=present_time, pitch=event.pitch, volume=event.velocity)
                on_notes[note.pitch] = note
                track.add_note(note)
            if MidiUtils.has_note_ended(event):
                note = on_notes[event.pitch]
                note.duration = present_time - note.start_time
        instrument = MidiUtils.get_instrument(miditrack)
        if instrument is None:
            instrument = instruments.PIANO
        self.transcript.add_track(instrument, track)
