import logging
log = logging.getLogger(__name__)

import math
import re
import os.path
import json
from collections import namedtuple
import subprocess
from functools import partial

from calaldees.shell import cmd_args
cmd_args = partial(cmd_args, FLAG_PREFIX='-')


# Experiments for ConstantRateFactor for videos
# This is largely an unused experiment but was interesting working through the problem and could be useful documentation for later
CRFFactorItem = namedtuple('CRFFactorItem', ['crf', 'pixels'])
CRFFactor = namedtuple('CRFFactor', ['lower', 'upper'])
DEFAULT_CRF_FACTOR = CRFFactor(CRFFactorItem(35, int(math.sqrt(320*240))), CRFFactorItem(45, int(math.sqrt(1280*720))))
def crf_from_res(width=320, height=240, crf=DEFAULT_CRF_FACTOR, **kwargs):
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


def parser_cmd_to_tuple(cmd):
    return tuple(filter(None, cmd.split(' ')))


class ProcessMediaFilesWithExternalTools:
    def __init__(self, **config):
        """

        The width and height must be divisible by 2
        Using w=320:h-1 should auto set the height preserving aspect ratio
        Sometimes using this method the height is an odd number, which fails to encode
        From the avconv documentation we have some mathematical functions and variables
        'a' is the aspect ratio. floor() rounds down to nearest integer
        If we divide by 2 and ensure that an integer, multiplying by 2 must be divisible by 2
        """
        self.config = {
            **{
                'threads': 2,
                'process_timeout_seconds': 60 * 30,  # There are some HUGE videos ... this timeout should be dramatically reduced when we've cleared out the crud
                'log_level': 'warning',
                'h264_codec': 'libx264',  # 'libx264',  # 'h264',
                'preview_width': 320,
                'scale_even': 'scale=w=floor(iw/2)*2:h=floor(ih/2)*2',  # 264 codec can only handle dimension a multiple of 2. Some input does not adhere to this and need correction.
                'crf_factor': DEFAULT_CRF_FACTOR,
                'cmd_ffmpeg': ('nice', 'ffmpeg'),
                'cmd_ffprobe': ('ffprobe', ),
                'cmd_jpegoptim': ('jpegoptim', ),
                'cmd_sox': ('sox', ),
            },
            **config,
        }
        # parse cmd_xxx into tuples
        for key in ('cmd_ffmpeg', 'cmd_ffprobe', 'cmd_jpegoptim', 'cmd_sox'):
            self.config[key] = tuple(self.config[key].split(' ')) if isinstance(self.config[key], str) else self.config[key]
        self.config.update({
            'vf_for_preview': "scale=w='{0}:h=floor(({0}*(1/a))/2)*2'".format(self.config['preview_width'])    # scale=w='min(500, iw*3/2):h=-1'
        })
        self.config.update({
            'ffmpeg_base_args': self.config['cmd_ffmpeg'] + cmd_args(
                #threads=CONFIG['threads'],
                loglevel=self.config['log_level'],
                y=None,
            ),
            'encode_image_to_video': cmd_args(
                vcodec=self.config['h264_codec'],
                r=5,  # 5 fps
                bf=0,  # wha dis do?
                qmax=1,  # wha dis do?
                vf=self.config['scale_even'],  # .format(width=width, height=height),  # ,pad={TODO}:{TODO}:(ow-iw)/2:(oh-ih)/2,setsar=1:1
                threads=self.config['threads'],
            ),
            'extract_audio': cmd_args(
                vcodec='none',
                ac=2,
                ar=44100,
            ),
            'encode_video': cmd_args(
                # preset='slow',
                vcodec=self.config['h264_codec'],
                crf=21,
                maxrate='1500k',
                bufsize='2500k',

                acodec='aac',
                strict='experimental',
                ab='196k',
                threads=self.config['threads'],
            ),
            'encode_preview': cmd_args(
                vcodec=self.config['h264_codec'],
                crf=34,
                vf=self.config['vf_for_preview'],
                acodec='aac',  # libfdk_aac
                strict='experimental',
                ab='48k',
                threads=self.config['threads'],
                #'profile:a': 'aac_he_v1',
                #ac=1,
            ),
        })

    CommandResult = namedtuple('CommandResult', ('success', 'result'))
    def _run_tool(self, *args, **kwargs):
        cmd = cmd_args(*args, **kwargs)
        log.debug(cmd)
        #import pdb ; pdb.set_trace()
        cmd_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=self.config['process_timeout_seconds'])
        if cmd_result.returncode != 0:
            log.error(cmd_result)
        return self.CommandResult(cmd_result.returncode == 0, cmd_result)

    def probe_media(self, source):
        """
        TODO: update for audio and images
        """
        if not source:
            return {}
        cmd_success, cmd_result = self._run_tool(
            *self.config['cmd_ffprobe'],
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


    def encode_image_to_video(self, source, destination, duration=10, width=320, height=240, **kwargs):
        """
        TODO: use same codec as encode_video
        """
        log.debug('encode_image_to_video - %s', os.path.basename(source))
        self._run_tool(
            *self.config['ffmpeg_base_args'],
            '-loop', '1',
            '-i', source,
            *cmd_args(
                t=duration,
            ),
            *self.config['encode_image_to_video'],
            destination,
        )


    def encode_video(self, video_source, audio_source, subtitle_source, destination):
        log.debug('encode_video - %s', os.path.basename(video_source))

        filters = [self.config['scale_even']]
        if subtitle_source:
            filters.append(f'subtitles={subtitle_source}')

        return self._run_tool(
            *self.config['ffmpeg_base_args'],
            '-i', video_source,
            '-i', audio_source,
            *cmd_args(
                vf=', '.join(filters),
            ),
            *self.config['encode_video'],
            destination,
        )

    def encode_audio(self, source, destination, **kwargs):
        """
            Decompress audio
            Normalize audio volume
            Offset audio
        """
        log.debug('encode_audio - %s', os.path.basename(source))

        path = os.path.dirname(destination)

        cmds = (
            lambda: self._run_tool(
                *self.config['ffmpeg_base_args'],
                '-i', source,
                *self.config['extract_audio'],
                os.path.join(path, 'audio_raw.wav'),
            ),
            lambda: self._run_tool(
                *self.config['cmd_sox'],
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


    def encode_preview_video(self, source, destination):
        """
        https://trac.ffmpeg.org/wiki/Encode/AAC#HE-AACversion2
        """
        log.debug('encode_preview_video - %s', os.path.basename(source))

        #crf = crf_from_res(**probe_media(source))
        #log.debug('crf: %s', crf)

        return self._run_tool(
            *self.config['ffmpeg_base_args'],
            '-i', source,
            *self.config['encode_preview'],
            destination,
        )


    def extract_image(self, source, destination, time=0.2):
        log.debug('extract_image - %s', os.path.basename(source))

        cmds = (
            lambda: self._run_tool(
                *self.config['ffmpeg_base_args'],
                '-i', source,
                *cmd_args(
                    ss=str(time),
                    vframes=1,
                    an=None,
                    vf=self.config['vf_for_preview'],
                ),
                destination,
            ),
            lambda: (os.path.exists(destination), 'expected destination image file was not generated (video source may be damaged) {0}'.format(source)),
            lambda: self._run_tool(
                *self.config['cmd_jpegoptim'],
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
