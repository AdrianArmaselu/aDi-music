from collections import OrderedDict

import midi
from midi import events
from collections import defaultdict
from graphmodel.model.Meta import MetaContext

from graphmodel.utils import MidiUtils

__author__ = 'Adisor'


def to_midi_pattern(transcript):
    pattern_schedule = PatternSchedule(transcript)
    converter = MidiConverter(pattern_schedule)
    converter.convert()
    return converter.pattern


class PatternSchedule:
    def __init__(self, transcript):
        self.scheduled_tracks = []
        self.schedule_tracks(transcript)

    def schedule_tracks(self, transcript):
        for track in transcript.get_tracks():
            scheduled_track = TrackSchedule(track)
            self.scheduled_tracks.append(scheduled_track)


class TrackSchedule:
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

    def __init__(self, track):
        self.scheduled_events = defaultdict(lambda: [])
        self.previous_context = MetaContext()
        self.schedule_track(track)

    # TODO: add ticks to meta events but no ticks to the immediate next note
    def schedule_track(self, track):
        start = 0
        for sound_event in track.get_sound_events():
            for note in sound_event.get_notes():
                self.schedule_note(note, start)
                self.previous_context = note.meta_context
            start += sound_event.get_shortest_pause_to_next_note()
        self.scheduled_events = OrderedDict(sorted(self.scheduled_events.items(), key=lambda key: key[0]))

    def schedule_note(self, note, start):
        self.schedule_meta_events(note, start)
        self.scheduled_events[start].append(MidiUtils.note_on_event(note))
        self.scheduled_events[start + note.duration].append(MidiUtils.note_off_event(note))

    def schedule_meta_events(self, note, start):
        changed_events = self.previous_context.get_changed_events_from(note.meta_context)
        for meta_event in changed_events:
            meta_event.tick = 0
            self.scheduled_events[start].append(meta_event)
        self.previous_context = note.meta_context


# TODO: CHOOSE RESOLUTION FROM FILE OR WHATNOT
class MidiConverter:
    """
    """

    def __init__(self, pattern_schedule, resolution=120, format=0):
        self.pattern_schedule = pattern_schedule
        self.resolution = resolution
        self.format = format
        self.pattern = midi.Pattern(resolution=120, format=format)
        self.convert()

    def convert(self):
        """
        Loops through each event and updates its tick based on delta ticks.
        Delta ticks are also called times between events (start of an event or its end)

        After updating the event, it adds it to a track, then the track is added to the midi pattern
        """
        tracks = []
        for track_schedule in self.pattern_schedule.scheduled_tracks:
            track = midi.Track()
            last_tick = 0
            for tick in track_schedule.scheduled_events:
                for event in track_schedule.scheduled_events[tick]:
                    event.tick = tick - last_tick
                    last_tick = tick
                    track.append(event)
            track.append(events.EndOfTrackEvent(tick=1))
            tracks.append(track)
        self.pattern = midi.Pattern(tracks=tracks, resolution=self.resolution, format=self.format)
