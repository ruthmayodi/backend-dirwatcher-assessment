__author__ = "ruthmayodi, with the help of Howard Post"
import logging 
import time
import signal
import argparse
import sys

from os import listdir
from os.path import isfile, join, splitext
from collections import defaultdict

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s:%(funcName)s:%(levelname)s:%(message)s'
)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# global variables
exit_flag = False
banner_text = '\n' + '-' * 30 + '\n'


def signal_handler(sig_num, frame):
    """handler for system signals"""
    global exit_flag
    logger.warning('Received ' + signal.Signals(sig_num).name)
    exit_flag = True


def dect_added_files(files_dict, only_files, file_ext):
    """lopps through the files list and checks to see
    if there are any new files"""
    for file in only_files:
        filename, file_extension = splitext(file)
        if file_extension == file_ext:
            if file not in 