import os.path
from collections import ChainMap
import subprocess

from libs.misc import cmd_args

import logging
log = logging.getLogger(__name__)


CONFIG = {
    'threads': 1,
    'audio_rate_khz': 44000,
    'process_timeout_seconds': 30 * 60,
    'log_level': 'warning',
}


AVCONV_COMMON_ARGS = cmd_args(
    'avconv',
    threads=CONFIG['threads'],
    loglevel=CONFIG['log_level'],
    y=None,
)



def check_tools():
    """
    Assert exteranl dependeycs
    """
    pass


def _run_tool(*args, **kwargs):
    cmd = cmd_args(*args, **kwargs)
    log.debug(cmd)
    cmd_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=CONFIG['process_timeout_seconds'])
    if cmd_result.returncode != 0:
        log.error(cmd_result)
    return cmd_result.returncode == 0, cmd_result


def encode_video(source, sub, destination):
    log.info('encode_video - %s', source)
    output_args = cmd_args(
        quiet=None,
        ass=None,
        nosound=None,
        ovc='x264',
        #aspect=
        x264encopts='profile=main:preset=slow:threads=%s' % CONFIG['threads'],
    )
    sub_args = cmd_args(sub=sub) if sub else ()
    return _run_tool(
        'mencoder',
        source,
        *sub_args,
        *output_args,
        '-o', destination,
    )


def encode_audio(source, destination, **kwargs):
    """
        Decompress audio
        Normalize audio volume
        Offset audio
    """
    log.info('encode_audio - %s', source)

    path = os.path.dirname(destination)
    avconv_output_args = cmd_args(
        vcodec='none',
        strict='experimental',
        ac=2,
        ar=CONFIG['audio_rate_khz'],
    )

    cmds = (
        lambda: _run_tool(
            *AVCONV_COMMON_ARGS,
            '-i', source,
            *avconv_output_args,
            os.path.join(path, 'audio_raw.wav'),
        ),
        lambda: _run_tool(
            'sox',
            os.path.join(path, 'audio_raw.wav'),
            #os.path.join(path, 'audio_norm.wav'),
            destination,
            'fade', 'l', '0.15', '0', '0.15',
            'norm',
        ),
        # TODO: Cut and offset
    )

    for cmd in cmds:
        cmd_success, cmd_result = cmd()
        if not cmd_success:
            return False, cmd_result
    return True, None


def mux(video, audio, destination):
    """
    """
    log.info('mux - %s - %s', video, audio)
    return _run_tool(
        *AVCONV_COMMON_ARGS,
        '-i', video,
        '-i', audio,
        *cmd_args(
            strict='experimental',
            vcodec='copy',
            ab='224k',
        ),
        destination
    )