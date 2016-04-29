import logging
log = logging.getLogger(__name__)

import math
import re
import os.path
import json
import subprocess  # TODO: depricated
from collections import ChainMap, namedtuple
import subprocess
from io import BytesIO

from dateutil import parser as dateparse
try:
    from PIL import Image
except ImportError:
    Image = None
    log.error('Unable to import PIL (Python image library) - try installing Pillow')

from libs.misc import cmd_args, color_close


CRFFactorItem = namedtuple('CRFFactorItem', ['crf', 'pixels'])
CRFFactor = namedtuple('CRFFactor', ['lower', 'upper'])

CONFIG = {
    'threads': 2,
    'process_timeout_seconds': 30 * 60,
    'log_level': 'warning',
    'h264_codec': 'libx264',  # 'libx264',  # 'h264',
    'preview_width': 320,
    'scale_even': 'scale=w=floor(iw/2)*2:h=floor(ih/2)*2',  # 264 codec can only handle dimension a multiple of 2. Some input does not adhear to this and need correction.
    'crf_factor': CRFFactor(CRFFactorItem(35, int(math.sqrt(320*240))), CRFFactorItem(45, int(math.sqrt(1280*720)))),
}
CONFIG.update({
    'encode_image_to_video': {
        'vcodec': CONFIG['h264_codec'],
        'r': 5,  # 5 fps
        'bf': 0,  # wha dis do?
        'qmax': 1,  # wha dis do?
        'vf': CONFIG['scale_even'],  # .format(width=width, height=height),  # ,pad={TODO}:{TODO}:(ow-iw)/2:(oh-ih)/2,setsar=1:1
    },
    'extract_audio': {
        'vcodec': 'none',
        'ac': 2,
        'ar': 44100,
    },
    'encode_video': {
        # preset='slow',
        'vcodec': CONFIG['h264_codec'],
        'crf': 21,
        'maxrate': '1500k',
        'bufsize': '2500k',

        'acodec': 'aac',
        'strict': 'experimental',
        'ab': '196k',
    },
    'encode_preview': {
        'vcodec': CONFIG['h264_codec'],
        'crf': 34,
        'vf': "scale=w='{0}:h=floor(({0}*(1/a))/2)*2'".format(CONFIG['preview_width']),  # scale=w='min(500, iw*3/2):h=-1'

        'acodec': 'aac',  # libfdk_aac
        'strict': 'experimental',
        'ab': '48k',
        #'profile:a': 'aac_he_v1',
        #ac=1,
    },

    # The width and height must be divisable by 2
    # Using w=320:h-1 should auto set the height preserving aspect ratio
    # Sometimes using this method the height is an odd number, which fails to encode
    # From the avconv documentation we have some mathmatical functions and variables
    # 'a' is the aspect ratio. floor() rounds down to nearest integer
    # If we divide by 2 and ensure that an integer, multiplying by 2 must be divisable by 2
})


ENCODE_VIDEO_COMMON_ARGS = cmd_args(
    'ffmpeg',
    threads=CONFIG['threads'],
    loglevel=CONFIG['log_level'],
    y=None,
)


def check_tools():
    """
    Assert exteranl dependeycs
    """
    # check ffmpeg (with dependencys)
    # check sox
    # check jpegoptim
    # check (h264 or libx264)?
    pass


CommandResult = namedtuple('CommandResult', ('success', 'result'))
def _run_tool(*args, **kwargs):
    cmd = cmd_args(*args, **kwargs)
    log.debug(cmd)
    cmd_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=CONFIG['process_timeout_seconds'])
    if cmd_result.returncode != 0:
        log.error(cmd_result)
    return CommandResult(cmd_result.returncode == 0, cmd_result)


def crf_from_res(width=320, height=240, crf=CONFIG['crf_factor'], **kwargs):
    """
    Attempt to keep the same (rough) filesize regardless of resolution.

    0=lossless - 51=shit - default=23 - http://slhck.info/articles/crf

    >>> crf_from_res(320, 200)
    34
    >>> crf_from_res(1280, 720)
    45
    """
    factor = (math.sqrt(width*height) - crf.lower.pixels) / (crf.upper.pixels - crf.lower.pixels)
    return int(((crf.upper.crf - crf.lower.crf) * factor) + crf.lower.crf)


