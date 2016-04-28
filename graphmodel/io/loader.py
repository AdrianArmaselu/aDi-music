import midi
import sys

from graphmodel.utils import MidiUtils
from graphmodel.model.Meta import NoteMetaContext
from graphmodel.model.Song import SongTranscript, TranscriptTrack, SongMeta, TrackMetaContext
from graphmodel.model.SongObjects import Note

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
        # loads and converts data from the midi file into notes
        self.track_loader = self.create_track_loader()
        # creates a transcript with the song meta information
        self.transcript = SongTranscript(SongMeta(self.pattern))
        # Used to map instruments to channels
        self.instrument_channel = {}

    def create_track_loader(self):
        """
        Loads the context from the first track and creates a track loader with it
        """
        contexts = NoteGlobalMetaContexts()
        time = 0
        for event in self.pattern[0]:
            time += event.tick
            contexts.add(time, event)
        return TrackLoader(contexts)

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
        timed_track = self.track_loader.load_track(track)
        # check if the track actually has notes then add it to the transcript
        if len(timed_track):
            channel = timed_track.get_meta_context().get_channel()
            instrument = timed_track.get_meta_context().get_instrument()
            # get the channel of the instrument if another track has already used it
            if instrument in self.instrument_channel:
                channel = self.instrument_channel[instrument]
            # set the channel to the track instrument if it is a new instrument
            if instrument not in self.instrument_channel:
                self.instrument_channel[instrument] = channel
            self.transcript.add_track(channel, timed_track)


class TrackLoader:
    """
    Loads the track data and converts it into sound events which are added into a timed track
    """

    def __init__(self, note_global_contexts):
        # This object is used for updating the meta context for each new note that is created
        self.context_tracker = ContextTracker(note_global_contexts)
        # Keeps track of the time after each event
        self.present_time = 0
        # Object represents the current meta context based on global context from the context tracker and track context
        self.current_context = NoteMetaContext()
        # Keeps track of notes whose duration has not been computed
        self.on_notes = {}
        # Used for storing notes converted from file data
        self.transcript_track = TranscriptTrack()

    def load_track(self, track):
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
        self._reset()
        self.transcript_track.set_meta_context(TrackMetaContext(track))
        for event_index in range(0, len(track), 1):
            event = track[event_index]
            self.present_time += event.tick
            self.update_context(event)
            if MidiUtils.is_new_note(event):
                self.add_new_note(event)
            if MidiUtils.has_note_ended(event):
                self.compute_event_note_duration(event)
        return self.transcript_track

    def update_context(self, event):
        """
        Updates the context based on the current event, time, and global context
        """
        global_context = self.context_tracker.get_context_at_time(self.present_time)
        self.current_context.update_from_context(global_context)
        if MidiUtils.is_music_control_event(event):
            self.current_context.update_from_event(event)

    def add_new_note(self, event):
        """
        Creates a new note based on the event and adds it to the track
        """
        note = Note(self.present_time, 0, event, self.current_context.copy())
        self.on_notes[note.pitch] = note
        self.transcript_track.add_note(note)

    def compute_event_note_duration(self, event):
        """
        Computes the duration the note that just ended, which is indicated by the parameter event
        """
        note = self.on_notes[event.pitch]
        note.duration = self.present_time - note.time

    def _reset(self):
        self.present_time = 0
        self.current_context = NoteMetaContext()
        self.on_notes = {}
        self.transcript_track = TranscriptTrack()


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


class ContextTracker:
    """
    This class is used for keeping track of context objects based on the current time
    The class maintains an index that points to the most current context object
    """

    def __init__(self, note_meta_contexts):
        self.contexts = note_meta_contexts
        self.current_index = 0
        self.current = None

    def set_contexts(self, contexts):
        self.contexts = contexts
        self.reset()

    def get_context_at_time(self, time):
        """
        Updates the index and current context object to match the current time and
        returns the updated current context object
        """
        if self.current.time < time and self.current_index < len(self.contexts) - 1:
            self.current_index += 1
            self.current = self.contexts[self.current_index]
        return self.current

    def reset(self):
        self.current_index = 0
        self.current = self.contexts[0]


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
