from collections import OrderedDict
import midi
from midi.events import NoteOnEvent
from midi.events import NoteOffEvent

__author__ = 'Adisor'


# TODO: HANDLE CHANNELS IN A NEW WAY
# TODO: OFFSET PITCHES IF IT INCREASES DISTRIBUTION COUNTS
# TODO: RESOLUTION METHOD FOR SONGS METADATAS


class Note(object):
    def __init__(self, start_tick, ticks, channel, pitch, velocity):
        self.start_tick = start_tick
        self.ticks = ticks
        self.channel = channel
        self.pitch = pitch
        self.velocity = velocity

    # ticks | channel | pitch | velocity
    # bytes: 12 | 5 | 7 | 8
    def encode(self):
        return (self.ticks << 20) | (self.channel << 15) | (self.pitch << 8) | self.velocity

    def __hash__(self):
        return self.encode()

    def __str__(self):
        return ("Note(start_tick:%d, ticks:%d, channel:%d, pitch:%d, velocity:%d)" %
                (self.start_tick, self.ticks, self.channel, self.pitch, self.velocity))


def get_note_mappings(midi_file):
    mappings = {}
    running_events = {}
    cumulative_tick = 0
    pattern = midi.read_midifile(midi_file)
    for track in pattern:
        for event in track:
            cumulative_tick += event.tick
            event_type = type(event)
            if event_type != NoteOnEvent and event_type != NoteOffEvent:
                continue
            if event_type == NoteOffEvent or (event_type == NoteOnEvent and event.velocity == 0):
                (event_tick, event) = running_events[event.pitch][event.channel]
                del running_events[event.pitch][event.channel]
                ticks = cumulative_tick - event_tick
                new_note = Note(event_tick, ticks, event.channel, event.pitch, event.velocity)
                start_tick = new_note.start_tick
                channel = new_note.channel
                if start_tick not in mappings:
                    mappings[start_tick] = {}
                if new_note.channel not in mappings[start_tick]:
                    mappings[start_tick][channel] = []
                mappings[start_tick][channel].append(new_note)
            if event_type == NoteOnEvent:
                if event.channel not in running_events:
                    running_events[event.pitch] = {}
                running_events[event.pitch][event.channel] = (cumulative_tick, event)
    # sort by first key, the starting tick
    mappings = OrderedDict(sorted(mappings.items(), key=lambda key: key[0]))
    return mappings


def print_mappings(mappings):
    for tick in mappings:
        for channel in mappings[tick]:
            if len(mappings[tick][channel]) > 1:
                print "CHORD:"
            else:
                print "NOTE:"
            for note in mappings[tick][channel]:
                print note


class SoundEvent(object):
    def __init__(self, notes):
        self.notes = notes

    def __hash__(self):
        return hash(self.notes)


class NGram(object):
    def __init__(self, mappings, n):
        self.mappings = mappings
        self.n = n
        self.distribution = {}
        self.tuples = {}
        self.build()

    def build(self):
        tuples_being_built = [()]

        for tick in self.mappings:

            notes_in_first_channel = self.mappings[tick][0]
            # check to see if there are any notes
            if notes_in_first_channel and len(notes_in_first_channel) > 0:
                # create a new tuple
                tuples_being_built.append(())
                # append the notes to our list of tuples
                for ntuple in tuples_being_built:
                    ntuple += (SoundEvent(self.mappings[tick][0]))
            else:
                continue

            # if the first tuple has n elements, update its count, then remove it
            if len(tuples_being_built[0]) == self.n:
                tuples_id = hash(tuples_being_built[0])
                self.tuples[tuples_id] = tuples_being_built[0]
                # if the tuple is new, then set its count to 1, otherwise update it
                if self.distribution[tuples_id]:
                    self.distribution[tuples_id] += 1
                else:
                    self.distribution[tuples_id] = 1
                del tuples_being_built[0]


class MusicGenerator(object):
    def __init__(self, ngram, size):
        self.ngram = ngram
        self.tuples = ngram.tuples
        self.distribution = ngram.distribution
        self.size = size

    def generate(self):
        sequence = []
        distribution = self.distribution
        # first tuple
        tuple = distribution[distribution.keys()[0]]
        for i in range(0, self.size, 1):
            for sound_event in tuple:
                sequence.append(sound_event)
            tuple = self.next_tuple(tuple[-1])
        return sequence

    # find the tuple with the maximum count that starts with last_sound_event
    def next_tuple(self, last_sound_event):
        tuples = self.tuples
        distribution = self.distribution
        max_count = 0
        next_tuple = None
        for (tuple_key, count) in distribution:
            if tuples[tuple_key][0] == last_sound_event and count > max_count:
                max_count = count
                next_tuple = tuples[tuple_key][0]
        return next_tuple


mappings = get_note_mappings("mary.mid")
# print_mappings(mappings)

bigram = NGram(mappings, 2)
generator = MusicGenerator(bigram, 10)
sequence = generator.generate()
for event in sequence:
    print event

