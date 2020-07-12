__author__ = "ruthmayodi with the help of Nikal Morgan"
import logging
import sys
import signal
import time
import argparse
import os
import errno
logger = logging.getLogger(__name__)
watched_files = {}
exit_flag = False


def read_file(path, start_line, search_text):
    """ This function reads individual file and 
    looks for searched text within file"""
    line_number = 0
    with open(path) as f:
        for line_number, line in enumerate(f):
            if line_number >= start_line:
                if search_text in line:
                    logger.info(
                        f"Match found for {search_text} "
                        f"found on line {line_number+1} in {path}"
                                )
    return line_number + 1


def watch_dir(args):
    """Function gets ran based on args, builds list
    of current files and passes them along to add,delete and read detections"""
    file_list = os.listdir(args.watchDir)
    detect_added_files(file_list, args.fileExt)
    detect_removed_files(file_list)
    for f in watched_files:
        path = os.path.join(args.watchDir, f)
        watched_files[f] = read_file(
            path,
            watched_files[f],
            args.search_text
        )
    return watched_files


def detect_added_files(file_list, ext):
    """loops through the files list and checks to see
    if there are any new files"""
    global watched_files
    for f in file_list:
        if f.endswith(ext) and f not in watched_files:
            watched_files[f] = 0
            logger.info(f"{f} added to watchlist.")
    return file_list


def detect_removed_files(file_list):
    """Checks the directory if a given file was deleted"""
    global watched_files
    for f in list(watched_files):
        if f not in file_list:
            logger.info(f"{f} removed from watchlist.")
            del watched_files[f]
    return file_list


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT.
    Other signals can be mapped here as well (SIGHUP?)
    Basically, it just sets a global flag, and main() will exit its loop
    if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    # log the associated signal name
    global exit_flag
    logger.warning('Received ' + signal.Signals(sig_num).name)
    exit_flag = True


def create_parser():
    """Create an argument parser object"""
    parser = argparse.ArgumentParser(
        description="Watches a directory of text files for a magic string"
    )
    parser.add_argument('watchDir', help='directory to watch')
    parser.add_argument('search_text', help='text that will be searched')
    parser.add_argument('-p',
                        '--pollint',
                        help='interval which directory is scanned',
                        type=float,
                        default=1.0)
    parser.add_argument( '-ext', '--fileExt', help='extension of files to search',
                        type=str,
                        default='.txt')
    return parser


def main(args):
    """Used to initialize program and start watch directory"""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    polling_interval = parsed_args.pollint
    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(name)-12s '
               '%(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d &%H:%M:%S'
    )
    logger.setLevel(logging.DEBUG)
    start_time = time.time()
    logger.info(
        '\n'
        '-------------------------------------------------\n'
        f'   Running {__file__}\n'
        f'   Started on {start_time:.1f}\n'
        '-------------------------------------------------\n'
    )
    
    # Hook into these two signals from the OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    while not exit_flag:
        try:
            watch_dir(parsed_args)
        except OSError as e:
            if e.errno == errno.ENOENT:
                logger.error(f"{parsed_args.watchDir} directory not found")
                time.sleep(2)
            else:
                logger.error(e)
        except Exception as e:
            logger.error(f"UNHANDLED EXCEPTION:{e}")
        time.sleep(polling_interval)
    full_time = time.time() - start_time
    logger.info(
        '\n'
        '-------------------------------------------------\n'
        f'   Stopped {__file__}\n'
        f'   Uptime was {full_time:.1f}\n'
        '-------------------------------------------------\n'
    )
    logging.shutdown()


if __name__ == "__main__":
    """Runs the main loop until an interrupt like control+c are input."""
    main(sys.argv[1:])
