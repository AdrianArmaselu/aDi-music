import midi

from graphmodel.utils import MidiUtils
from graphmodel.model.Meta import MetaContext
from graphmodel.model.Song import MusicTranscript
from graphmodel.model.SongObjects import Note

__author__ = 'Adisor'


def get_transcript(midifile):
    loader = TranscriptLoader(midifile)
    loader.load()
    return loader.transcript


class TranscriptLoader:
    def __init__(self, midifile):
        self.pattern = midi.read_midifile(midifile)
        self.context_tracker = ContextTracker()
        self.transcript = MusicTranscript()

    def load(self):
        self.load_context()
        for track in self.pattern:
            self.load_track(track)

    def load_context(self):
        contexts = GlobalMetaContexts()
        time = 0
        for event in self.pattern[0]:
            time += event.tick
            contexts.add(time, event)
        self.context_tracker.set_contexts(contexts)

    def load_track(self, track):
        track_loader = TrackLoader(self.context_tracker, self.transcript)
        track_loader.load_track(track)
        self.context_tracker.reset()


class TrackLoader:
    def __init__(self, context_tracker, transcript):
        self.context_tracker = context_tracker
        self.transcript = transcript
        self.time = 0
        self.current_context = MetaContext()
        self.on_notes = {}
        self.recent_off_notes = {}

    def load_track(self, track):
        for event_index in range(0, len(track), 1):
            event = track[event_index]
            self.time += event.tick
            self.update_context(event)
            if MidiUtils.is_new_note(event):
                note = Note(self.time, 0, event, self.current_context)
                self.on_notes[note.pitch] = note
                self.update_and_remove_recent_off_notes(event)
                note.pause_to_previous_note = note.time - self.transcript.get_time_lt(event.channel, self.time)
                self.transcript.add_note(note)
            if MidiUtils.has_note_ended(event):
                note = self.on_notes[event.pitch]
                note.duration = self.time - note.time
                self.recent_off_notes[note.pitch] = note

    def update_context(self, event):
        global_context = self.context_tracker.get_context_at_time(self.time)
        self.current_context.update_from_context(global_context)
        if MidiUtils.is_music_control_event(event):
            self.current_context.update_from_event(event)

    def update_and_remove_recent_off_notes(self, event):
        if event.tick != 0:
            for note in self.recent_off_notes.values():
                note.pause_to_next_note = self.time - note.time
                del self.recent_off_notes[note.pitch]


class GlobalMetaContexts(list):
    def __init__(self):
        super(GlobalMetaContexts, self).__init__()

    def add(self, time, event):
        current_context = self.get_last_if_exists()
        current_context.update_from_event(event)
        current_context.time = time
        self.append(current_context)

    def get_last_if_exists(self):
        last_index = len(self) - 2
        context = MetaContext()
        if last_index >= 0:
            previous_context = self[last_index]
            context = previous_context.copy()
        return context


class ContextTracker:
    def __init__(self):
        self.contexts = []
        self.current_index = 0
        self.current = None

    def set_contexts(self, contexts):
        self.contexts = contexts
        self.reset()

    def get_context_at_time(self, time):
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

    def __init__(self, midi_file):
        self.pattern = midi.read_midifile(midi_file)

    def perform_analysis(self):
        # check for unprocessed events
        for track in self.pattern:
            channel  = -1
            for event in track:
                if MidiUtils.is_channel_event(event):
                    if channel == -1:
                        channel = event.channel
                    if channel != event.channel:
                        print "TRACK HAS MULTIPLE CHANNELS"
                        # sys.exit(0)
                if not MidiUtils.is_event_processed(event):
                    print "EVENT NOT PROCESSED: ", event
                    # sys.exit(0)
        # global meta events should be in the first track
        for i in range(1, len(self.pattern), 1):
            for event in self.pattern[i]:
                if MidiUtils.is_global_meta_event(event):
                    print "GLOBAL META EVENTS NEED TO BE IN THE FIRST TRACK", event
                    # sys.exit(0)
