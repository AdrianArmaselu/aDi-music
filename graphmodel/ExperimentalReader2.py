from collections import defaultdict
from graphmodel import MidiUtils
from graphmodel.Model import MetaContext, MusicTranscript

__author__ = 'Adisor'


class ExperimentalReader2:
    def __init__(self, pattern):
        self.pattern = pattern
        self.context_tracker = ContextTracker()
        self.transcript = MusicTranscript()

    def load(self):
        self.load_context()
        for track in self.pattern:
            self.load_track(track)

    def load_context(self):
        contexts = GlobalMetaContexts()
        # global meta context
        time = 0
        for event in self.pattern[0]:
            time += event.tick
            contexts.add(time, event)

    def load_track(self, track):
        time = 0
        for event in track:
            time += event.tick
            global_context = self.context_tracker.get_context_at_time(time)
            if MidiUtils.is_music_control_event(event):
                current_context = global_context.copy().update_from_event(event)


class GlobalMetaContexts:
    def __init__(self):
        self.context = []

    def add(self, time, event):
        current_context = self.get_previous_if_exists()
        current_context.update_from_event(event)
        current_context.time = time
        self.context.append(current_context)

    def get_previous_if_exists(self):
        previous_index = len(self.context) - 1
        context = MetaContext()
        if previous_index >= 0:
            previous_context = self.context[previous_index]
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
