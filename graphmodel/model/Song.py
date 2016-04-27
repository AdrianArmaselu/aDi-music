from collections import defaultdict, OrderedDict

from graphmodel.model.SongObjects import SoundEvent, Track
from graphmodel.utils import MidiUtils

__author__ = 'Adisor'


# TODO: MERGE SOUND EVENTS WITH DIFFERENT INSTRUMENTS INTO ONE SOUND EVENT

class SongTranscript(object):
    """
    Used for storing simplified musical information from file in the form of sound events

    The class stores sound events into multiple tracks, where each track has a specific instrument
    """

    def __init__(self, song_meta=None):
        self.tracks = defaultdict(lambda: None)
        self.song_meta = song_meta

    def get_song_meta(self):
        return self.song_meta

    def set_track(self, channel, track):
        self.tracks[channel] = track

    def add_track(self, channel, track):
        if self.tracks[channel] is None:
            self.set_track(channel, track)
        else:
            self.merge_tracks(channel, track)

    def merge_tracks(self, channel, track):
        final_track = TranscriptTrack(channel, track.get_program_change_event())
        param_times = track.times()
        param_index = 0
        times = self.tracks[channel].times()
        index = 0
        # merge both tracks into one track and respect times
        while param_index < len(param_times) or index < len(times):
            if param_index < len(param_times):
                param_time = param_times[param_index]
            if index < len(times):
                time = times[index]
            # merge from param track
            can_add = (param_time < time or (param_time > time and index == len(times)))
            if param_index < len(param_times) and can_add:
                self.add_notes_to_track(track, final_track, param_time)
                param_index += 1
            # merge from both tracks
            if param_time == time:
                self.add_notes_to_track(track, final_track, param_time)
                self.add_notes_to_track(self.tracks[channel], final_track, time)
                param_index += 1
                index += 1
            # merge from self track
            can_add = (param_time > time or (param_time < time and param_index == len(param_times)))
            if index < len(times) and can_add:
                self.add_notes_to_track(self.tracks[channel], final_track, time)
                index += 1

        self.set_track(channel, final_track)

    @staticmethod
    def add_notes_to_track(from_track, to_track, time):
        for note in from_track.get_sound_event(time).get_notes():
            to_track.add_note(note)

    def get_channels(self):
        return self.tracks.keys()

    def get_track(self, channel):
        return self.tracks[channel]

    def get_tracks(self):
        return self.tracks.values()

    def __str__(self):
        string = "MusicalTranscript:\n"
        for channel in self.tracks:
            string += str(self.tracks[channel])
        return string


class SongMeta:
    def __init__(self, pattern):
        self.key_signature_event = None
        self.time_signature_event = None
        self.format = pattern.format
        self.resolution = pattern.resolution
        self.load_signature_events(pattern)

    def load_signature_events(self, pattern):
        self.key_signature_event = MidiUtils.get_key_signature_event(pattern)
        self.time_signature_event = MidiUtils.get_time_signature_event(pattern)


class TranscriptTrack(Track):
    """
    THIS CLASS DOES NOT MAINTAIN SORTED TIMES, BUT ONLY REMEMBERS INSERTION ORDER
    IF YOU WANT THE ELEMENTS TO BE SORTED BY TIME, INSERT THE SOUND EVENTS BY TIME
    """

    def __init__(self, channel=0, program_change_event=None):
        Track.__init__(self)
        self.previous_time = 0
        self.current_time = 0
        self.channel = channel
        self.program_change_event = program_change_event
        self._sound_events = OrderedDict()

    def set_channel(self, channel):
        self.channel = channel

    def get_channel(self):
        return self.channel

    def get_instrument(self):
        return self.program_change_event.data[0]

    def get_program_change_event(self):
        return self.program_change_event

    def set_program_change_event(self, program_change_event):
        self.program_change_event = program_change_event

    def get_sound_event(self, time):
        return self._sound_events[time]

    def get_sound_events(self):
        return self._sound_events.values()

    def add_sound_event(self, sound_event):
        for note in sound_event.get_notes():
            self.add_note(note)

    def add_note(self, note):
        sound_event = self._sound_events.get(note.time)
        if sound_event is None:
            self._sound_events[note.time] = SoundEvent()
        sound_event = self._sound_events.get(note.time)
        sound_event.add_note(note)

        # update previous sound event note pauses
        previous = self._sound_events.get(self.current_time)
        if note.time == self.current_time:
            previous = self._sound_events.get(self.previous_time)
        if previous is not None:
            pause = note.time - previous.get_time()
            previous.update_pause_to_next_note(pause)
            sound_event.update_pause_to_previous_note(pause)

        if note.time != self.current_time:
            self.previous_time = self.current_time
            self.current_time = note.time

    def times(self):
        return self._sound_events.keys()

    def __len__(self):
        return len(self._sound_events)

    def __str__(self):
        string = "Track\n"
        for time in sorted(self._sound_events.keys()):
            string += str(self._sound_events.get(time)) + "\n"
        return string