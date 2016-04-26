from collections import defaultdict
import midi

from graphmodel.utils import MidiUtils
from graphmodel.model.Meta import MetaContext
from graphmodel.model.Song import MusicTranscript, SoundEventsTimedTrack
from graphmodel.model.SongObjects import Note

__author__ = 'Adisor'


def get_transcript(midifile):
    loader = TranscriptLoader(midifile)
    loader.load()
    return loader.transcript


class TranscriptLoader:
    def __init__(self, midifile):
        self.pattern = midi.read_midifile(midifile)
        self.track_loader = None
        self.transcript = MusicTranscript()
        self.instrument_channel = {}

    def load(self):
        self.load_context()
        for track_index in range(1, len(self.pattern), 1):
            self.load_track(self.pattern[track_index])

    def load_context(self):
        context_tracker = ContextTracker()
        contexts = GlobalMetaContexts()
        time = 0
        for event in self.pattern[0]:
            time += event.tick
            contexts.add(time, event)
        context_tracker.set_contexts(contexts)
        self.track_loader = TrackLoader(context_tracker)

    def load_track(self, track):
        timed_track = self.track_loader.load_track(track)
        # check if the track actually has notes
        if len(timed_track):
            channel = self.track_loader.channel
            instrument = self.track_loader.program_change_event.data[0]
            # check if instrument already has a channel and place track in the same channel
            if instrument in self.instrument_channel:
                channel = self.instrument_channel[instrument]
            if instrument not in self.instrument_channel:
                self.instrument_channel[instrument] = channel
            self.transcript.add_track(channel, timed_track)
        self.track_loader.reset()


class TrackLoader:
    def __init__(self, context_tracker):
        self.context_tracker = context_tracker
        self.present_time = 0
        self.current_context = MetaContext()
        self.channel = 0
        self.program_change_event = None

    # TODO: SET CHANnEL ONCE
    def load_track(self, track):
        on_notes = {}
        timed_track = SoundEventsTimedTrack()
        for event_index in range(0, len(track), 1):
            event = track[event_index]
            self.present_time += event.tick
            self.update_context(event)
            if MidiUtils.is_program_change_event(event):
                self.program_change_event = event
            if MidiUtils.is_new_note(event):
                note = Note(self.present_time, 0, event, self.current_context)
                on_notes[note.pitch] = note
                timed_track.add_note(note)
                self.channel = event.channel
            if MidiUtils.has_note_ended(event):
                note = on_notes[event.pitch]
                note.duration = self.present_time - note.time
        return timed_track

    def update_context(self, event):
        global_context = self.context_tracker.get_context_at_time(self.present_time)
        self.current_context.update_from_context(global_context)
        if MidiUtils.is_music_control_event(event):
            self.current_context.update_from_event(event)

    def get_instrument(self):
        return self.program_change_event.data[0]

    def reset(self):
        self.present_time = 0
        self.current_context = MetaContext()
        self.channel = 0
        self.program_change_event = None


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
            channel = -1
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
