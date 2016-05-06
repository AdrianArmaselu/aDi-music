from collections import OrderedDict, defaultdict
from graphmodel.utils import MidiUtils

__author__ = 'Adisor'


class PatternSchedule(object):
    """
    Used by the writer to convert scheduled tracks into a midi tracks
    Contains metadata for the final midi Pattern
    """
    def __init__(self, scheduled_tracks, meta):
        self._scheduled_tracks = scheduled_tracks
        self._meta = meta

    def get_scheduled_tracks(self):
        """
        :return: list of scheduled tracks
        """
        return self._scheduled_tracks

    def get_meta_events(self):
        return [self._meta.key_signature_event, self._meta.time_signature_event]

    def get_resolution(self):
        """
        :return: midi resolution number
        """
        return self._meta.resolution


class AbstractEventsScheduledTrack(object):
    """
    Used to model time-mapped tracks that are used by the writer to convert into a midi track
    """
    def __init__(self, channel=None):
        self.channel = channel
        self._scheduled_events = defaultdict(lambda: [])
        self.duration = 0

    def schedule_event(self, event, start):
        self._scheduled_events[start].append(event)
        self.duration = max(start, self.duration)

    def get_duration(self):
        return self.duration

    def get_scheduled_events(self):
        """
        :return: list of sound event objects
        """
        return self._scheduled_events

    def sort(self):
        """
        :return: list of sound event objects sorted by time
        """
        self._scheduled_events = OrderedDict(sorted(self._scheduled_events.items(), key=lambda key: key[0]))

    def __str__(self):
        string = ""
        for time in self._scheduled_events:
            string += str(time) + " " + str(self._scheduled_events[time]) + "\n"
        return string


class NotesAndEventsScheduledTrack(AbstractEventsScheduledTrack):
    """
    Used to model tracks that contain mostly note events
    """

    def __init__(self, instrument=0, channel=0):
        super(NotesAndEventsScheduledTrack, self).__init__(channel)
        self._scheduled_events[0] = [MidiUtils.to_program_change_event(instrument)]

    def schedule_note(self, note, start):
        """
        Converts the note into a midi note_on event and schedules its start at the start time and end after its duration
        :param note: Note object
        :param start: start time of the note
        """
        self.schedule_event(MidiUtils.to_note_on_event(note, self.channel), start)
        self.schedule_event(MidiUtils.to_note_off_event(note, self.channel), start + note.duration)


