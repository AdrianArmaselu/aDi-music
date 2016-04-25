__author__ = 'Adisor'


class SoundEvent(object):
    """
    If the size of the list is greater than 1 - this object symbolizes a chord
    """

    def __init__(self):
        self.notes = []
        self.hash = None

    def get_time(self):
        if len(self.notes) == 0:
            return 0
        return self.notes[0].time

    def add_note(self, note):
        self.notes.append(note)
        self.hash = None

    def get_shortest_pause_to_next_note(self):
        min_pause = self.notes[0].pause_to_next_note
        for i in range(1, len(self.notes), 1):
            if min_pause > self.notes[i].pause_to_next_note:
                min_pause = self.notes[i].pause_to_next_note
        return min_pause

    def get_channel(self):
        return self.notes[0].channel

    def first(self):
        return self.notes[0]

    def get_notes(self):
        return self.notes

    def update_pause_to_next_note(self, pause):
        for note in self.notes:
            note.pause_to_next_note = pause

    def update_pause_to_previous_note(self, pause):
        for note in self.notes:
            note.pause_to_previous_note = pause

    def __hash__(self):
        if self.hash is None:
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

    def __init__(self, time, duration, event, meta_context=None):
        # timestamp from original song - used purely for debugging purposes
        self.time = time

        # how long to play this note (not how many ticks until next note)
        self.duration = duration

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
        return (self.duration << 20) | (self.channel << 15) | (self.pitch << 8) | self.velocity
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
            (self.time, self.duration,
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
