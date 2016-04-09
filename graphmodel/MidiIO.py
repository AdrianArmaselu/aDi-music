from midi import NoteOnEvent, NoteOffEvent
import midi

from graphmodel.Model import Note, OrganizedNotesTable, RunningNotesTable

__author__ = 'Adisor'


def is_meta_event(event):
    event_type = type(event)
    return event_type is not NoteOnEvent and event_type != NoteOffEvent


def has_note_ended(event):
    event_type = type(event)
    return event_type == NoteOffEvent or (event_type == NoteOnEvent and event.velocity == 0)


def is_new_note(event):
    event_type = type(event)
    return event_type == NoteOnEvent and event.velocity > 0


class MidiIO:
    def __init__(self, midi_file):
        self.data = midi.read_midifile(midi_file)
        self.table = OrganizedNotesTable()

        # 0 - single multi-channel track
        # 1 - one or more simultaneous tracks
        # 2 - one ore more sequential tracks
        self.format = self.data.format
        self.__build_table__()

    def __build_table__(self):
        running_notes = RunningNotesTable()
        timeline_tick = 0
        for track in self.data:
            timeline_tick = self.extract_track_notes(track, running_notes, timeline_tick)

    def extract_track_notes(self, track, running_notes, timeline_tick):
        for event in track:
            if is_meta_event(event):
                continue
            timeline_tick += event.tick
            if is_new_note(event):
                note = Note(timeline_tick, event.tick, 0, event.channel, event.pitch, event.velocity)
                running_notes.add(note)
            if has_note_ended(event):
                note = running_notes.get_note(event.channel, event.pitch)
                note.duration_ticks = timeline_tick - note.timeline_tick
                self.table.add(note)
        self.table.sort()
        self.table.update_delta_times()
        return timeline_tick

    def __str__(self):
        return str(self.data)
