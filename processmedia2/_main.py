import json
import argparse
import sys
import fcntl

from libs.misc import postmortem
from processmedia_libs.fileset_change_monitor import FilesetChangeMonitor

import logging
import logging.config
log = logging.getLogger(__name__)


DEFAULT_VERSION = '0.0.0'

DEFAULT_LOCKFILE = '.lock'
DEFAULT_CONFIG_FILENAME = 'config.json'
DEFAULT_LOGGINGCONF = 'logging.json'


def main(
        name,
        main_function,
        additional_arguments_function=lambda parser: None,
        additional_arguments_processing_function=lambda kwargs: None,
        version=DEFAULT_VERSION,
        description='',
        epilog='',
        mtime_path=None,
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
    parser.add_argument('--pdb', action='store_true', help='drop into pdb on fail')
    parser.add_argument('--loggingconf', action='store', help='logfilename', default=DEFAULT_LOGGINGCONF)
    parser.add_argument('--lockfile', action='store', help='lockfilename, to ensure multiple encoders do not operate at once', default=DEFAULT_LOCKFILE)
    parser.add_argument('--version', action='version', version=version)

    additional_arguments_function(parser)
    kwargs = vars(parser.parse_args())
    additional_arguments_processing_function(kwargs)

    try:
        lockfile = open(kwargs['lockfile'], 'w')
        fcntl.flock(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        log.warn('Existing process already active. Aborting.')
        sys.exit(0)

    # Overlay config.json defaults
    with open(kwargs['config'], 'rt') as config_filehandle:
        config = json.load(config_filehandle)
        kwargs = {k: v or config.get(k) for k, v in kwargs.items()}

    # Setup logging.json
    with open(kwargs['loggingconf'], 'rt') as filehandle:
        logging.config.dictConfig(json.load(filehandle))

    # Optimisation to abort early if files to process have not chnaged since last time
    if mtime_path:
        fileset_monitor = FilesetChangeMonitor(path=kwargs['path_{}'.format(mtime_path)], name=name)
        if not kwargs.get('force') and not fileset_monitor.has_changed:
            exit_message = "{} has not updated since last successful scan. Aborting. use `--force` to bypass this check".format(mtime_path)
            log.warn(exit_message)
            sys.exit(exit_message)

    # Run main func (maybe with debugging)
    if kwargs.get('pdb'):
        return_value = postmortem(main_function, **kwargs)
    else:
        return_value = main_function(**kwargs)

    # Record optimisation
    if mtime_path and not kwargs.get('force'):
        fileset_monitor.has_changed = True

    main_function.calling_kwargs = kwargs

    lockfile.close()
    return return_value
