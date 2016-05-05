from collections import OrderedDict
import logging
from operator import itemgetter
from midi import events
import operator
from graphmodel.Generator import SingleInstrumentGenerator
from graphmodel.NGram import _SingleInstrumentNGram
from graphmodel.io.reader import load_transcript

__author__ = 'Adisor'


def clear_log_file():
    with open(logfile, 'w'):
        pass

logfile = 'log.log'
clear_log_file()

FORMAT = '%(asctime)-12s %(message)s'
logging.basicConfig(filename=logfile, format=FORMAT, level=logging.DEBUG)
# logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger()
logger.info("Application Start")

transcript = load_transcript("../music/bach.mid")
ngram = _SingleInstrumentNGram(2)
ngram.build_from_transcript(transcript)
ngram.sort_and_index()
generator = SingleInstrumentGenerator(ngram, 50, transcript.get_transcript_meta())
generator.generate(transcript.get_instruments()[0])
print ngram
logger.info("Application End")


