from collections import OrderedDict
import sys

from midi.events import EndOfTrackEvent
import midi

from Model import Note, OrganizedNotesTable, NotesTable, MetaContext
from graphmodel import MidiUtils

__author__ = 'Adisor'


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
                            helper_table.get_current_context())
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
            self.current_context.update(self.global_context_map[global_timeline])

    def get_global_timeline(self):
        # print str(len(self.context_map.keys())), str(self.current_context_index)
        return self.global_context_map.keys()[self.global_index]

    def get_current_context(self):
        return self.current_context

    def get_note(self, channel, pitch):
        return self.table[pitch][channel]


def to_midi_pattern(sequence):
    scheduler = Scheduler(sequence)
    scheduler.schedule()
    converter = MidiConverter(scheduler.scheduled_sequence)
    converter.convert()
    return converter.pattern


# TODO: HANDLE MULTIPLE CHANNELS INTO MULTIPLE TRACKS
class Scheduler:
    """
    Uses a sequence of SoundEvent objects to schedule them in a timeline of ticks

    The algorithm works as follows:
    1. Initialize the "start" variable to 0. It will be used to keep track when the next SoundEvent object starts
    2. Loop through each SoundEvent object s of sequence seq
    3. Loop through each note n of s
    4. Schedule when n starts playing based on the start variable.
    5. Schedule when n stops playing based on the start variable + duration_ticks of the note
    6. End loop of s
    7. Update the start variable by the duration of the shortest note of s
    """

    def __init__(self, sequence):
        self.sequence = sequence
        self.scheduled_sequence = {}

    def schedule(self):
        start = 0
        for sound_event in self.sequence:
            for note in sound_event.notes:
                self.schedule_note(note, start)
            start += sound_event.shortest_note().next_delta_ticks
        self.scheduled_sequence = OrderedDict(sorted(self.scheduled_sequence.items(), key=lambda key: key[0]))

    def schedule_note(self, note, start):
        if start not in self.scheduled_sequence:
            self.scheduled_sequence[start] = []
        if start + note.duration_ticks not in self.scheduled_sequence:
            self.scheduled_sequence[start + note.duration_ticks] = []
        self.scheduled_sequence[start].append(MidiUtils.note_on_event(note))
        self.scheduled_sequence[start + note.duration_ticks].append(MidiUtils.note_off_event(note))


# TODO: HANDLE MULTIPLE CHANNELS INTO MULTIPLE TRACKS
class MidiConverter:
    """
    Converts a scheduled sequence of notes into a midi pattern object
    """

    def __init__(self, scheduled_sequence):
        self.scheduled_sequence = scheduled_sequence
        self.pattern = midi.Pattern()
        self.convert()

    def convert(self):
        """
        Loops through each event and updates its tick based on delta ticks.
        Delta ticks are also called times between events (start of an event or its end)

        After updating the event, it adds it to a track, then the track is added to the midi pattern
        """
        track = midi.Track()
        last_tick = 0
        for tick in self.scheduled_sequence:
            for note_on_event in self.scheduled_sequence[tick]:
                note_on_event.tick = tick - last_tick
                last_tick = tick
                track.append(note_on_event)
        track.append(EndOfTrackEvent(tick=1))
        self.pattern = midi.Pattern([track])
