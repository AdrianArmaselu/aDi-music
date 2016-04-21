from collections import defaultdict
import logging
import time
import midi
from midi.events import SetTempoEvent
import pygame
from graphmodel import MidiUtils
from graphmodel.MidiIO import MidiIO

__author__ = 'Adisor'

# FORMAT = '%(asctime)-12s %(message)s'
# logging.basicConfig(format=FORMAT)
#
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)
# # logger.warning('Protocol problem: %s', 'connection reset')
# logger.info('Lala: %s', 'asd')
pattern = midi.read_midifile("../music/bach.mid")
# pattern = midi.read_midifile("../music/Eminem/thewayiam.mid")
print pattern
MidiUtils.delete_tracks(pattern, 2, 3)
# Utils.delete_tracks(pattern, 1, 3)
# Utils.change_program(pattern[1], [26])
# Utils.convert_channel(pattern[1], 0)
# Utils.change_key_signature(pattern[0], [0, 1])
# # print pattern
midi.write_midifile("test.mid", pattern)
#
# pattern = midi.read_midifile("test.mid")
# # pattern = midi.read_midifile("../music/Eminem/thewayiam.mid")
# print pattern
pygame.init()
pygame.mixer.music.load("test.mid")
pygame.mixer.music.play()
while pygame.mixer.music.get_busy():
    pygame.time.wait(1000)

