from graphmodel.model import instruments

__author__ = 'Adisor'


class InstrumentSoundEvent(object):
    """
    This class is used for storing notes that are played starting at the exact same time

    If the size of the list is greater than 1 - this object symbolizes a chord
    """

    def __init__(self, instrument=instruments.PIANO):
        self.instrument = instrument
        self.notes = []
        self.hash = None

    def set_instrument(self, instrument):
        self.instrument = instrument

    def get_start_time(self):
        if len(self.notes) == 0:
            return 0
        return self.notes[0].get_start_time()

    def add_note(self, note):
        self.notes.append(note)
        self.hash = None

    def get_pause_to_next_note(self):
        return self.notes[0].get_pause_to_next_note()

    def first(self):
        return self.notes[0]

    def get_notes(self):
        return self.notes

    def update_pause_to_next_note(self, pause):
        for note in self.notes:
            note.set_pause_to_next_note(pause)

    def update_pause_to_previous_note(self, pause):
        for note in self.notes:
            note.set_pause_to_previous_note(pause)

    def __hash__(self):
        """
        Builds the hash first if it is null. The hash is built by creating a tuple of notes and using the builtin
        hash function on the tuple

        The tuple contains the notes in sorted order by duration because the tuple hashing function should not care
        about the order of the notes

        Things the hash could include: pauses
        """
        if self.hash is None:
            notes_tuple = ()
            for note in sorted(self.notes, key=lambda key: self.notes[0].duration):
                notes_tuple += (note,)
            self.hash = (hash(notes_tuple) << 8) | len(notes_tuple)
        return self.hash

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, str(self.notes))


class OrchestralSoundEvent(object):
    """
    Collection of instrument sound events
    """

    def __init__(self):
        self.instrument_sound_events = {}
        self.hash = None

    def add_sound_event(self, instrument, sound_event):
        self.instrument_sound_events[instrument] = sound_event

    def get_instruments(self):
        return self.instrument_sound_events.keys()

    def __hash__(self):
        """
        Sorted by instrument before hashing
        """
        if self.hash is None:
            sound_events_tuple = ()
            for instrument in sorted(self.get_instruments()):
                sound_events_tuple += (self.instrument_sound_events[instrument],)
            self.hash = (hash(sound_events_tuple) << 8) | len(sound_events_tuple)
        return self.hash

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __str__(self):
        string = str(self.__class__.__name__)
        for instrument in self.get_instruments():
            string += 'Instrument:{}, {}\n'.format(instrument, str(self.instrument_sound_events[instrument]))
        return string


# TODO: PAUSES BETWEEN NOTES SHOULD NOT BE HERE
class Note(object):
    """
    The class that represents a musical note.

    The class contains a custom hash function to ensure its uniqueness.
    A note is unique by its duration and pitch
    """

    def __init__(self, pitch=0, volume=0):
        self._time_measurements = TimeMeasurements()
        self._meta = NoteMeta()
        self.pitch = pitch
        self.volume = volume
        self.hash = None

    def get_start_time(self):
        return self._time_measurements.start_time

    def set_pause_to_next_note(self, pause):
        self._time_measurements.pause_to_next_note = pause

    def get_pause_to_next_note(self):
        return self._time_measurements.pause_to_next_note

    def set_pause_to_previous_note(self, pause):
        self._time_measurements.pause_to_previous_note = pause

    # duration | tempo | pitch
    # bytes: >0 | 24 | 8
    def encoding(self):
        return (self._time_measurements.duration << 32) | (self._meta.tempo.encoding() << 8) | self.pitch

    def __hash__(self):
        if self.hash is None:
            self.hash = self.encoding()
        return self.hash

    def __eq__(self, other):
        return self.encoding() == other.encoding()

    def __str__(self):
        args = (self.__class__.__name__, self.pitch, self.volume, self.hash, str(self._time_measurements),
                str(self._meta))
        return '{}(pitch:{}, vol:{}, hash:{}, {}, {})'.format(args)


class TimeMeasurements(object):
    def __init__(self, start_time=0, duration=0, pause_to_next_note=0, pause_to_previous_note=0):
        self.start_time = start_time
        self.duration = duration
        self.pause_to_next_note = pause_to_next_note
        self.pause_to_previous_note = pause_to_previous_note

    def __str__(self):
        args = (self.__class__.__name__, self.start_time, self.duration, self.pause_to_previous_note,
                self.pause_to_next_note)
        return '{}(s:{}, d:{}, p-:{}, p+:{})'.format(args)


class NoteMeta(object):
    """
    """

    def __init__(self, tempo=Tempo()):
        self.tempo = tempo

    def encoding(self):
        return self.tempo.encoding()

    def __str__(self):
        return '{}({}):'.format(self.__class__.__name__, str(self.tempo))


class Tempo(object):
    def __init__(self, data=None):
        if not data:
            data = [0, 0, 0]
        self.data = data

    def encoding(self):
        return (self.data[0] << 16) | (self.data[1] << 8) | self.data[2]

    def __str__(self):
        return str(self.data)
