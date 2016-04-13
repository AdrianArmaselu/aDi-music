import logging
import time
import midi
from midi.events import SetTempoEvent
import pygame
from graphmodel.MidiIO import MidiIO

__author__ = 'Adisor'

# FORMAT = '%(asctime)-12s %(message)s'
# logging.basicConfig(format=FORMAT)
#
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)
# # logger.warning('Protocol problem: %s', 'connection reset')
# logger.info('Lala: %s', 'asd')
pattern = midi.read_midifile("music/bach.mid")
print pattern
for track in pattern:
    new_track = midi.Track()
    for event in track:
        if type(event) == SetTempoEvent:
            continue
        new_track.append(event)
    pattern.remove(track)
    pattern.append(new_track)
    break


# midi.write_midifile("test.mid", pattern)
#
# pattern = midi.read_midifile("test.mid")
# print pattern

# pygame.init()
# pygame.mixer.music.load("test.mid")
# pygame.mixer.music.play()
#
# while pygame.mixer.music.get_busy():
#     pygame.time.wait(1000)

