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
    """loops through the files list and checks to see
    if there are any new files"""
    for file in only_files:
        filename, file_extension = splitext(file)
        if file_extension == file_ext:
            if file not in files_dict.keys():
                logger.info("new file detected:{}".format(file))
                files_dict[file] = 0
    return files_dict


def dect_removed_files(files_dict, only_files):
    """loops through the files list and checks to see
    if any files have been removed"""
    removed_files = []
    for file in files_dict.keys():
        if file not in only_files:
            logger.info("deleted file detected:{}".format(file))
            removed_files.append(file)
    for file in removed_files:
        del files_dict[file]
    return files_dict


def read_files(file_path, line_num, text, files_dict, file):
    """ This function reads individual file and 
    looks for peculiar text within file"""
    current_line = 1
    with open(file_path) as f:
        for line in f:
            if current_line >= line_num:
                if text in line:
                    logger.info(
                        'peculiar text found in file {0} at line number {1}'
                        .format(file, current_line)
                    )
            current_line +=1
    files_dict[file] = current_line
    return files_dict


def watch_dict(files_dict, watch_dir, file_ext, search_text):
    """Function gets ran based on polling interval, builds list
    of current files and passes them along to add and delete detections"""
    try:
        only_files = [f for f in listdir(watch_dir)
                      if isfile(join(watch_dir, f))]
    except OSError as err:
        logger.error(err)
    else:
        try:
            files_dict = dect_added_files(files_dict, only_files, file_ext)
            files_dict = dect_removed_files(files_dict, only_files)
        except Exception as e:
            logger.exception(e)
        for k, v in files_dict.items():
            try:
                filename, file_extension = splitext(k)
            except Exception as e:
                logger.exception(e)
            else:
                file = join(watch_dir, k)
                if file_ext == file_extension:
                    try:
                        files_dict = read_files(
                            file, v, search_text, files_dict, k
                        )
                    except Exception as e:
                        logger.exception(e)
    finally:
        return files_dict


def create_parser():
    """ Creates parser to add command line arguments"""
    parser = argparse.ArgumentParser(
        description='watches a directory for files that contain search text'
    )
    parser.add_argument(
        '-p', '--pollint', help='interval which directory is scanned',
         default=1, type=int
    )
    parser.add_argument(
        '-st', '--searchText', help='text that will be searched'
    )
    parser.add_argument(
        '-ext', '--fileExt', help='extension of files to search'
    )
    parser.add_argument(
        '-wd', '--watchDir', help='directory to watch'
    )
    return parser


def calc_run_time(start_time, end_time):
    """function that calculates running time"""
    total_time = end_time - start_time
    days = total_time // 86400
    hours = total_time // 3600 % 24
    minutes = total_time // 60 % 60
    seconds = total_time % 60
    result = '{0} days, {1} hours, {2} mins and {3} secs'.format(
        days, hours, minutes, seconds
    )
    return result


def main(args):
    """Used to initialize program and start watch directory"""
    global exit_flag
    start_time = time.time()
    logger.info('{0} dirwatcher.py started {1}'.format(
        banner_text, banner_text
    ))
    files_dict = defaultdict(list)
    try:
        parser = create_parser()
        ns = parser.parse_args(args)
    except Exception as e:
        logger.exception(e)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    if not ns:
        logger.exception('arguments not passed correctly')
    magic_text = ns.searchText
    polling_interval = ns.pollint
    file_ext = ns.fileExt
    watch_dir = ns.watchDir
    while not exit_flag:
        try:
            files_dict = watch_dict(
                files_dict, watch_dir, file_ext, magic_text
            )
        except Exception as e:
            logger.exception(e)
            exit_flag = True
        finally:
            time.sleep(polling_interval)
    end_time = time.time()
    run_time = calc_run_time(start_time, end_time)
    logger.info('{0} dirwatcher.py stopped \n runningtime {1}{2}'
                .format(banner_text, run_time, banner_text))


if __name__ == '__main__':
    main(sys.argv[1:])


    