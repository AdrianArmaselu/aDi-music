from midi import events
from graphmodel.model import instruments
from graphmodel.utils import MidiUtils

__author__ = 'Adisor'


class InstrumentSoundEvent(object):
    """
    This class is used for storing notes that are played starting at the exact same time

    If the size of the list is greater than 1 - this object symbolizes a chord
    """

    def __init__(self, instrument=instruments.PIANO):
        self._instrument = instrument
        self._notes = []
        self._hash = None

    def set_instrument(self, instrument):
        self._instrument = instrument

    def get_start_time(self):
        if len(self._notes) == 0:
            return 0
        return self._notes[0].get_start_time()

    def add_note(self, note):
        self._notes.append(note)
        self._hash = None

    def first(self):
        return self._notes[0]

    def get_notes(self):
        return self._notes

    def __hash__(self):
        """
        Builds the hash first if it is null. The hash is built by creating a tuple of notes and using the builtin
        hash function on the tuple

        The tuple contains the notes in sorted order by duration because the tuple hashing function should not care
        about the order of the notes

        Things the hash could include: pauses
        """
        if self._hash is None:
            notes_tuple = ()
            for note in sorted(self._notes, key=lambda key: self._notes[0].duration):
                notes_tuple += (note,)
            self._hash = (hash(notes_tuple) << 8) | len(notes_tuple)
        return self._hash

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, str(self._notes))


class OrchestralSoundEvent(object):
    """
    Collection of instrument sound events
    """

    def __init__(self):
        self._instrument_sound_events = {}
        self._hash = None

    def add_sound_event(self, instrument, sound_event):
        self._instrument_sound_events[instrument] = sound_event

    def get_instruments(self):
        return self._instrument_sound_events.keys()

    def __hash__(self):
        """
        Sorted by instrument before hashing
        """
        if self._hash is None:
            sound_events_tuple = ()
            for instrument in sorted(self.get_instruments()):
                sound_events_tuple += (self._instrument_sound_events[instrument],)
            self._hash = (hash(sound_events_tuple) << 8) | len(sound_events_tuple)
        return self._hash

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __str__(self):
        string = str(self.__class__.__name__)
        for instrument in self.get_instruments():
            string += 'Instrument:{}, {}\n'.format(instrument, str(self._instrument_sound_events[instrument]))
        return string


class Note(object):
    """
    The class that represents a musical note.

    The class contains a custom hash function to ensure its uniqueness.
    A note is unique by its duration and pitch
    """

    def __init__(self, start_time=0, duration=0, pitch=0, volume=0):
        self.start_time = start_time
        self.duration = duration
        self.pitch = pitch
        self.volume = volume
        self._hash = None

    # duration | tempo | pitch
    # bytes: >0 | 24 | 8
    def encoding(self):
        return (self.duration << 8) | self.pitch

    def __hash__(self):
        if self._hash is None:
            self._hash = self.encoding()
        return self._hash

    def __eq__(self, other):
        return self.encoding() == other.encoding()

    def __str__(self):
        args = (self.__class__.__name__, self.start_time, self.duration, self.pitch, self.volume, self._hash)
        return '{}(s:{}, d:{}, pitch:{}, vol:{}, hash:{})'.format(args)
