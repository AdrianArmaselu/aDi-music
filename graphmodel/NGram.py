import Queue
from random import randint

import midi

from graphmodel.MidiIO import MidiIO
from graphmodel.Model import SoundEvent, is_chord, MusicalTranscript, OrderedFrames, RunningNotesTable
from graphmodel.Policies import SoundEventTupleSelectionPolicy, ChannelMixingPolicy, MetadataResolutionPolicy

__author__ = 'Adisor'

# TODO: HANDLE CHANNELS IN A NEW WAY
# TODO: HANDLE ALL CHANNELS
# TODO: RESOLUTION METHOD FOR SONGS METADATAS
# TODO: KEEP IN MIND DIFFERENT FILE FORMATS
"""
TODO: Methods for increasing distribution counts:
    velocity tolerance
    ticks tolerance
    duration tolerance
    pitch offset from other song
    pitch tolerance
"""


def print_tuple(t):
    for event in t:
        print event, "----"


def has_notes(channel_notes):
    return channel_notes and len(channel_notes) > 0


class NGram(object):
    def __init__(self, musical_transcript, n, policies=Policies.default()):
        self.music_transcript = musical_transcript
        self.n = n
        self.policies = policies
        self.frame_count = {}
        self.event_count = {}
        self.__build__()

    def __build__(self):
        frames = OrderedFrames(self.n)

        if self.policies.channel_mixing_policy is ChannelMixingPolicy.NO_MIX:
            for track in self.music_transcript.tracks:
                for sound_event in self.music_transcript.get_sound_events(track):
                    frames.add(sound_event)

                # for logging purposes
                if sound_event not in self.event_count:
                    self.event_count[0][sound_event] = 1
                else:
                    self.event_count[0][sound_event] += 1

                # update the count with the first frame
                if frames.is_first_frame_full():
                    frame = frames.remove_first()
                    if frame not in self.frame_count:
                        self.frame_count[frame] = 1
                    self.frame_count[frame] += 1

        # needs implementation
        if self.policies.channel_mixing_policy is ChannelMixingPolicy.MIX:
            pass


class MusicGenerator(object):
    def __init__(self, ngram, song_duration, policies=Policies.default()):
        self.ngram = ngram
        # measured in number of notes
        self.frame_count = ngram.frame_count
        self.song_duration = song_duration
        self.policies = policies
        self.sequence = []

    def generate(self):

        # first tuple
        frame = self.frame_count[self.frame_count.keys()[0]]
        for i in range(0, self.song_duration, 1):
            for sound_event in frame.sound_events:
                self.sequence.append(sound_event)
            frame = self.next_frame(frame.last())
            # we are only concerned about elements after the first one
            frame = frame[1:]

    # find the frame with the maximum count that starts with last_sound_event
    def next_frame(self, last_sound_event):
        next_frame = None

        if self.policies.selection_policy is SoundEventTupleSelectionPolicy.HIGHEST_COUNT:
            max_count = 0
            for frame in self.frame_count:
                count = self.frame_count[frame]
                if frame.first() == last_sound_event and (count > max_count):
                    max_count = count
                    next_frame = frame
        return next_frame

    def to_midi_pattern(self):
        running_notes = Queue.PriorityQueue()
        pattern = midi.Pattern()
        track = midi.Track()
        for sound_event in self.sequence:
            if is_chord(sound_event):
                for note in sound_event.notes:
                    on_event = midi.NoteOnEvent(channel=note.channel, tick=note.wait_tick, pitch=note.pitch,
                                                velocity=note.velocity)
                    track.append(on_event)

    def print_sequence(self):
        print "SEQUENCE:"
        for item in self.sequence:
            print item


class Policies:
    def __init__(self, selection_policy, metadata_resolution_policy, channel_mixing_policy):
        self.selection_policy = selection_policy
        self.metadata_resolution_policy = metadata_resolution_policy
        self.channel_mixing_policy = channel_mixing_policy

    @staticmethod
    def default():
        return Policies(SoundEventTupleSelectionPolicy.HIGHEST_COUNT, MetadataResolutionPolicy.FIRST_SONG_RESOLUTION,
                        ChannelMixingPolicy.NO_MIX)

# define properties
midi_file = "bach.mid"
number_of_notes = 2

# load file
data = MidiIO(midi_file)
print data

# get the notes table
table = data.table
print data.table

# build the musical transcript
musical_transcript = MusicalTranscript(table)

# construct the ngram
ngram = NGram(musical_transcript, 3)
print ngram

# construct the generator and generate a sequence of sound events
generator = MusicGenerator(ngram, number_of_notes)
generator.generate()
generator.print_sequence()

sequence = generator.sequence
