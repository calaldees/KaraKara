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
        'h264_codec': 'h264',  # 'libx264'
        'scale': "scale=w='320:h=-1'",  # scale=w='min(500, iw*3/2):h=-1'
    }
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
    log.info('encode_video - %s', source)
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
            #aspect=
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
        destination,
    )


def encode_preview_video(source, destination):
    log.info('encode_preview_video - %s', source)
    return _run_tool(
        *AVCONV_COMMON_ARGS,
        '-i', source,
        *cmd_args(
            strict='experimental',
            vcodec=CONFIG['avconv']['h264_codec'],
            b='150k',
            bt='240k',
            acodec='aac',
            ac=1,
            ar=CONFIG['audio_rate_khz'],
            ab='48k',
            vf=CONFIG['avconv']['scale'],
        ),
        destination,
    )


def extract_images(source, destination_path, num_images=4):
    log.info('extract_images')
    video_duration = probe_media(source).get('duration')
    if not video_duration:
        log.warn('unable to assertain video duration; unable to extact images')
        return
    times = (float("%.3f" % (video_duration * offset)) for offset in (x/(num_images+1) for x in range(1, num_images)))
    for index, time in enumerate(times):
        destination = os.path.join(destination_path, '{}.jpg'.format(index))
        encode_success, cmd_result = _run_tool(
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
        if encode_success:
            yield destination
