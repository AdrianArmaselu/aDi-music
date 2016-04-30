import midi
import sys

from graphmodel.utils import MidiUtils
from graphmodel.model.meta import NoteMetaContext
from graphmodel.model.Song import SongTranscript, TranscriptTrack, SongMeta, TrackMetaContext, MetaMap
from graphmodel.model.SongObjects import Note, TimeMeasurements

__author__ = 'Adisor'

"""
PROPER INPUT MIDI FILE FORMAT:
FILE FORMAT = 1
GLOBAL META EVENTS ARE IN THE FIRST TRACK
EACH TRACK HAS ONLY 1 CHANNEL AND 1 INSTRUMENT
"""


def load_transcript(midifile):
    """
    Creates a transcript from the midi file and returns it
    First runs an analysis on the file to check for irregularities in the data
    """
    analyzer = Analyzer(midifile)
    analyzer.perform_analysis()
    loader = TranscriptLoader(midifile)
    loader.load()
    return loader.transcript


class TranscriptLoader:
    """
    Reads the data from the midi file notes and loads it into a transcript

    The class assumes the midi file is in the proper format(read above)
    """

    def __init__(self, midifile):
        # Get the data from the midi file
        self.pattern = midi.read_midifile(midifile)
        # creates a transcript with the song meta information
        self.transcript = SongTranscript(SongMeta(self.pattern))
        # Used to map instruments to channels
        self.instrument_channel = {}

    def load_meta(self):
        """
        """
        meta_map = MetaMap()
        time = 0
        for event in self.pattern[0]:
            time += event.tick
            meta_map.add(time, event)
        self.transcript.meta_map = meta_map

    def load(self):
        """
        First load the context, then loop through each track and load the notes from the tracks
        """
        for track_index in range(1, len(self.pattern), 1):
            self.load_track(self.pattern[track_index])

    def load_track(self, track):
        """
        Creates a track loader object that loads the data from the track and places it in a transcript

        If the loaded track uses the same instrument as another track, no matter the channel, then
        the track will be merged with the other track
        """
        timed_track = load_track(track)
        # check if the track actually has notes then add it to the transcript
        if len(timed_track):
            self.transcript.add_track(timed_track.instrument, timed_track)


def load_track(track):
    """
    The main method for converting the track data into sound events

    Loops sequentially through each event and does the following:
    1. Update the current time from the event
    2. Update the context from the global context at the current time
    3. If the current event is a meta event, then update the current context
    4. If the event is a note on event, then create a new note with the current context, add it to the timed track
        and keep track of it
    5. If the event is an end note event, then compute its duration
    """
    present_time = 0
    on_notes = {}
    transcript_track = TranscriptTrack(MidiUtils.get_instrument(track))
    for event_index in range(0, len(track), 1):
        event = track[event_index]
        present_time += event.tick
        if MidiUtils.is_new_note(event):
            note = Note(start_time=present_time, pitch=event.pitch, volume=event.velocity)
            on_notes[note.pitch] = note
            transcript_track.add_note(note)
        if MidiUtils.has_note_ended(event):
            note = on_notes[event.pitch]
            note.duration = present_time - note.time
    return transcript_track

class NoteGlobalMetaContexts(list):
    """
    Used for storing data about the song meta events in the midi file
    """

    def __init__(self):
        super(NoteGlobalMetaContexts, self).__init__()

    def add(self, time, event):
        """
        Creates a new context object for the time and new event
        The new context maintains meta information from previous context
        """
        if MidiUtils.is_music_control_event(event):
            current_context = self.get_last_if_exists()
            current_context.update_from_event(event)
            current_context.time = time
            self.append(current_context)

    def get_last_if_exists(self):
        """
        Returns a copy of the most previous context object if it exists
        The most previous context object is usually the last one
        """
        last_index = len(self) - 1
        context = NoteMetaContext()
        if last_index >= 0:
            previous_context = self[last_index]
            context = previous_context.copy()
        return context


class Analyzer:
    """
    Class is used for analyzing, input curation, validation, and pre-processing a midi file before execution.
    With this class, we can capture events that are not being processed or midi patterns that break our
    rules or assumptions. If any pattern would break our rules or assumptions, the program exits.
    """
    DO_EXIT = True

    def __init__(self, midi_file):
        self.pattern = midi.read_midifile(midi_file)

    def perform_analysis(self):
        # check for unprocessed events
        for track in self.pattern:
            channel = -1
            for event in track:
                if MidiUtils.is_channel_event(event):
                    if channel == -1:
                        channel = event.channel
                    if channel != event.channel:
                        print "TRACK HAS MULTIPLE CHANNELS"
                        if Analyzer.DO_EXIT:
                            sys.exit(-1)

        # global meta events should be in the first track
        for i in range(1, len(self.pattern), 1):
            for event in self.pattern[i]:
                if MidiUtils.is_song_meta_event(event):
                    print "GLOBAL META EVENTS NEED TO BE IN THE FIRST TRACK", event
                    if Analyzer.DO_EXIT:
                        sys.exit(-1)
