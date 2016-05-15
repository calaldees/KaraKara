import json

import logging
log = logging.getLogger(__name__)

EXTS = dict(
    video=('rm', 'mpg', 'avi', 'mkv', 'ogm', 'mp4'),
    audio=('mp2', 'mp3', 'ogg', 'flac'),
    image=('jpg', 'png'),
    sub=('ssa', 'srt'),
    data=('yml', 'yaml'),
    tag=('txt', )
)
ALL_EXTS = tuple(j for i in EXTS.values() for j in i)

DEFAULT_VERSION = '0.0.0'

PENDING_ACTION = dict(
    encode='encode',
)

DEFAULT_CONFIG_FILENAME = 'config.json'


def add_default_argparse_args(parser, version=DEFAULT_VERSION):
    parser.add_argument('--config', action='store', help='', default=DEFAULT_CONFIG_FILENAME)

    parser.add_argument('--path_source', action='store', help='')
    parser.add_argument('--path_processed', action='store', help='')
    parser.add_argument('--path_meta', action='store', help='')

    parser.add_argument('--debug_on_fail', action='store_true', help='drop into pdb on encode fail')
    parser.add_argument('--log_level', type=int, help='log level')
    parser.add_argument('--version', action='version', version=version)


def parse_args(parser):
    return apply_config(vars(parser.parse_args()))


def apply_config(args_dict):
    with open(args_dict['config'], 'r') as config_filehandle:
        config = json.load(config_filehandle)
        return {k: v or config.get(k) for k, v in args_dict.items()}
