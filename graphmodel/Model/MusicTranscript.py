from collections import defaultdict
from graphmodel.Model import SoundEvent

__author__ = 'Adisor'


class MusicTranscript(object):
    """
    Simple data structure for storing sound events on multiple tracks
    """

    def __init__(self, ):
        self.tracks = defaultdict(SoundEventsTrack)

    def get_sound_events(self, channel):
        return self.tracks[channel].get_sound_events()

    def get_channels(self):
        return self.tracks.keys()

    def get_track(self, channel):
        return self.tracks[channel]

    def get_tracks(self):
        return self.tracks.values()

    def add_note(self, note):
        self.tracks[note.chan].add_note(note)

    def get_sound_event(self, channel, time_index):
        return self.tracks[channel].get_sound_event(time_index)

    def get_time_lt(self, channel, time):
        return self.tracks[channel].get_time_lt(time)

    def __str__(self):
        string = "MusicalTranscript:\n"
        for channel in self.tracks:
            string += str(self.tracks[channel])
        return string


class SoundEventsTrack:
    def __init__(self):
        self.times = []
        self.sound_events = defaultdict(SoundEvent)

    def add_note(self, note):
        self.times.append(note.time)
        self.sound_events[note.time].add_note(note)

    def get_sound_event(self, time_index):
        time = self.times[time_index]
        return self.sound_events[time]

    def get_sound_events(self):
        return self.sound_events.values()

    def get_time_lt(self, time):
        index = -1
        previous_time = time
        while previous_time >= time and abs(index) < len(self.times):
            index -= 1
            previous_time = self.times[index]
        return previous_time

    def __str__(self):
        string = "Track\n"
        for time in self.times:
            string += str(self.sound_events[time]) + "\n"
        return string
