from collections import OrderedDict
from midi import NoteOnEvent, NoteOffEvent
from midi.events import EndOfTrackEvent, TimeSignatureEvent, SetTempoEvent, KeySignatureEvent, ControlChangeEvent, \
    PortEvent, ProgramChangeEvent
import midi

from Model import Note, OrganizedNotesTable, NotesTable

__author__ = 'Adisor'

music_control_events = [TimeSignatureEvent, SetTempoEvent, KeySignatureEvent, ControlChangeEvent, PortEvent,
                        ProgramChangeEvent]
"""
Consider: Polyphonic Aftertouch, Channel Aftertouch - how much a key is pressed more - for now we can ignore
Port Events can be ignored
Control Change and aftertouch - modulation and pitch bend
check MIT music21
"""


def get_event_type(event):
    return type(event)


def is_meta_event(event):
    event_type = get_event_type(event)
    return event_type is not NoteOnEvent and event_type != NoteOffEvent


def is_music_control_event(event):
    """
    Checks to see if the event is an event that sets music control - meaning tempo, key signature etc.
    Object event must be one of the following:  TimeSignatureEvent, SetTempoEvent, KeySignatureEvent,
    ControlChangeEvent, PortEvent, ProgramChangeEvent
    """
    event_type = get_event_type(event)
    boolean = False
    for control_event in music_control_events:
        boolean = boolean or event_type is control_event
    return boolean


def has_note_ended(event):
    event_type = get_event_type(event)
    return event_type == NoteOffEvent or (event_type == NoteOnEvent and event.velocity == 0)


def is_new_note(event):
    event_type = get_event_type(event)
    return event_type == NoteOnEvent and event.velocity > 0


class MidiIO:
    """
    Used to read the notes from the midi file

    The midi file can come in multiple formats as follows:
    0 - single multi-channel track
    1 - one or more simultaneous tracks
    2 - one ore more sequential tracks
    """

    def __init__(self, midi_file):
        self.pattern = midi.read_midifile(midi_file)
        self.table = OrganizedNotesTable()
        self.format = self.pattern.format
        self.build_table()

    def build_table(self):
        running_notes = RunningNotesTable()
        timeline_tick = 0
        for track in self.pattern:
            timeline_tick = self.extract_track_data(track, running_notes, timeline_tick)

    def extract_track_data(self, track, running_notes, timeline_tick):
        for event in track:
            # if is_meta_event(event) and is_music_control_event(event):

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
        return "File Loaded:\n" + str(self.pattern) + "\n"


class RunningNotesTable(NotesTable):
    """
    Used during the reading of file pattern for keeping track of notes whose durations have not been computed

    This class uses a table for storing the notes. The row is the pitch and the column is the channel
    You can never have two notes with the same pitch running at the same time
    """

    def add(self, note):
        # Add the note to a cell located by the note's pitch and channel
        pitch = note.pitch
        channel = note.channel
        if pitch not in self.table:
            self.table[pitch] = {}
        self.table[pitch][channel] = note

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
        self.scheduled_sequence[start].append(note_on_event(note))
        self.scheduled_sequence[start + note.duration_ticks].append(note_off_event(note))


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
        self.pattern.append(track)


def note_on_event(note):
    return midi.NoteOnEvent(channel=note.channel, tick=0, pitch=note.pitch,
                            velocity=note.velocity)


def note_off_event(note):
    return midi.NoteOffEvent(channel=note.channel, tick=0, pitch=note.pitch,
                            velocity=0)
