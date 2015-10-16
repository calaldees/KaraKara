from collections import ChainMap
import subprocess

from libs.misc import cmd_args

HALF_HOUR_IN_SECONDS = 30 * 60

avconv_threads = 1


def check_tools():
    """
    Assert exteranl dependeycs
    """
    pass


def _run_tool(*args, **kwargs):
    return subprocess.run(cmd_args(*args, **kwargs), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=HALF_HOUR_IN_SECONDS)


def encode_video(source, destination, **kwargs):
    defaults = dict(
        quiet=None,
        ass=None,
        nosound=None,
        ovc='x264',
        #aspect=
        x264encopts='profile=main:preset=slow:threads=%s' % avconv_threads,
    )
    kwargs['o'] = destination
    return _run_tool('mencoder', source, **ChainMap(defaults, kwargs))
