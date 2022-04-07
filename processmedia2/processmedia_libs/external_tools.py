import logging
log = logging.getLogger(__name__)

import re
import os.path
from collections import namedtuple
import subprocess
from functools import partial

from calaldees.shell import cmd_args
cmd_args = partial(cmd_args, FLAG_PREFIX='-')


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
                'threads': 4,
                'process_timeout_seconds': 60 * 60,  # There are some HUGE videos a timeout of an hour seems pauseable
                'log_level': 'warning',
                'preview_width': 320,
                'scale_even': 'scale=w=floor(iw/2)*2:h=floor(ih/2)*2',  # 264 codec can only handle dimension a multiple of 2. Some input does not adhere to this and need correction.

                'cmd_ffmpeg': ('nice', 'ffmpeg'),
                'cmd_ffprobe': ('ffprobe', ),
                'cmd_imagemagick_convert': ('convert', ),
            },
            **config,
        }
        # parse cmd_xxx into tuples
        for key in ('cmd_ffmpeg', 'cmd_ffprobe', 'cmd_imagemagick_convert'):
            self.config[key] = tuple(self.config[key].split(' ')) if isinstance(self.config[key], str) else self.config[key]
        self.config.update({
            'vf_for_preview': "scale=w='{0}:h=floor(({0}*(1/a))/2)*2'".format(self.config['preview_width'])
        })
        self.config.update({
            'ffmpeg_base_args': self.config['cmd_ffmpeg'] + cmd_args(
                loglevel=self.config['log_level'],
                y=None,
                strict='experimental',
                threads=self.config['threads'],
            ),
            'audio_normalisisation': cmd_args(
                ac=2,
                ar=48000,
                af='loudnorm=I=-23:LRA=1:dual_mono=true:tp=-1',
                # GoogleGroups - crazy audio guys conversation
                # https://groups.google.com/a/opencast.org/g/users/c/R40ZE3l_ay8/m/2IUpQTcQCAAJ
                # highpass=f=120,acompressor=threshold=0.3:makeup=3:release=50:attack=5:knee=4:ratio=10:detection=peak,alimiter=limit=0.95 
            ),
        })

    CommandResult = namedtuple('CommandResult', ('success', 'result'))
    def _run_tool(self, *args, **kwargs):
        cmd = cmd_args(*args, **kwargs)
        log.debug(cmd)
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


    def encode_image_to_video(self, video_source, audio_source, destination, encode_args, duration=10, **kwargs):
        log.debug(f'encode_image_to_video - {video_source=} {audio_source=}')
        self._run_tool(
            *self.config['ffmpeg_base_args'],
            '-loop', '1',
            '-i', video_source,
            '-i', audio_source,
            *cmd_args(
                t=duration,

                r=5,  # 5 fps
                bf=0,  # wha dis do?
                qmax=1,  # wha dis do?
                #vf=self.config['scale_even'],  # .format(width=width, height=height),  # ,pad={TODO}:{TODO}:(ow-iw)/2:(oh-ih)/2,setsar=1:1
                **encode_args,
            ),
            destination,
        )

    def encode_video(self, source, destination, encode_args):
        return self._run_tool(
            *self.config['ffmpeg_base_args'],
            '-i', source,
            *cmd_args(**encode_args),
            *self.config['audio_normalisisation'],
            *cmd_args(
                sn=None, # don't process subtitles
            ),
            destination,
        )

    def encode_preview_video(self, source, destination, encode_args):
        log.debug('encode_preview_video - %s', os.path.basename(source))
        return self._run_tool(
            *self.config['ffmpeg_base_args'],
            '-i', source,
            *cmd_args(**encode_args),
            *self.config['audio_normalisisation'],
            *cmd_args(
                #vf=self.config['vf_for_preview'],
                ac=1, # unsure if this helps
                sn=None, # don't process subtitles
            ),
            destination,
        )


    def extract_image(self, source, destination, timecode=0.2):
        log.debug(f'extract_image - {os.path.basename(source)}')
        return self._run_tool(
            *self.config['ffmpeg_base_args'],
            '-i', source,
            *cmd_args(
                ss=str(timecode),
                vframes=1,
                an=None,
                vf=self.config['vf_for_preview'],  # TODO: consider higher resolution images now we have moved to av1?
            ),
            destination,
        )

    def compress_image(self, source, destination):
        log.debug(f'compress_image - {os.path.basename(source)}')
        return self._run_tool(
            *self.config['cmd_imagemagick_convert'],
            source,
            destination,
        )
