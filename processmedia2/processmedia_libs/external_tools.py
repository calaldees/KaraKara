import re
import os.path
import subprocess
from collections import ChainMap, namedtuple

from dateutil import parser as dateparse

from libs.misc import cmd_args

import logging
log = logging.getLogger(__name__)


CONFIG = {
    'threads': 2,
    'audio_rate_khz': 44100,
    'process_timeout_seconds': 30 * 60,
    'log_level': 'warning',
    'avconv': {
        'h264_codec': 'libx264',  # 'h264',
        # The width and height must be divisable by 2
        # Using w=320:h-1 should auto set the height preserving aspect ratio
        # Sometimes using this method the height is an odd number, which fails to encode
        # From the avconv documentation we have some mathmatical functions and variables
        # 'a' is the aspect ratio. floor() rounds down to nearest integer
        # If we divide by 2 and ensure that an integer, timesing by 2 must be divisable by 2
        'scale': "scale=w='{0}:h=floor(({0}*(1/a))/2)*2'".format(320),  # scale=w='min(500, iw*3/2):h=-1'
        'preview_crf': 30,  # 0=lossless - 51=shit - default=23 - http://slhck.info/articles/crf
        'preview_audio_bitrate': '32k',
    },
}


AVCONV_COMMON_ARGS = cmd_args(
    'avconv',
    threads=CONFIG['threads'],
    loglevel=CONFIG['log_level'],
    y=None,
    # strict='experimental',
)


def check_tools():
    """
    Assert exteranl dependeycs
    """
    # check (h264 or libx264):
    pass


CommandResult = namedtuple('CommandResult', ('success', 'result'))
def _run_tool(*args, **kwargs):
    cmd = cmd_args(*args, **kwargs)
    log.debug(cmd)
    cmd_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=CONFIG['process_timeout_seconds'])
    if cmd_result.returncode != 0:
        log.error(cmd_result)
    return CommandResult(cmd_result.returncode == 0, cmd_result)


def probe_media(source):
    cmd_success, cmd_result = _run_tool(
        'avprobe',
        source
    )
    result = (cmd_result.stdout + cmd_result.stderr).decode('utf-8')
    data = {}
    try:
        raw_duration = re.search(r'Duration: (\d+):(\d+):(\d+)\.(\d+)', result)
        hours = float(raw_duration.group(1)) * 60.0 * 60.0
        minutes = float(raw_duration.group(2)) * 60.0
        seconds = float(raw_duration.group(3))
        fraction = raw_duration.group(4)
        fraction = float(fraction) / (10**(len(fraction)))
        data['duration'] = hours + minutes + seconds + fraction
    except:
        pass
    return data


def encode_video(source, sub, destination):
    log.info('encode_video - %s - %s -%s', source, sub, destination)
    sub_args = cmd_args(sub=sub) if sub else ()
    return _run_tool(
        'mencoder',
        source,
        *sub_args,
        *cmd_args(
            quiet=None,
            ass=None,
            nosound=None,
            ovc='x264',
            x264encopts='profile=main:preset=slow:threads=%s' % CONFIG['threads'],
        ),
        '-o', destination,
    )


def encode_audio(source, destination, **kwargs):
    """
        Decompress audio
        Normalize audio volume
        Offset audio
    """
    log.info('encode_audio - %s - %s', source, destination)

    path = os.path.dirname(destination)

    cmds = (
        lambda: _run_tool(
            *AVCONV_COMMON_ARGS,
            '-i', source,
            *cmd_args(
                strict='experimental',
                vcodec='none',
                ac=2,
                ar=CONFIG['audio_rate_khz'],
            ),
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
    log.info('mux - %s - %s - %s', video, audio, destination)
    return _run_tool(
        *AVCONV_COMMON_ARGS,
        '-i', video,
        '-i', audio,
        *cmd_args(
            strict='experimental',
            vcodec='copy',
            ab='224k',
        ),
        destination,
    )


def encode_preview_video(source, destination):
    log.info('encode_preview_video - %s - %s', source, destination)
    return _run_tool(
        *AVCONV_COMMON_ARGS,
        '-i', source,
        *cmd_args(
            strict='experimental',
            vcodec=CONFIG['avconv']['h264_codec'],
            crf=CONFIG['avconv']['preview_crf'],
            acodec='aac',
            ac=1,
            ar=CONFIG['audio_rate_khz'],
            ab=CONFIG['avconv']['preview_audio_bitrate'],
            vf=CONFIG['avconv']['scale'],
        ),
        destination,
    )


def extract_image(source, destination, time=0.2):
    log.info('extract_image - %s - %s', source, destination)
    return _run_tool(
        *AVCONV_COMMON_ARGS,
        '-i', source,
        *cmd_args(
            ss=str(time),
            vframes=1,
            an=None,
            vf=CONFIG['avconv']['scale'],
        ),
        destination,
    )
