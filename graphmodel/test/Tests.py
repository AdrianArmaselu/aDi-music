import logging
import time
import midi
from midi.events import SetTempoEvent
import pygame
from graphmodel import Utils
from graphmodel.MidiIO import MidiIO

__author__ = 'Adisor'

# FORMAT = '%(asctime)-12s %(message)s'
# logging.basicConfig(format=FORMAT)
#
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)
# # logger.warning('Protocol problem: %s', 'connection reset')
# logger.info('Lala: %s', 'asd')
# pattern = midi.read_midifile("../music/bach.mid")
pattern = midi.read_midifile("../music/Eminem/thewayiam.mid")
print pattern
Utils.delete_tracks(pattern, 4, 9)
Utils.delete_tracks(pattern, 1, 3)
Utils.convert_channel(pattern[1], 12)
# print pattern
midi.write_midifile("test.mid", pattern)

pattern = midi.read_midifile("test.mid")
# pattern = midi.read_midifile("../music/Eminem/thewayiam.mid")
print pattern
pygame.init()
pygame.mixer.music.load("test.mid")
# pygame.mixer.music.load("../music/Eminem/thewayiam.mid")
pygame.mixer.music.play()
while pygame.mixer.music.get_busy():
    pygame.time.wait(1000)

