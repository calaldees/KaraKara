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
DEFAULT_PATH_SOURCE = '../mediaserver/www/files/'
DEFAULT_PATH_PROCESSED = '../mediaserver/www/processed/'
DEFAULT_PATH_META = '../mediaserver/www/meta/'

PENDING_ACTION = dict(
    encode='encode',
)


def add_default_argparse_args(parser, version=DEFAULT_VERSION):
    parser.add_argument('--path_source', action='store', help='', default=DEFAULT_PATH_SOURCE)
    parser.add_argument('--path_processed', action='store', help='', default=DEFAULT_PATH_PROCESSED)
    parser.add_argument('--path_meta', action='store', help='', default=DEFAULT_PATH_META)

    parser.add_argument('--log_level', type=int, help='log level', default=logging.INFO)
    parser.add_argument('--version', action='version', version=version)
