import logging

__author__ = 'Adisor'


def clear_log_file(logfile):
    with open(logfile, 'w'):
        pass


logfile = 'log.log'
FORMAT = '%(asctime)-12s %(message)s'
logging.basicConfig(filename=logfile, format=FORMAT, level=logging.DEBUG)
clear_log_file(logfile)
logger = logging.getLogger()
