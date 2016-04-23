__author__ = 'Adisor'


class SoundEvent(object):
    """
    Stores a list of sorted notes by next_delta_ticks duration

    If the size of the list is greater than 1 - this object symbolizes a chord
    """

    def __init__(self, notes=None):
        self.time = 0
        if notes is None:
            notes = []
        else:
            self.time = notes[0].time
        # sorted by duration
        self.notes = notes
        # self.notes = notes
        self.hash = None
        self.isModified = True
        self.isSorted = False

    def get_time(self):
        if len(self.notes) == 0:
            return 0
        return self.notes[0].time

    def add_note(self, note):
        self.notes.append(note)
        self.isModified = True

    def get_channel(self):
        return self.notes[0].channel

    def first(self):
        return self.notes[0]

    def shortest_note(self):
        return self.notes[0]

    # TODO: CHECK THIS LATER
    def get_smallest_duration(self):
        self._sort_notes_if_not_sorted()
        min_ticks = None
        for note in self.notes:
            if min_ticks is None or note.pause_to_next_note < min_ticks:
                min_ticks = note.duration_ticks
        return min_ticks

    def _sort_notes_if_not_sorted(self):
        if not self.isSorted:
            self.notes = sorted(self.notes, key=lambda note: note.pause_to_next_note)
            self.isSorted = True

    def __hash__(self):
        if not self.hash or self.isModified:
            self._sort_notes_if_not_sorted()
            notes_tuple = ()
            for note in self.notes:
                notes_tuple += (note,)
            self.hash = (hash(notes_tuple) << 4) | len(notes_tuple)
        return self.hash

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __str__(self):
        string = "SoundEvent: "
        for note in self.notes:
            string += str(note) + " "
        return string


class Note(object):
    """
    The class that represents a musical note. Contains all the necessary data.
    """
    SHOW_CONTEXT_INFO = False

    def __init__(self, time, duration_ticks, event, meta_context=None):
        # timestamp from original song - used purely for debugging purposes
        self.time = time

        # how long to play this note (not how many ticks until next note)
        self.duration_ticks = duration_ticks

        # ticks from last sound event
        self.pause_to_previous_note = 0

        # ticks to next sound event
        self.pause_to_next_note = 0
        self.channel = event.channel
        self.pitch = event.pitch
        self.velocity = event.velocity

        self.meta_context = meta_context
        self.hash = None

    # ticks | channel | pitch | velocity
    # bytes: 12 | 5 | 7 | 8
    def encode(self):
        return (self.duration_ticks << 20) | (self.channel << 15) | (self.pitch << 8) | self.velocity
        # return (self.ticks << 20) | (self.channel << 15) | (self.pitch << 8)
        # return (self.ticks << 20) | (self.channel << 15)

    def __hash__(self):
        if not self.hash:
            self.hash = self.encode()
        return self.hash

    def __eq__(self, other):
        # return self.__hash__() == other.__hash__ and abs(self.pitch - other.pitch) < 10
        return self.encode() == other.encode()

    def __str__(self):
        string = (
            "Note(timeline:%d, t:%d, "
            "dt-:%d, dt+:%d, "
            "ch:%d, pitch:%d, vol:%d" %
            (self.time, self.duration_ticks,
             self.pause_to_previous_note, self.pause_to_next_note,
             self.channel, self.pitch, self.velocity))
        if self.SHOW_CONTEXT_INFO:
            string += (" meta_context: %s" % self.meta_context)
        string += ")"
        return string


def is_chord(sound_event):
    return is_chord(sound_event.notes)


def is_chord(notes):
    return len(notes) > 0
