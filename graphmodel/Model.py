from collections import OrderedDict

__author__ = 'Adisor'


def is_chord(sound_event):
    return is_chord(sound_event.notes)


def is_chord(notes):
    return len(notes) > 0


class Note(object):
    def __init__(self, timeline_tick, wait_ticks, duration_ticks, channel, pitch, velocity):
        # timestamp
        self.timeline_tick = timeline_tick
        # ticks before playing this note
        self.wait_ticks = wait_ticks
        # how long to play this note (not how many ticks until next note)
        self.duration_ticks = duration_ticks
        self.channel = channel
        self.pitch = pitch
        self.velocity = velocity
        self.context = []

    # ticks | channel | pitch | velocity
    # bytes: 12 | 5 | 7 | 8
    def encode(self):
        return (self.duration_ticks << 20) | (self.channel << 15) | (self.pitch << 8) | self.velocity
        # return (self.ticks << 20) | (self.channel << 15) | (self.pitch << 8)
        # return (self.ticks << 20) | (self.channel << 15)

    def __hash__(self):
        return self.encode()

    def __eq__(self, other):
        # return self.__hash__() == other.__hash__ and abs(self.pitch - other.pitch) < 10
        return self.encode() == other.encode()

    def __str__(self):
        return ("Note(start_tick:%d, wait_ticks:%d, ticks:%d, channel:%d, pitch:%d, velocity:%d)" %
                (self.timeline_tick, self.wait_ticks, self.duration_ticks, self.channel, self.pitch, self.velocity))


class NotesTable(object):
    def __init__(self):
        self.table = {}
        self.channels = []

    def add(self, note):
        self.table[note.timeline_tick] = note

    def add_channel_if_not_exists(self, channel):
        if not self.has_channel(channel):
            self.add_channel(channel)

    def has_channel(self, channel):
        return channel in self.channels

    def add_channel(self, channel):
        self.channels.append(channel)


class OrganizedNotesTable(NotesTable):
    def __init__(self):
        super(OrganizedNotesTable, self).__init__()
        # this encodes channels as follows: if the nth bit is on, it means channel n contains notes
        self.channel_coding = 0 << 16

    def add(self, note):
        tick = note.timeline_tick
        channel = note.channel
        pitch = note.pitch
        self.add_channel_if_not_exists(channel)
        if tick not in self.table:
            self.table[tick] = {}
        if channel not in self.table[tick]:
            self.table[tick][channel] = {}
        self.table[tick][channel][pitch] = note

    def has_channel(self, channel):
        return self.channel_coding & (1 << channel)

    def add_channel(self, channel):
        super(OrganizedNotesTable, self).add_channel(channel)
        self.channel_coding |= 1 << channel

    def get_note(self, tick, channel, pitch):
        return self.table[tick][channel][pitch]

    # sort by timeline_tick
    def sort(self):
        self.table = OrderedDict(sorted(self.table.items(), key=lambda key: key[0]))

    def __str__(self):
        string = ""
        for tick in self.table:
            for channel in self.table[tick]:
                if len(self.table[tick][channel]) > 1:
                    string += "CHORD:\n"
                else:
                    string += "NOTE:\n"
                for pitch in self.table[tick][channel]:
                    string += str(self.table[tick][channel][pitch]) + "\n"
        return string


class RunningNotesTable(NotesTable):
    def add(self, note):
        pitch = note.pitch
        channel = note.channel
        if pitch not in self.table:
            self.table[pitch] = {}
        self.table[pitch][channel] = note

    def get_note(self, channel, pitch):
        return self.table[pitch][channel]


# Dictionary of tracks. Each track contains consecutive sound events
class MusicalTranscript(object):
    def __init__(self, notes_table):
        self.notes_table = notes_table
        self.tracks = {}
        self.__build__()

    def __build__(self):
        for channel in self.notes_table.channels:
            self.tracks[channel] = []
        for tick in self.notes_table.table:
            for channel in self.notes_table[tick]:
                notes = []
                for pitch in self.notes_table[tick][channel]:
                    notes.append(self.notes_table[tick][channel][pitch])
                sound_event = SoundEvent(notes)
                self.tracks[channel].append(sound_event)

    def get_sound_events(self, channel):
        return self.tracks[channel]


# List of consecutive frames - consecutive from the point of view of the first note of every frame
class OrderedFrames(object):
    def __init__(self, frame_size):
        self.frame_size = frame_size
        self.frames = []

    def add(self, sound_event):
        frame = Frame(self.frame_size)
        self.frames.append(frame)
        for frame in self.frames:
            frame.add(sound_event)

    def remove_first(self):
        frame = self.frames[0]
        del self.frames[0]
        return frame

    def is_first_frame_full(self):
        return self.frames[0].is_full

    def __sizeof__(self):
        return len(self.frames)


# Tuple of Sound Events
class Frame(object):
    def __init__(self, max_size):
        self.max_size = max_size
        self.sound_events = ()

    def add(self, sound_event):
        self.sound_events += (sound_event,)

    def is_full(self):
        return self.__sizeof__() == self.max_size

    def first(self):
        return self.sound_events[0]

    def last(self):
        return self.sound_events[-1]

    def __sizeof__(self):
        return len(self.sound_events)

    def __hash__(self):
        return hash(self.sound_events)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__


# List of notes
# The size of the list indicates whether this is a chord or not ( n > 1 means chord, otherwise note)
class SoundEvent(object):
    def __init__(self, notes):
        self.notes = notes

    def __hash__(self):
        return (hash(self.notes[0]) << 4) | len(self.notes)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __str__(self):
        string = "("
        for note in self.notes:
            string += str(note) + ", "
        return string + ")"
