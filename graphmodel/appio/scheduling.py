from collections import OrderedDict, defaultdict
from graphmodel.utils import MidiUtils

__author__ = 'Adisor'


class PatternSchedule(object):
    def __init__(self, scheduled_tracks, meta):
        self._scheduled_tracks = scheduled_tracks
        self._meta = meta

    def get_scheduled_tracks(self):
        return self._scheduled_tracks

    def get_meta_events(self):
        return [self._meta.key_signature_event, self._meta.time_signature_event]

    def get_resolution(self):
        return self._meta.resolution


class AbstractEventsScheduledTrack(object):
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
        return self._scheduled_events

    def sort(self):
        self._scheduled_events = OrderedDict(sorted(self._scheduled_events.items(), key=lambda key: key[0]))

    def __str__(self):
        string = ""
        for time in self._scheduled_events:
            string += str(time) + " " + str(self._scheduled_events[time]) + "\n"
        return string


class NotesAndEventsScheduledTrack(AbstractEventsScheduledTrack):
    """
    The algorithm works as follows:
    1. Initialize the "start" variable to 0. It will be used to keep track when the next SoundEvent object starts
    2. Loop through each SoundEvent object s of sequence seq
    3. Loop through each note n of s
    4. Schedule when n starts playing based on the start variable.
    5. Schedule when n stops playing based on the start variable + duration_ticks of the note
    6. End loop of s
    7. Update the start variable by the duration of the shortest note of s
    """

    def __init__(self, instrument=0, channel=0):
        super(NotesAndEventsScheduledTrack, self).__init__(channel)
        self._scheduled_events[0] = [MidiUtils.to_program_change_event(instrument)]

    def schedule_note(self, note, start):
        self.schedule_event(MidiUtils.to_note_on_event(note, self.channel), start)
        self.schedule_event(MidiUtils.to_note_off_event(note, self.channel), start + note.duration)


