import logging

__author__ = 'Adisor'

"""
This file is used to configure logging and to give the configured logging object to the rest of the application
"""


def clear_log_file(logfile):
    with open(logfile, 'w'):
        pass


logfile = 'log.log'
FORMAT = '%(asctime)-12s %(message)s'
logging.basicConfig(filename=logfile, format=FORMAT, level=logging.DEBUG)
clear_log_file(logfile)
logger = logging.getLogger()
