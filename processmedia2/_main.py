import json
import argparse
import sys
import fcntl
import os

from calaldees.debug import postmortem
from processmedia_libs.fileset_change_monitor import FilesetChangeMonitor

import logging
import logging.config
log = logging.getLogger(__name__)


DEFAULT_VERSION = '0.0.0'

DEFAULT_DATA_PATH = 'data'
DEFAULT_LOCKFILE = os.path.join(DEFAULT_DATA_PATH, '.lock')
DEFAULT_CONFIG_FILENAME = os.path.join(DEFAULT_DATA_PATH, 'config.json')
DEFAULT_LOGGINGCONF = os.path.join(DEFAULT_DATA_PATH, 'logging.json')
DEFAULT_MTIME_STORE_PATH = os.path.join(DEFAULT_DATA_PATH, 'mtimes.json')
DEFAULT_CMD_FFMPEG = 'nice ffmpeg'


def main(
        name,
        main_function,
        additional_arguments_function=lambda parser: None,
        additional_arguments_processing_function=lambda kwargs: None,
        version=DEFAULT_VERSION,
        description='',
        epilog='',
        folder_type_to_derive_mtime=None,
        lock=True,  # True = Exclusive execution. No other processmedia task can run while exclusive lock is on.
):

    parser = argparse.ArgumentParser(
        prog=name,
        description=description,
        epilog=epilog,
    )
    parser.add_argument('--config', action='store', help='', default=DEFAULT_CONFIG_FILENAME)

    parser.add_argument('--path_source', action='store', help='')
    parser.add_argument('--path_processed', action='store', help='')
    parser.add_argument('--path_meta', action='store', help='')

    parser.add_argument('--force', action='store_true', help='ignore mtime optimisation check')

    parser.add_argument('--loggingconf', action='store', help='logfilename', default=DEFAULT_LOGGINGCONF)
    parser.add_argument('--lockfile', action='store', help='lockfilename, to ensure multiple encoders do not operate at once', default=DEFAULT_LOCKFILE)
    parser.add_argument('--mtime_store_path', action='store', help='optimisation file that tracks the last time processing was done on a folder.', default=DEFAULT_MTIME_STORE_PATH)

    parser.add_argument('--cmd_ffmpeg', action='store', help='cmd for ffmpeg', default=DEFAULT_CMD_FFMPEG)

    parser.add_argument('--postmortem', action='store_true', help='drop into pdb on fail')
    parser.add_argument('--version', action='version', version=version)

    additional_arguments_function(parser)
    kwargs = vars(parser.parse_args())
    additional_arguments_processing_function(kwargs)

    # Overlay config.json defaults
    with open(kwargs['config'], 'rt') as config_filehandle:
        config = json.load(config_filehandle)
        kwargs = {k: v or config.get(k) for k, v in kwargs.items()}

    if lock:
        try:
            lockfile = open(kwargs['lockfile'], 'w')
            fcntl.flock(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            log.warn('Existing process already active. Aborting.')
            sys.exit(0)

    # Setup logging.json
    with open(kwargs['loggingconf'], 'rt') as filehandle:
        logging.config.dictConfig(json.load(filehandle))

    # Optimisation to abort early if files to process have not changed since last time
    if folder_type_to_derive_mtime:
        fileset_monitor = FilesetChangeMonitor(
            mtime_store_path=kwargs['mtime_store_path'],
            path=kwargs[f'path_{folder_type_to_derive_mtime}'],
            name=name,
        )
        if not kwargs.get('force') and not fileset_monitor.has_changed:
            exit_message = f'{folder_type_to_derive_mtime} has not updated since last successful scan. Aborting. use `--force` to bypass this check'
            sys.exit(exit_message)

    # Run main func (maybe with debugging)
    if kwargs.get('postmortem'):
        return_value = postmortem(main_function, **kwargs)
    else:
        return_value = main_function(**kwargs)

    # Record optimisation
    if folder_type_to_derive_mtime and not kwargs.get('force'):
        fileset_monitor.has_changed = True

    main_function.calling_kwargs = kwargs

    if lock:
        lockfile.close()
        os.remove(kwargs['lockfile'])
    return return_value
