from collections import OrderedDict
import sys
from collections import defaultdict
import midi

from Model import Note, OrganizedNotesTable, NotesTable, MetaContext, MusicTranscript, SoundEvent
from graphmodel import MidiUtils

__author__ = 'Adisor'


# def read_transcript(midi_file):
#     io = MidiIO(midi_file)
#     transcript = MusicTranscript()
# transcript.add_tracks()

# TODO: CAPTURE SOUND EVENTS THAT ARE PARALLEL OVER MULTIPLE CHANNELS/TRACKS FOR BETTER REPRODUCTION
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
                note = Note(timeline_tick, 0, event, helper_table.get_context_at_time().copy())
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
                if MidiUtils.is_channel_event(event):
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
        self.current_context.update_from_event(global_meta_event)

        if timeline not in self.global_context_map:
            self.global_context_map[timeline] = self.current_context.copy()

    def sort_global_context(self):
        self.global_context_map = OrderedDict(sorted(self.global_context_map.items()))

    def add_track_meta_event(self, timeline, meta_event):
        self.update_current_context(timeline)
        self.current_context.update_from_event(meta_event)

    def update_current_context(self, timeline):
        """
        Move the global context timeline to the newest context
        """
        global_timeline = self.get_global_timeline()
        while global_timeline <= timeline and self.global_index < len(self.global_context_map.keys()) - 1:
            self.global_index += 1
            global_timeline = self.get_global_timeline()
            self.current_context.update_from_context(self.global_context_map[global_timeline])

    def get_global_timeline(self):
        return self.global_context_map.keys()[self.global_index]

    def get_current_context(self):
        return self.current_context

    def get_note(self, channel, pitch):
        return self.table[pitch][channel]


class PreProcessor:
    def __init__(self):
        self.timelines = PatternTimelines()
        self.primary_channel = defaultdict(lambda: None)
        self.primary_track_index = defaultdict(lambda: None)
        self.flagged_track_indexes = []

    def schedule_tracks(self, pattern):
        for track_index in range(0, len(pattern), 1):
            time = 0
            for event_index in pattern[track_index]:
                current_event = pattern[track_index][event_index]
                time += current_event.tick

                if MidiUtils.is_channel_event(current_event):
                    channel = current_event.channel
                    # set primary channel of this track
                    if self.primary_channel[track_index] is None:
                        self.primary_channel[track_index] = channel
                        self.primary_track_index[channel] = track_index
                    # flag track if different than the primary track of this channel
                    if self.primary_track_index[channel] != track_index:
                        self.flagged_track_indexes.append(pattern)

                # time table
                self.timelines.set_event_index(track_index, time, event_index)

        # reschedule events in target tracks
        for flagged_track_index in self.flagged_track_indexes:
            target_channel = self.primary_channel[flagged_track_index]
            target_track_index = self.primary_track_index[target_channel]
            target_track = pattern[target_track_index]
            current_track_time = 0
            target_time_index = 0
            target_track_time = self.timelines.get_track_time(target_track_index, target_time_index)

            # reschedule event in the target track
            for current_event in pattern[flagged_track_index]:
                """
                update current track time
                update track time of target track
                place event from current track into target track
                update adjacent ticks
                update indexes
                """
                current_track_time += current_event.tick

                # update the time so we can place events in this track into the target track
                if target_track_time < current_track_time:
                    target_track_time = self.timelines.get_track_time(target_track_index, target_time_index)
                    target_time_index += 1

                target_event_index = self.timelines.get_event_index(target_track_index, target_time_index)
                target_event = pattern[target_track_index][target_event_index]
                # place event in target track
                pattern[target_track_index].insert(target_event_index - 1, current_event)
                # update event ticks
                target_previous_track_time = self.timelines.get_track_time(target_track_index, target_time_index - 1)
                current_event.tick = current_track_time - target_previous_track_time
                target_event.tick = target_track_time - current_track_time

                # update timings and indexes
                self.timelines.set_event_index(target_track_index, current_track_time, target_event_index - 1)


class PatternTimelines:
    def __init__(self):
        self.timeline = defaultdict(Timeline)

    def set_event_index(self, track_index, time, event_index):
        self.timeline[track_index].set_value(time, event_index)

    def get_track_time(self, track_index, time_index):
        return self.timeline[track_index].get_time(time_index)

    def get_event_index(self, track_index, time):
        return self.timeline[track_index].get_value[time]


class Timeline:
    def __init__(self):
        self.timeline = defaultdict(lambda: None)

    def set_value(self, time, value):
        self.timeline[time] = value

    def get_value(self, time):
        return self.timeline[time]

    def get_time(self, time_index):
        return self.timeline.keys()[time_index]


