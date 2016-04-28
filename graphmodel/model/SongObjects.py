__author__ = 'Adisor'


class SoundEvent(object):
    """
    This class is used for storing notes that are played starting at the exact same time

    If the size of the list is greater than 1 - this object symbolizes a chord
    """

    def __init__(self):
        self.notes = []
        self.hash = None

    def get_start_time(self):
        if len(self.notes) == 0:
            return 0
        return self.notes[0].time

    def add_note(self, note):
        self.notes.append(note)
        self.hash = None

    def get_pause_to_next_note(self):
        return self.notes[0].pause_to_next_note

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
        """
        Builds the hash first if it is null. The hash is built by creating a tuple of notes and using the builtin
        hash function on the tuple

        The tuple contains the notes in sorted order by duration because the tuple hashing function should not care
        about the order of the notes
        """
        if self.hash is None:
            notes_tuple = ()
            for note in sorted(self.notes, key=lambda key: self.notes[0].duration):
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
    The class that represents a musical note.

    The class contains a custom hash function to ensure its uniqueness.
    A note is unique by its duration and pitch
    """
    SHOW_CONTEXT_INFO = False

    def __init__(self, start_time, duration, event, meta_context=None):
        # timestamp from original song - used purely for loading and debugging purposes
        self.start_time = start_time

        # how long to play this note (not how many ticks until next note)
        self.duration = duration

        # ticks from last sound event
        self.pause_to_previous_note = 0

        # ticks to next sound event
        self.pause_to_next_note = 0
        self.channel = event.channel
        self.pitch = event.pitch
        self.volume = event.velocity

        self.meta_context = meta_context
        self.hash = None

    # ticks | pitch
    # bytes: 25 | 7
    def encode(self):
        return (self.duration << 7) | self.pitch

    def __hash__(self):
        if not self.hash:
            self.hash = self.encode()
        return self.hash

    def __eq__(self, other):
        return self.encode() == other.encode()

    def __str__(self):
        string = (
            "Note(timeline:%d, t:%d, "
            "dt-:%d, dt+:%d, "
            "ch:%d, pitch:%d, vol:%d" %
            (self.start_time, self.duration,
             self.pause_to_previous_note, self.pause_to_next_note,
             self.channel, self.pitch, self.volume))
        if self.SHOW_CONTEXT_INFO:
            string += (" meta_context: %s" % self.meta_context)
        string += ")"
        return string
