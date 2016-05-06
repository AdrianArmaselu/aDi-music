import logging
from random import randint

import midi
from graphmodel.NGram import MultiInstrumentNGram

from graphmodel.appio import reader
from graphmodel.appio.scheduling import AbstractEventsScheduledTrack, NotesAndEventsScheduledTrack, PatternSchedule
from graphmodel.appio.writer import MidiFileWriter
from graphmodel.model import Policies
from graphmodel.model.Policies import FrameSelectionPolicy

__author__ = 'Adisor'


# TODO: BREAK REPEATING LOOPS IN GENERATION
# TODO: USE SEED FOR RANDOM GENERATOR TO REPRODUCE
# TODO: DURATION IS NOT COMPUTED CORRECTLY
class SingleInstrumentGenerator(object):
    """
    This class generates music. Currently, it takes the sound event data from an ngram, but that can change
    """

    def __init__(self, ngram, duration, meta_track):
        self.ngram = ngram
        self.duration = duration
        self.meta_track = meta_track

    def generate(self, instrument, channel):
        """
        """
        scheduler = TrackScheduler(meta_track=self.meta_track, instrument=instrument, channel=channel)
        frame = self.ngram.get_first_frame()
        while scheduler.get_duration() < self.duration:
            scheduler.schedule_frame_components(frame.get_components()[1:])
            frame = self.next_frame(frame.last())
            # we are only concerned about elements after the first one
        return scheduler.get_scheduled_track()

    # find the frame with the maximum count that starts with last_sound_event
    def next_frame(self, last_frame_component):
        if Policies.frame_selection_policy is FrameSelectionPolicy.HIGHEST_COUNT:
            return self.get_next_highest_count_frame(last_frame_component)
        if Policies.frame_selection_policy is FrameSelectionPolicy.RANDOM:
            pass
        if Policies.frame_selection_policy is FrameSelectionPolicy.PROB:
            return self.get_prob_next_frame(last_frame_component)
        return None

    def get_next_highest_count_frame(self, last_sound_event):
        next_frame = self.ngram.get_next_best_frame(last_sound_event)
        if next_frame is None:
            next_frame = self.ngram.get_random_frame()
        return next_frame

    def get_prob_next_frame(self, last_sound_event):
        # Gets the next frame according to probability
        next_frame = None
        total_count = 0
        frame_list = []
        count_list = []
        if not self.ngram.has_index(last_sound_event):
            return self.ngram.get_random_frame()
        indexes = self.ngram.get_sound_event_indexes(last_sound_event)
        for index in indexes:
            frame = self.ngram.get_indexed_frame(index)
            count = self.ngram.get_frame_count(frame)
            if frame.first() == last_sound_event:
                total_count += count
                frame_list.append(frame)
                count_list.append(total_count)
        key = randint(0, total_count)
        for i, count in enumerate(count_list):
            if key <= count:
                next_frame = frame_list[i]
                break
        # this means we reached the end of the samples, pick a random next frame
        if next_frame is None:
            next_frame = self.ngram.get_random_frame()
        return next_frame


# TODO: TEMPOS SHOULD BE UNIQUE AND CAN ONLY HAVE ONE AT A TIME NOT TWO( which happens when taking notes further in the track)
class TrackScheduler(object):
    def __init__(self, meta_track, instrument=0, channel=0):
        self.meta_track = meta_track
        self.time = 0
        self.scheduled_track = NotesAndEventsScheduledTrack(instrument=instrument, channel=channel)

    def schedule_frame_components(self, components):
        for component in components:
            sound_event = component.get_sound_event()
            # add tempo and other events
            for note in sound_event.get_notes():
                self.scheduled_track.schedule_note(note, self.time)
                self.meta_track.schedule_event(component.get_tempo_event(), self.time)
            self.time += component.get_pause_to_next_component()

    def get_duration(self):
        return self.scheduled_track.get_duration()

    def get_scheduled_track(self):
        return self.scheduled_track


def generate_multi_instrument_tracks(multi_instrument_ngram, duration):
    instruments = multi_instrument_ngram.get_instruments()
    meta_track = AbstractEventsScheduledTrack()
    # scheduled_tracks = [meta_track]
    scheduled_tracks = []
    channel = 0
    for instrument in instruments:
        ngram = multi_instrument_ngram.get_ngram(instrument)
        single_instrument_generator = SingleInstrumentGenerator(meta_track=meta_track, ngram=ngram, duration=duration)
        scheduled_track = single_instrument_generator.generate(instrument, channel)
        scheduled_tracks.append(scheduled_track)
        channel += 1
    return scheduled_tracks


"""
THINGS TO ADD:
SELECTING TEMPO AT EACH NOTE
GENERATE FROM A COLLECTION OF SONGS
USE DISTRIBUTED SOUND EVENT
"""


def generate(input_file, ticks, folder='default', nsize=2):
    # properties that should be on the website:
    Policies.frame_selection_policy = FrameSelectionPolicy.HIGHEST_COUNT

    # generation code
    name = input_file.split('.')[0]
    output_file_name = "%s/output-%s.mid" % (folder, name)
    in_transcript = reader.load_transcript("%s/%s" % (folder, input_file))
    ngram = MultiInstrumentNGram(nsize)
    ngram.build_from_transcript(in_transcript)
    scheduled_tracks = generate_multi_instrument_tracks(ngram, ticks)
    pattern_schedule = PatternSchedule(scheduled_tracks=scheduled_tracks, meta=in_transcript.get_transcript_meta())
    MidiFileWriter(pattern_schedule).save_to_file(output_file_name)
