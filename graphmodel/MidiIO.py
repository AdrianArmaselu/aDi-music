from collections import OrderedDict

from midi import NoteOnEvent, NoteOffEvent
import midi

from graphmodel.Objects import Note

__author__ = 'Adisor'


def is_meta_event(event):
    event_type = type(event)
    return event_type is not NoteOnEvent and event_type != NoteOffEvent


def has_note_ended(event):
    event_type = type(event)
    return event_type == NoteOffEvent or (event_type == NoteOnEvent and event.velocity == 0)


def is_new_note(event):
    event_type = type(event)
    return event_type == NoteOnEvent


class MidiIO:
    def __init__(self, midi_file):
        self.midi_file = midi.read_midifile(midi_file)
        self.mappings = {}
        self.build_note_mappings()

    def build_note_mappings(self):
        running_events = {}
        cumulative_tick = 0
        for track in self.midi_file:
            for event in track:
                if is_meta_event(event):
                    continue
                cumulative_tick += event.tick
                if has_note_ended(event):
                    self.map_sound_event(event, running_events, cumulative_tick)
                if is_new_note(event):
                    if event.channel not in running_events:
                        running_events[event.pitch] = {}
                    running_events[event.pitch][event.channel] = (cumulative_tick, event.tick, event)

        # sort by first key, the starting tick
        self.mappings = OrderedDict(sorted(self.mappings.items(), key=lambda key: key[0]))

    def map_sound_event(self, ended_event, running_events, cumulative_tick):
        (timeline_tick, wait_ticks, ended_event) = running_events[ended_event.pitch][ended_event.channel]
        del running_events[ended_event.pitch][ended_event.channel]
        ticks = cumulative_tick - timeline_tick
        new_note = Note(timeline_tick, wait_ticks, ticks, ended_event.channel, ended_event.pitch, ended_event.velocity)
        start_tick = new_note.start_tick
        channel = new_note.channel
        if start_tick not in self.mappings:
            self.mappings[start_tick] = {}
        if new_note.channel not in self.mappings[start_tick]:
            self.mappings[start_tick][channel] = []
        self.mappings[start_tick][channel].append(new_note)

    def print_events(self):
        print self.midi_file

    def print_mappings(self):
        for tick in self.mappings:
            for channel in self.mappings[tick]:
                if len(self.mappings[tick][channel]) > 1:
                    print "CHORD:"
                else:
                    print "NOTE:"
                for note in self.mappings[tick][channel]:
                    print note
