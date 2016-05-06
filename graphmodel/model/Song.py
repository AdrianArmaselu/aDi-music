from collections import defaultdict, OrderedDict

from graphmodel.model.SongObjects import InstrumentSoundEvent

__author__ = 'Adisor'


# TODO: ADD OPTION TO LOAD NOTES BUT ON SEPARATE TRACKS
class SongTranscript(object):
    """
    Used for storing simplified musical information from file in the form of sound events

    The class stores sound events into multiple tracks, where each track has a specific instrument
    The class also holds meta information about the song, such as key signature and time signature
    """

    def __init__(self, transcript_meta=None):
        self._transcript_meta = transcript_meta
        self.instrument_tracks = defaultdict(lambda: None)

    def get_tempo_events(self):
        """
        :return: list of tempo events
        """
        return self.get_tempo_dict().values()

    def get_tempo_dict(self):
        return self._transcript_meta.tempo_dict

    def set_transcript_meta(self, transcript_meta):
        self._transcript_meta = transcript_meta

    def set_track(self, instrument, track):
        """
        Sets the track for the specified instrument
        :param instrument: midi instrument number
        :param track: instrument track
        """
        self.instrument_tracks[instrument] = track

    def add_track(self, instrument, track):
        """
        If there is no track on the channel, then the track notes are added to the channel, otherwise, the tracks
        are merged together
        """
        if self.instrument_tracks[instrument] is None:
            self.set_track(instrument, track)
        else:
            self.merge_tracks(instrument, track)

    def merge_tracks(self, instrument, track):
        """
        Merges the track on the current channel with the parameter track
        The merge algorithm ensures the notes are in sorted order by time
        """
        final_track = InstrumentTrack()
        param_times = track.times()
        param_index = 0
        times = self.instrument_tracks[instrument].times()
        index = 0
        # merge both tracks into one track in order of time
        while param_index < len(param_times) or index < len(times):
            if param_index < len(param_times):
                param_time = param_times[param_index]
            if index < len(times):
                time = times[index]
            # merge from param track if param time is smaller or the entire source track has been merged
            can_add = (param_time < time or (param_time > time and index == len(times)))
            if param_index < len(param_times) and can_add:
                self.add_notes_to_track(track, final_track, param_time)
                param_index += 1
            # merge from both tracks
            if param_time == time:
                self.add_notes_to_track(track, final_track, param_time)
                self.add_notes_to_track(self.instrument_tracks[instrument], final_track, time)
                param_index += 1
                index += 1
            # merge from self track if time is smaller or the entire param track has been merged
            can_add = (param_time > time or (param_time < time and param_index == len(param_times)))
            if index < len(times) and can_add:
                self.add_notes_to_track(self.instrument_tracks[instrument], final_track, time)
                index += 1

        self.set_track(instrument, final_track)

    @staticmethod
    def add_notes_to_track(from_track, to_track, time):
        for note in from_track.get_sound_event(time).get_notes():
            to_track.add_note(note)

    def get_instruments(self):
        """
        :return: list of instrument numbers
        """
        return self.instrument_tracks.keys()

    def get_track(self, instrument):
        return self.instrument_tracks[instrument]

    def get_tracks(self):
        """
        :return: list of tracks
        """
        return self.instrument_tracks.values()

    def get_transcript_meta(self):
        return self._transcript_meta

    def __str__(self):
        string = "MusicalTranscript:\n"
        for instrument in self.instrument_tracks:
            string += str(self.instrument_tracks[instrument])
        return string


class InstrumentTrack(object):
    """
    This class stores note information in sorted order by time. Each note is stored into a sound event, and
    there are sound events that can have multiple notes, meaning the sound event is a chord

    This class also stores meta information regarding instrument and channel
    NOTE: THIS CLASS DOES NOT MAINTAIN SORTED TIMES, BUT ONLY REMEMBERS INSERTION ORDER
    IF YOU WANT THE ELEMENTS TO BE SORTED BY TIME, INSERT THE SOUND EVENTS BY TIME
    """

    def __init__(self):
        self._sound_events = OrderedDict()

    def times(self):
        """
        :return: list of numbers which represent absolute times for each played note
        """
        return self._sound_events.keys()

    def get_sound_event(self, time):
        """
        :param time: integer time
        :return: the sound event that starts at time
        """
        return self._sound_events[time]

    def get_sound_events(self):
        """
        :return: list of sound events
        """
        return self._sound_events.values()

    def add_sound_event(self, sound_event):
        self._sound_events[sound_event.get_start_time()] = sound_event

    def add_note(self, note):
        """
        Adds a note to the current sound event, and if there is no sound event at the note start time,
        a new sound event is created
        """
        if note.start_time not in self._sound_events:
            self._sound_events[note.start_time] = InstrumentSoundEvent()
        self._sound_events.get(note.start_time).add_note(note)

    def __len__(self):
        return len(self._sound_events)

    def __str__(self):
        string = "Track\n"
        for time in sorted(self._sound_events.keys()):
            string += str(self._sound_events.get(time)) + "\n"
        return string
