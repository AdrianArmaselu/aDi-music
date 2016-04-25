from bisect import bisect_left
from collections import OrderedDict
from mido import MidiFile
import pygame.midi

__author__ = 'Adisor'

# data = MidiFile("music/bach.mid")
# mylist = [0, 0, 2 , 3]
# index = bisect_left(mylist, 1)
# print index
mapping = OrderedDict()
mapping[1] = 2
mapping[0] = 3
print mapping
