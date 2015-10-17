from collections import ChainMap
import subprocess

from libs.misc import cmd_args

import logging
log = logging.getLogger(__name__)


CONFIG = {
    'threads': 1,
    'audio_rate_khz': 44000,
    'process_timeout_seconds': 30 * 60,
}


def check_tools():
    """
    Assert exteranl dependeycs
    """
    pass


def _run_tool(*args, **kwargs):
    return subprocess.run(cmd_args(*args, **kwargs), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=CONFIG['process_timeout_seconds'])


def encode_video(source, destination, **kwargs):
    defaults = dict(
        quiet=None,
        ass=None,
        nosound=None,
        ovc='x264',
        #aspect=
        x264encopts='profile=main:preset=slow:threads=%s' % CONFIG['threads'],
    )
    kwargs['o'] = destination
    if 'sub' in kwargs and kwargs['sub'] == None:
        del kwargs['sub']
    return _run_tool('mencoder', source, **ChainMap(defaults, kwargs))


def encode_audio(source, destination, **kwargs):
    """
        # 4.) Decompress audio
        # 5.) Normalize audio volume
        # 6.) Offset audio
    """
    pass