def probe_media(source):
    """
    Todo: update for audio and images

    >>> json.dumps(probe_media('tests/source/test1.mp4'), sort_keys=True)
    '{"audio": {"bitrate": "2", "format": "aac", "sample_rate": "44100"}, "duration": 30.02, "height": 480, "width": 640}'

    """
    if not source:
        return {}
    cmd_success, cmd_result = _run_tool(
        'ffprobe',
        source
    )
    result = (cmd_result.stdout + cmd_result.stderr).decode('utf-8', 'ignore')
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
    try:
        raw_res = re.search(r'Video:.*?(\d{3,4})x(\d{3,4}).*?', result)
        data['width'] = int(raw_res.group(1))
        data['height'] = int(raw_res.group(2))
    except:
        pass
    try:
        raw_audio = re.search(r'Audio:\s*(?P<format>\w+?)[\s,].*, (?P<sample_rate>\d+) Hz,.*, (?P<bitrate>\d+) kb', result)
        data['audio'] = raw_audio.groupdict()
    except:
        pass
    return data


def encode_image_to_video(source, destination, duration=10, width=320, height=240, **kwargs):
    """
    Todo: use same codec as encode_video
    """
    log.debug('encode_image_to_video - %s', os.path.basename(source))
    _run_tool(
        *ENCODE_VIDEO_COMMON_ARGS,
        '-loop', '1',
        '-i', source,
        *cmd_args(
            t=duration,
            **CONFIG['encode_image_to_video'],
        ),
        destination,
    )


def encode_video(video_source, audio_source, subtitle_source, destination):
    log.debug('encode_video - %s', os.path.basename(video_source))

    filters = [CONFIG['scale_even']]
    if subtitle_source:
        filters.append('subtitles={}'.format(subtitle_source))

    return _run_tool(
        *ENCODE_VIDEO_COMMON_ARGS,
        '-i', video_source,
        '-i', audio_source,
        *cmd_args(
            vf=', '.join(filters),
            **CONFIG['encode_video'],
        ),
        destination,
    )


def encode_audio(source, destination, **kwargs):
    """
        Decompress audio
        Normalize audio volume
        Offset audio
    """
    log.debug('encode_audio - %s', os.path.basename(source))

    path = os.path.dirname(destination)

    cmds = (
        lambda: _run_tool(
            *ENCODE_VIDEO_COMMON_ARGS,
            '-i', source,
            *cmd_args(
                **CONFIG['extract_audio']
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


def encode_preview_video(source, destination):
    """
    https://trac.ffmpeg.org/wiki/Encode/AAC#HE-AACversion2
    """
    log.debug('encode_preview_video - %s', os.path.basename(source))

    #crf = crf_from_res(**probe_media(source))
    #log.debug('crf: %s', crf)

    return _run_tool(
        *ENCODE_VIDEO_COMMON_ARGS,
        '-i', source,
        *cmd_args(
            **CONFIG['encode_preview']
        ),
        destination,
    )


def extract_image(source, destination, time=0.2):
    log.debug('extract_image - %s', os.path.basename(source))

    cmds = (
        lambda: _run_tool(
            *ENCODE_VIDEO_COMMON_ARGS,
            '-i', source,
            *cmd_args(
                ss=str(time),
                vframes=1,
                an=None,
                vf=CONFIG['encode_preview']['vf'],
            ),
            destination,
        ),
        lambda: (os.path.exists(destination), 'expected destiantion image file was not generated (video source may be damaged) {0}'.format(source)),
        lambda: _run_tool(
            'jpegoptim',
            #'--size={}'.format(CONFIG['jpegoptim']['target_size_k']),
            '--strip-all',
            '--overwrite',
            destination,
        ),
    )

    for cmd in cmds:
        cmd_success, cmd_result = cmd()
        if not cmd_success:
            return False, cmd_result
    return True, None


def get_frame_from_video(url, time="00:00:10"):
    """
    FFMpeg | pipe stdout -> PIL.Image (from stringbuffer)

    time string format - hh:mm:ss[.xxx]

    Gets Image progressivly - Largers times read linearly from the beggining of the file

    >>> color_close((255, 0, 0), get_frame_from_video('tests/source/test1.mp4', 0).getpixel((0,0)))
    True
    >>> color_close((0, 255, 0), get_frame_from_video('tests/source/test1.mp4', '10').getpixel((0,0)))
    True
    >>> color_close((0, 0, 255), get_frame_from_video('tests/source/test1.mp4', '00:00:20').getpixel((0,0)))
    True
    """
    cmd = """ffmpeg -loglevel quiet -i "{url}" -ss {time} -vframes 1 -f image2 pipe: """.format(url=url, time=time)
    return Image.open(BytesIO(subprocess.check_output(cmd, stderr=subprocess.PIPE, shell=True)))
