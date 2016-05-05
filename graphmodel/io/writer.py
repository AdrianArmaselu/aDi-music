import midi
from midi import events
from graphmodel import defaults
from graphmodel.io import applogger

__author__ = 'Adisor'


class MidiFileWriter(object):
    def __init__(self, pattern_schedule):
        self.pattern_schedule = pattern_schedule
        self.pattern = self.create_midi_pattern()
        logger = applogger.logger
        logger.debug(self.pattern)

    def create_midi_pattern(self):
        """
        Loops through each event and updates its tick based on delta ticks.
        Delta ticks are also called times between events (start of an event or its end)

        After updating the event, it adds it to a track, then the track is added to the midi pattern
        """
        meta_events = self.pattern_schedule.get_meta_events() + [events.EndOfTrackEvent(tick=0)]
        meta_track = midi.Track(events=meta_events)
        tracks = [meta_track]
        for track_schedule in self.pattern_schedule.get_scheduled_tracks():
            miditrack = MidiTrackWriter(track_schedule).write_midi_track()
            tracks.append(miditrack)
        return midi.Pattern(tracks=tracks, resolution=self.pattern_schedule.get_resolution(), format=defaults.FORMAT)

    def save_to_file(self, midi_file_name):
        midi.write_midifile(midi_file_name, self.pattern)


class MidiTrackWriter(object):
    def __init__(self, track_schedule):
        self.track_schedule = track_schedule
        self.track = midi.Track()

    def write_midi_track(self):
        self.track_schedule.sort()
        last_time = 0
        for time in self.track_schedule.get_scheduled_events():
            last_time = self.append_events_to_track(time, last_time)
        self.track.append(events.EndOfTrackEvent(tick=1))
        return self.track

    def append_events_to_track(self, time, last_time):
        for event in self.track_schedule.get_scheduled_events()[time]:
                event.tick = time - last_time
                last_time = time
                self.track.append(event)
        return last_time
