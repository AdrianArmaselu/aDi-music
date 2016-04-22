from collections import defaultdict
import midi
import sys
import time
from graphmodel import MidiUtils
from graphmodel.Model import MetaContext, MusicTranscript, Note

__author__ = 'Adisor'


def next_note_starts_later(track, event_index):
    return (event_index + 1) > len(track) and track[event_index].tick != track[event_index + 1].tick


class ExperimentalReader2:
    def __init__(self, midifile):
        start = time.time()
        self.pattern = midi.read_midifile(midifile)
        end = time.time()
        print "Loaded Pattern ", end - start
        self.context_tracker = ContextTracker()
        self.transcript = MusicTranscript()

    def load(self):
        start = time.time()
        self.load_context()
        end = time.time()
        print "Loaded Context ", end - start
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
        start = time.time()
        track_loader = TrackLoader(self.context_tracker, self.transcript)
        track_loader.load_track(track)
        end = time.time()
        print "Loaded Track ", end - start


class TrackLoader:
    def __init__(self, context_tracker, transcript):
        self.context_tracker = context_tracker
        self.transcript = transcript
        self.time = 0
        self.current_context = MetaContext()
        self.on_notes = {}
        self.recent_off_notes = {}
        self.previous_note = None

    def load_track(self, track):
        is_first_note = True
        for event_index in range(0, len(track), 1):
            event = track[event_index]
            self.time += event.tick
            self.update_context(event)
            if MidiUtils.is_new_note(event):
                note = Note(self.time, 0, event, self.current_context)
                note.event_index = event_index
                self.on_notes[note.pitch] = note
                self.transcript.add_note(note)
                self.update_and_remove_recent_off_notes(event)
            if MidiUtils.has_note_ended(event):
                note = self.on_notes[event.pitch]
                note.duration = self.time - note.time
                if not is_first_note:
                    note.pause_to_previous_note = note.time - self.previous_note.time

                self.update_previous_note(track, event_index, note)
                self.recent_off_notes[note.pitch] = note
                is_first_note = True

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

    def update_previous_note(self, track, event_index, note):
        # if the next note starts later than the current node, update the previous note
        has_next = (note.event_index + 1) < len(track) - 1
        next_starts_later = track[event_index].tick != 0 and track[event_index + 1].tick != 0
        if has_next and next_starts_later:
            self.previous_note = note


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
        self.current_index = 0
        self.current = self.contexts[0]

    def get_context_at_time(self, time):
        if self.current.time < time:
            self.current_index += 1
            self.current = self.contexts[self.current_index]
        return self.current


start = time.time()
reader = ExperimentalReader2("music/bach.mid")
reader.load()
end = time.time()
print end - start
# print reader.pattern
print reader.transcript
