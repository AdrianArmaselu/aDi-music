from collections import defaultdict
from midi import events
from graphmodel.utils import MidiUtils

__author__ = 'Adisor'


class MetaContext:
    def __init__(self):
        self.meta_events_dict = defaultdict(lambda: None)
        self.meta_events_dict[events.ControlChangeEvent] = ControlChangeEvents()

    def copy(self):
        meta_context = MetaContext()
        for event_type in self.meta_events_dict:
            meta_context.meta_events_dict[event_type] = self.meta_events_dict[event_type].copy()
        return meta_context

    def update_from_event(self, event):
        if not MidiUtils.is_music_control_event(event):
            return
        event_type = type(event)
        if self.meta_events_dict[event_type] is None:
            self.meta_events_dict[event_type] = MetaEventWrapper()
        self.meta_events_dict[event_type].add_event(event)

    def update_from_context(self, context):
        for key in context.meta_events_dict.keys():
            self.meta_events_dict[key] = context.meta_events_dict[key].copy()

    # if both events are none, there is no change
    def get_changed_events_from(self, meta_context):
        changed_events = []
        for key in meta_context.meta_events_dict.keys():
            wrapper1 = self.meta_events_dict[key]
            wrapper2 = meta_context.meta_events_dict[key]
            if wrapper2 is not None and (wrapper1 is None or wrapper1 != wrapper2):
                changed_events += meta_context.meta_events_dict[key].get_events()
        return changed_events

    def __str__(self):
        string = ""
        for value in self.meta_events_dict.values():
            string += str(value) + " "
        return string


class MetaEventWrapper:
    def __init__(self):
        self.event = None
        pass

    def add_event(self, event):
        self.event = event

    def copy(self):
        copy = MetaEventWrapper()
        copy.event = self.event
        return copy

    def get_events(self):
        return [self.event]

    def __str__(self):
        return str(self.event)

    def __ne__(self, other):
        if other is None:
            return True
        return self.event.data != other.event.data


class ControlChangeEvents(MetaEventWrapper):
    def __init__(self):
        MetaEventWrapper.__init__(self)
        self.events = {}

    def add_event(self, event):
        self.events[event.data[0]] = event

    def copy(self):
        copy = ControlChangeEvents()
        for key in self.events.keys():
            copy.events[key] = self.events[key]
        return copy

    def get_events(self):
        return self.events.values()

    def __ne__(self, other):
        if len(self.events) != len(other.events):
            return True
        for key_index in range(0, len(self.events.keys()), 1):
            key1 = self.events.keys()[key_index]
            key2 = other.events.keys()[key_index]
            if key1 != key2 or self.events[key1] != self.events[key2]:
                return True
        return False

    def __str__(self):
        return str(self.events.values())
