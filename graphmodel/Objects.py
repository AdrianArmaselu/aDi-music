__author__ = 'Adisor'


def is_chord(sound_event):
    return len(sound_event.notes) > 0


class Note(object):
    def __init__(self, start_tick, wait_ticks, duration_ticks, channel, pitch, velocity):
        self.start_tick = start_tick
        self.wait_ticks = wait_ticks
        self.duration_ticks = duration_ticks
        self.channel = channel
        self.pitch = pitch
        self.velocity = velocity

    # ticks | channel | pitch | velocity
    # bytes: 12 | 5 | 7 | 8
    def encode(self):
        return (self.duration_ticks << 20) | (self.channel << 15) | (self.pitch << 8) | self.velocity
        # return (self.ticks << 20) | (self.channel << 15) | (self.pitch << 8)
        # return (self.ticks << 20) | (self.channel << 15)

    def __hash__(self):
        return self.encode()

    def __eq__(self, other):
        # return self.__hash__() == other.__hash__ and abs(self.pitch - other.pitch) < 10
        return self.encode() == other.encode()

    def __str__(self):
        return ("Note(start_tick:%d, wait_ticks:%d, ticks:%d, channel:%d, pitch:%d, velocity:%d)" %
                (self.start_tick, self.wait_ticks, self.duration_ticks, self.channel, self.pitch, self.velocity))


class SoundEvent(object):
    def __init__(self, notes):
        self.notes = notes

    def __hash__(self):
        return (hash(self.notes[0]) << 4) | len(self.notes)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __str__(self):
        string = "("
        for note in self.notes:
            string += str(note) + ", "
        return string + ")"
