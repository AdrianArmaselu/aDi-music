import logging
import time
from graphmodel.MidiIO import MidiIO

__author__ = 'Adisor'

# FORMAT = '%(asctime)-12s %(message)s'
# logging.basicConfig(format=FORMAT)
#
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)
# # logger.warning('Protocol problem: %s', 'connection reset')
# logger.info('Lala: %s', 'asd')

mapping = {}
mapping["abc"] = 5
print mapping.keys()[0]
mapping["bcd"] = 6
print mapping.keys()[0]
for i in range(0, 100, 1):
    mapping[str(i)] = i
    print mapping.keys()[0]