class ExperimentalReader:
    def __init__(self, midi_file):
        analyzer = Analyzer(midi_file)
        analyzer.perform_analysis()
        self.pattern = midi.read_midifile(midi_file)
        self.meta_context = TrackMetaContext(self.pattern)
        self.transcript = MusicTranscript()
        self.tracker = NotesTracker()

    def load(self):
        """
        Constructs a music transcript from the file midi data
        :return:
        """
        is_finished = False
        # track timelines
        track_timeline = defaultdict(int)
        # track indexes
        event_indexes = defaultdict(int)

        while not is_finished:
            end_of_any_track = True
            for track_index in range(0, len(self.pattern), 1):

                event_index = event_indexes[track_index]
                current_track = self.pattern[track_index]
                # did we reach the end of all tracks?
                if event_index > len(current_track) - 1:
                    continue

                event = current_track[event_index]
                current_time = track_timeline[track_index] + event.tick
                track_timeline[track_index] = current_time
                context = self.meta_context.get_current_context(current_time, track_index, event)
                if MidiUtils.is_new_note(event):
                    event_indexes[track_index] = self.extract_notes_and_get_index(track_index, event_index,
                                                                                  current_time, context)
                    self.update_most_recent_notes(track_index, current_time)
                    continue

                if MidiUtils.has_note_ended(event):
                    note = self.tracker.get_on_note(event.channel, event.pitch)
                    self.update_and_track_off_note(note, current_time, track_index)
                event_indexes[track_index] += 1
                end_of_any_track = end_of_any_track and False
            is_finished = end_of_any_track

    def extract_notes_and_get_index(self, track_index, event_index, tick, context):
        track = self.pattern[track_index]

        # create node and track it
        note = Note(tick, 0, track[event_index], context.copy())
        self.update_and_track_on_note(note, track_index, tick)

        # create a tuple of notes
        notes = (note,)
        next_event_index = event_index + 1

        # loops through all notes that are part of the chord and adds them to a tuple
        while has_chord_notes(track, next_event_index):
            next_event = track[next_event_index]
            note = Note(tick, 0, next_event, context.copy())
            self.update_and_track_on_note(note, track_index, tick)
            notes += (note,)
            next_event_index += 1

        # create a sound event from the extracted notes
        sound_event = SoundEvent(notes)
        self.transcript.add_sound_event(sound_event)

        # return the index of the next unprocessed event
        return next_event_index

    def update_and_track_on_note(self, note, track_index, tick):
        # if this is the first note, the pause from last note is 0
        if self.tracker.get_last_note_end_time(track_index) != 0:
            note.pause_to_previous_note = tick - self.tracker.get_last_note_end_time(track_index)
        self.tracker.add_to_on_notes(note)
        self.tracker.set_note_start_time(note, tick)
        return note

    def update_most_recent_notes(self, track_index, current_time):
        for past_note in self.tracker.get_off_notes(track_index):
            past_note.pause_to_next_note = current_time - self.tracker.get_note_end_time(past_note)
            self.tracker.remove_from_off_notes(track_index, past_note)

    def update_and_track_off_note(self, note, current_time, track_index):
        note.duration_ticks = current_time - self.tracker.get_note_start_time(note)
        self.tracker.set_note_end_time(note, current_time)
        self.tracker.set_last_note_end_time(track_index, current_time)
        self.tracker.add_to_off_notes(track_index, note)


def has_chord_notes(track, index):
    return index < len(track) - 1 and MidiUtils.is_new_note(track[index]) and track[index].tick == 0


class NotesTracker:
    def __init__(self):
        self.on_notes = defaultdict(lambda: {})
        self.note_start_time = defaultdict(int)
        self.note_end_time = defaultdict(int)
        self.last_note_end_time = defaultdict(int)
        self.off_notes = defaultdict(lambda: [])

    def set_note_start_time(self, note, time):
        self.note_start_time[note] = time

    def set_note_end_time(self, note, time):
        self.note_end_time[note] = time

    def set_last_note_end_time(self, track_index, time):
        self.last_note_end_time[track_index] = time

    def get_last_note_end_time(self, track_index):
        return self.last_note_end_time[track_index]

    def get_on_note(self, channel, pitch):
        return self.on_notes[channel][pitch]

    def get_off_notes(self, track_index):
        return self.off_notes[track_index]

    def get_note_start_time(self, note):
        return self.note_start_time[note]

    def get_note_end_time(self, note):
        return self.note_end_time[note]

    def add_to_off_notes(self, track_index, note):
        self.off_notes[track_index].append(note)

    def remove_from_off_notes(self, track_index, note):
        self.off_notes[track_index].remove(note)

    def add_to_on_notes(self, note):
        self.on_notes[note.channel][note.pitch] = note


class GlobalMetaContextTable:
    def __init__(self, global_track):
        self.context = {}
        time = 0
        for event in global_track:
            time += event.tick
            context = MetaContext()
            context.update_from_event(event)
            self.context[time] = context

    def get_time(self, index):
        return self.context.keys()[index]

    def get_context_from_index(self, index):
        return self.context[self.get_time(index)]

    def __len__(self):
        return len(self.context)


class TrackMetaContext:
    def __init__(self, tracks):
        self.context = {}
        self.global_context_table = GlobalMetaContextTable(tracks[0])
        # used for updating track context from global context
        self.global_context_index = {}
        for track_index in range(0, len(tracks), 1):
            self.context[track_index] = MetaContext()
            self.global_context_index[track_index] = 0

    def get_current_context(self, track_tick, track_index, event):
        index = self.update_global_context_index(track_tick, track_index)
        global_context = self.global_context_table.get_context_from_index(index)
        track_context = self.context[track_index]
        track_context.update_from_context(global_context)
        track_context.update_from_event(event)
        return track_context

    def update_global_context_index(self, track_time, track_index):
        index = self.global_context_index[track_index]
        global_time = self.global_context_table.get_time(index)
        while global_time < track_time and index < len(self.global_context_table) - 1:
            index += 1
            global_time = self.global_context_table.get_time(index)
        self.global_context_index[track_index] = index
        return index

# midi_file = "music/cosifn2t.mid"
# midi_file = "music/bach.mid"
# experimentalReader = ExperimentalReader(midi_file)
# print experimentalReader.pattern
# experimentalReader.load()
# transcript = experimentalReader.transcript
# print transcript


