from collections import OrderedDict
from random import randint
import midi
from midi.events import NoteOnEvent
from midi.events import NoteOffEvent
from graphmodel.MidiIO import MidiIO
from graphmodel.Objects import SoundEvent, is_chord

__author__ = 'Adisor'


# TODO: HANDLE CHANNELS IN A NEW WAY
# TODO: HANDLE ALL CHANNELS
# TODO: RESOLUTION METHOD FOR SONGS METADATAS
# TODO: CONSIDER IGNORING CHANNEL
# TODO: INCLUDE CHANNEL IN NGram model
#
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
    def __init__(self, mappings, n):
        self.mappings = mappings
        self.n = n
        self.tuple_distribution = {}
        self.event_distribution = {}
        self.tuples = {}
        self.build()

    def build(self):
        tuples_being_built = []

        for tick in self.mappings:
            first_channel = self.mappings[tick][0]
            # check to see if there are any notes
            if has_notes(first_channel):
                sound_event = SoundEvent(self.mappings[tick][0])
                # create a new tuple
                tuples_being_built.append(())
                # append the notes to our list of tuples
                for i in range(len(tuples_being_built)):
                    tuples_being_built[i] += (sound_event,)
                self.update_event_distribution(sound_event)
            else:
                continue
            # if the first tuple has n elements, update its count, then remove it
            first_tuple = tuples_being_built[0]
            if len(first_tuple) >= self.n:
                self.update_tuples(tuples_being_built)

    # for logging purposes
    def update_event_distribution(self, sound_event):
        if sound_event not in self.event_distribution:
            self.event_distribution[sound_event] = 1
        else:
            self.event_distribution[sound_event] += 1

    def update_tuples(self, tuples_being_built):
        first_tuple = tuples_being_built[0]
        tuples_id = hash(first_tuple)
        self.tuples[tuples_id] = first_tuple
        # if the tuple is new, then set its count to 1, otherwise update it
        if tuples_id not in self.tuple_distribution:
            self.tuple_distribution[tuples_id] = 1
        else:
            self.tuple_distribution[tuples_id] += 1
        # del tuples_being_built[0]
        tuples_being_built.pop(0)

    def __str__(self):
        string = "SoundEventDistribution (unique events=%d)" % len(self.event_distribution) + "\n"
        string += "SoundEvent: Count \n"
        for key in self.event_distribution:
            string += '{}: {}\n'.format(key, self.event_distribution[key])
        string += ("TupleDistribution (unique tuples=%d)" % len(self.tuple_distribution)) + "\n"
        string += "Tuple: Count \n"
        string += self.to_string(self.tuple_distribution)
        return string

    def to_string(self, distribution):
        string = ""
        for key in distribution:
            for t in self.tuples[key]:
                string += '{}: {}\n'.format(t, distribution[key])
        return string


class MusicGenerator(object):
    def __init__(self, selection_policy, ngram, song_duration):
        self.selection_policy = selection_policy
        self.ngram = ngram
        self.tuples = ngram.tuples
        self.distribution = ngram.tuple_distribution
        # measured in number of notes
        self.song_duration = song_duration
        self.sequence = []

    def generate(self):
        # first tuple
        event_tuple = self.tuples[self.tuples.keys()[0]]
        for i in range(0, self.song_duration, 1):
            for sound_event in event_tuple:
                self.sequence.append(sound_event)
            event_tuple = self.next_tuple(event_tuple[-1])
            # we are only concerned about elements after the first one
            event_tuple = event_tuple[1:]

    # find the tuple with the maximum count that starts with last_sound_event
    def next_tuple(self, last_sound_event):
        max_count = 0
        next_tuple = None
        for key in self.distribution:
            count = self.distribution[key]
            t = self.tuples[key]
            if self.tuples[key][0] == last_sound_event and (count > max_count):
                max_count = count
                next_tuple = t


        # in NLP, once this condition is reached, the program ends, but it works differently with music
        if next_tuple is None:
            if self.selection_policy is SelectionPolicy.RANDOM:
                i = randint(0, len(self.tuples))
                print "random int {}".format(i)
                next_tuple = self.tuples[self.tuples.keys()[i]]
            if self.selection_policy is SelectionPolicy.NEXT:
                pass  # no implementation
            if self.selection_policy is SelectionPolicy.BEFORE_HIGHEST_RANGE:
                pass  # no implementation
            if self.selection_policy is SelectionPolicy.AFTER_HIGHEST_RANGE:
                pass  # no implementation

        return next_tuple

    def to_midi_pattern(self):
        pattern = midi.Pattern()
        track = midi.Track()
        for sound_event in self.sequence:
            if is_chord(sound_event):
                for note in sound_event.notes:
                    on_event = midi.NoteOnEvent(channel=note.channel, tick=0, pitch=note.pitch,
                                                velocity=note.velocity)
                    track.append(on_event)

    def print_sequence(self):
        print "SEQUENCE:"
        for item in self.sequence:
            print item


class SelectionPolicy:
    def __init__(self):
        pass

    RANDOM = 0
    NEXT = 1
    BEFORE_HIGHEST_RANGE = 2
    AFTER_HIGHEST_RANGE = 3


# define properties
midi_file = "mary.mid"
number_of_notes = 2
selection_policy = SelectionPolicy.RANDOM

# load file
midi_io = MidiIO(midi_file)
midi_io.print_events()

# get the note mappings
mappings = midi_io.mappings
midi_io.print_mappings()

# construct the bigram
bigram = NGram(mappings, 3)
print bigram

# construct the generator and generate a sequence of sound events
generator = MusicGenerator(selection_policy, bigram, number_of_notes)
generator.generate()
generator.print_sequence()

sequence = generator.sequence
