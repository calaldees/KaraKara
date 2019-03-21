import json
import argparse
import sys
import fcntl
import os
from pathlib import Path

from calaldees.debug import postmortem
from calaldees.environ import get_env
from calaldees.data import merge_dicts
from processmedia_libs.fileset_change_monitor import FilesetChangeMonitor

import logging
import logging.config
log = logging.getLogger(__name__)


DEFAULT_VERSION = '0.0.0'

DEFAULT_DATA_PATH = 'data'
DEFAULT_kwargs = {
    'config': os.path.join(DEFAULT_DATA_PATH, 'config.json'),
    'lockfile': os.path.join(DEFAULT_DATA_PATH, '.lock'),
    'loggingconf': os.path.join(DEFAULT_DATA_PATH, 'logging.json'),
    'mtime_store_path': os.path.join(DEFAULT_DATA_PATH, 'mtimes.json'),
    'heartbeat_file': os.path.join(DEFAULT_DATA_PATH, '.heartbeat'),
    'cmd_ffmpeg': 'nice ffmpeg',
}


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
    parser.add_argument('--config', action='store', help=f" default:{DEFAULT_kwargs['config']}")

    parser.add_argument('--path_source', action='store', help='')
    parser.add_argument('--path_processed', action='store', help='')
    parser.add_argument('--path_meta', action='store', help='')

    parser.add_argument('--force', action='store_true', help='ignore mtime optimisation check')

    parser.add_argument('--loggingconf', action='store', help=f" default:{DEFAULT_kwargs['loggingconf']}")
    parser.add_argument('--lockfile', action='store', help=f"lockfilename, to ensure multiple encoders do not operate at once. default:{DEFAULT_kwargs['lockfile']}")
    parser.add_argument('--mtime_store_path', action='store', help=f"optimisation file that tracks the last time processing was done on a folder. default:{DEFAULT_kwargs['mtime_store_path']}")
    parser.add_argument('--heartbeat_file', action='store', help=f"touch this file on each action default:{DEFAULT_kwargs['heartbeat_file']}")

    # TODO: is this needed? It was a consideration for containerisation, but the container has the relevant binaries now
    parser.add_argument('--cmd_ffmpeg', action='store', help=f"cmd for ffmpegdefault:{DEFAULT_kwargs['cmd_ffmpeg']}")

    parser.add_argument('--postmortem', action='store_true', help='drop into pdb on fail')
    parser.add_argument('--version', action='version', version=version)

    additional_arguments_function(parser)
    kwargs_cmd = vars(parser.parse_args())

    # Read config.json values
    config = {}
    if kwargs_cmd.get('config') and not os.path.isfile(kwargs_cmd['config']):
        raise Exception(f"config file does not exist {kwargs_cmd['config']}")
    config_filename = kwargs_cmd.get('config', DEFAULT_kwargs['config'])
    if os.path.isfile(config_filename):
        with open(config_filename, 'rt') as config_filehandle:
            config = json.load(config_filehandle)
            #kwargs = {k: v or config.get(k) for k, v in kwargs.items()}

    # Merge kwargs in order of precidence
    kwargs = merge_dicts(DEFAULT_kwargs, config, kwargs_cmd)

    # Format all strings with string formatter/replacer - this overlays ENV variables too
    #kwargs_templates = {k: v for k, v in kwargs.items() if v != None}
    for k in kwargs.keys():
        if isinstance(kwargs[k], str):
            kwargs[k] = kwargs[k].format(**os.environ, **kwargs)

    # Process str values into other data types
    additional_arguments_processing_function(kwargs)

    lockfile = None
    if lock:
        try:
            lockfile = open(kwargs['lockfile'], 'w')
            fcntl.flock(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            log.warning('Existing process already active. Aborting.')
            sys.exit(0)

    # Setup logging.json
    with open(kwargs['loggingconf'], 'rt') as filehandle:
        logging.config.dictConfig(json.load(filehandle))

    # Heartbeat
    if kwargs['heartbeat_file']:
        Path(kwargs['heartbeat_file']).touch()

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

    if lockfile:
        lockfile.close()
        os.remove(kwargs['lockfile'])
    return return_value
