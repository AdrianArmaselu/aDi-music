from collections import OrderedDict
import midi
from midi import events
from graphmodel import MidiUtils

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
            print transcript.get_tracks()
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
        self.scheduled_events = {}
        self.schedule_track(track)

    def schedule_track(self, track):

        start = 0
        for sound_event in track:
            for note in sound_event.notes:
                self.schedule_note(note, start)
            start += sound_event.shortest_note().next_delta_ticks
        self.scheduled_events = OrderedDict(sorted(self.scheduled_events.items(), key=lambda key: key[0]))

    def schedule_note(self, note, start):
        if start not in self.scheduled_events:
            self.scheduled_events[start] = []
        if start + note.duration_ticks not in self.scheduled_events:
            self.scheduled_events[start + note.duration_ticks] = []
        self.scheduled_events[start].append(MidiUtils.note_on_event(note))
        self.scheduled_events[start + note.duration_ticks].append(MidiUtils.note_off_event(note))


class MidiConverter:
    """
    """

    def __init__(self, pattern_schedule):
        self.pattern_schedule = pattern_schedule
        self.pattern = midi.Pattern()
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
                for note_on_event in track_schedule.scheduled_events[tick]:
                    note_on_event.tick = tick - last_tick
                    last_tick = tick
                    track.append(note_on_event)
            track.append(events.EndOfTrackEvent(tick=1))
            tracks.append(track)
        self.pattern = midi.Pattern(tracks)