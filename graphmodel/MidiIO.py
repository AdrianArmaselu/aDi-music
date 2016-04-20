from collections import OrderedDict
import sys

import midi

from Model import Note, OrganizedNotesTable, NotesTable, MetaContext
from graphmodel import MidiUtils

__author__ = 'Adisor'


# TODO: JUST GET TRANSCRIPT INSTEAD OF TABLE, MUCH SIMPLER
class MidiIO:
    """
    Used to read the notes from the midi file

    Each midi track read from file has to have 1-to-1 mapping with the notes channel.
    Any midi track that violates the above rule must be pre-processed.

    The midi file can come in multiple formats as follows:
    0 - single multi-channel track
    1 - one or more simultaneous tracks
    2 - one ore more sequential tracks
    """

    def __init__(self, midi_file):
        analyzer = Analyzer(midi_file)
        analyzer.perform_analysis()
        self.pattern = midi.read_midifile(midi_file)
        self.notes_table = OrganizedNotesTable()
        self.format = self.pattern.format
        self.build_notes_table()

    def build_notes_table(self):
        helper_table = RunningNotesTable()
        self.extract_global_meta_events(helper_table)
        for i in range(1, len(self.pattern), 1):
            self.extract_track_data(self.pattern[i], helper_table)

    def extract_global_meta_events(self, helper_table):
        timeline_tick = 0
        for event in self.pattern[0]:
            timeline_tick += event.tick
            if MidiUtils.is_global_meta_event(event):
                helper_table.add_global_meta_event(timeline_tick, event)
        helper_table.sort_global_context()

    def extract_track_data(self, track, helper_table):
        timeline_tick = 0
        for event in track:
            timeline_tick += event.tick
            if MidiUtils.is_track_meta_event(event):
                helper_table.add_track_meta_event(timeline_tick, event)
            if MidiUtils.is_meta_event(event):
                continue
            helper_table.update_current_context(timeline_tick)
            if MidiUtils.is_new_note(event):
                note = Note(timeline_tick, 0, event.channel, event.pitch, event.velocity,
                            helper_table.get_current_context().copy())
                helper_table.add(note)
            if MidiUtils.has_note_ended(event):
                note = helper_table.get_note(event.channel, event.pitch)
                note.duration_ticks = timeline_tick - note.timeline_tick
                self.notes_table.add(note)
        self.notes_table.sort()
        self.notes_table.update_delta_times()
        return timeline_tick

    def __str__(self):
        return "File Loaded:\n" + str(self.pattern) + "\n"


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
                if MidiUtils.is_event(event):
                    if channel == -1:
                        channel = event.channel
                    if channel != event.channel:
                        print "TRACK HAS MULTIPLE CHANNELS"
                        sys.exit(0)
                if not MidiUtils.is_event_processed(event):
                    print "EVENT NOT PROCESSED: ", event
                    sys.exit(0)
        # global meta events should be in the first track
        for i in range(1, len(self.pattern), 1):
            for event in self.pattern[i]:
                if MidiUtils.is_global_meta_event(event):
                    print "GLOBAL META EVENTS NEED TO BE IN THE FIRST TRACK", event
                    sys.exit(0)


class RunningNotesTable(NotesTable):
    """
    Used during the reading of file pattern for keeping track of notes whose durations have not been computed

    This class uses a table for storing the notes. The row is the pitch and the column is the channel
    You can never have two notes with the same pitch running at the same time
    """

    def __init__(self):
        super(RunningNotesTable, self).__init__()
        self.global_context_map = {}
        self.global_index = 0
        self.current_context = MetaContext()

    def add(self, note):
        # Add the note to a cell located by the note's pitch and channel
        pitch = note.pitch
        channel = note.channel
        if pitch not in self.table:
            self.table[pitch] = {}
        self.table[pitch][channel] = note

    def add_global_meta_event(self, timeline, global_meta_event):
        self.current_context.update(global_meta_event)

        if timeline not in self.global_context_map:
            self.global_context_map[timeline] = self.current_context.copy()

    def sort_global_context(self):
        self.global_context_map = OrderedDict(sorted(self.global_context_map.items()))

    def add_track_meta_event(self, timeline, meta_event):
        self.update_current_context(timeline)
        self.current_context.update(meta_event)

    def update_current_context(self, timeline):
        """
        Move the global context timeline to the newest context
        """
        global_timeline = self.get_global_timeline()
        while global_timeline <= timeline and self.global_index < len(self.global_context_map.keys()) - 1:
            self.global_index += 1
            global_timeline = self.get_global_timeline()
            self.current_context.update_global_context(self.global_context_map[global_timeline])

    def get_global_timeline(self):
        return self.global_context_map.keys()[self.global_index]

    def get_current_context(self):
        return self.current_context

    def get_note(self, channel, pitch):
        return self.table[pitch][channel]
