import logging
import re
import subprocess
import enum
import typing as t
from fractions import Fraction
from datetime import timedelta

log = logging.getLogger()
T = t.TypeVar("T")


class TargetType(enum.Enum):
    VIDEO_H264 = 10
    VIDEO_AV1 = 11
    VIDEO_H265 = 12
    PREVIEW_H264 = 20
    PREVIEW_AV1 = 21
    PREVIEW_H265 = 22
    IMAGE_WEBP = 30
    IMAGE_AVIF = 31
    IMAGE_JPEG = 32
    SUBTITLES_VTT = 40
    SUBTITLES_JSON = 41


class MediaType(enum.StrEnum):
    VIDEO = enum.auto()
    PREVIEW = enum.auto()
    SUBTITLE = enum.auto()
    IMAGE = enum.auto()


class MediaMeta(t.NamedTuple):
    fps: float = 0.0
    width: int = 0
    height: int = 0
    duration: timedelta = timedelta(seconds=0)
    aspect_ratio: Fraction = Fraction(1, 1)

    @property
    def aspect_ratio_str(self) -> str:
        return ':'.join(map(str,self.aspect_ratio.as_integer_ratio()))

    @classmethod
    def from_width_height(cls, width: int, height: int) -> "MediaMeta":
        return cls(width=width, height=height, aspect_ratio=Fraction(width, height))

    @classmethod
    def from_uri(cls, uri, _subprocess_run: t.Callable[...,subprocess.CompletedProcess]=subprocess.run) -> t.Self:
        r"""
        >>> from textwrap import dedent
        >>> from pathlib import Path

        >>> from unittest.mock import Mock
        >>> def from_uri(fake_ffprobe_stderr):
        ...     mock_subprocess_run = Mock()
        ...     mock_completed_process = Mock()
        ...     mock_subprocess_run.return_value = mock_completed_process
        ...     mock_completed_process.returncode = 0
        ...     mock_completed_process.stderr.decode.return_value = fake_ffprobe_stderr
        ...     return MediaMeta.from_uri(Path(), _subprocess_run=mock_subprocess_run)

        >>> fake_ffprobe_stderr_video = dedent('''
        ...     Input #0, matroska,webm, from 'Macross Dynamite7 - OP - Dynamite Explosion.mkv':
        ...     Metadata:
        ...         title           : [ET] マクロスダイナマイト7 - NC OP Ver.01
        ...         encoder         : libebml v1.3.0 + libmatroska v1.4.0
        ...         creation_time   : 2013-08-24T18:45:46.000000Z
        ...     Duration: 00:02:08.13, start: 0.000000, bitrate: 8747 kb/s
        ...     Stream #0:0(jpn): Video: h264 (High 10), yuv420p10le(tv, bt709/unknown/unknown, progressive), 960x720, SAR 1:1 DAR 4:3, 23.98 fps, 23.98 tbr, 1k tbn (default)
        ...     Stream #0:1(jpn): Audio: flac, 48000 Hz, stereo, s16 (default)
        ... ''')
        >>> from_uri(fake_ffprobe_stderr_video)
        MediaMeta(fps=23.98, width=960, height=720, duration=datetime.timedelta(seconds=128, microseconds=130000), aspect_ratio=Fraction(4, 3))

        >>> fake_ffprobe_stderr_image = dedent('''
        ...     Input #0, png_pipe, from 'Screenshot 2025-02-14 at 15.58.24.png':
        ...     Duration: N/A, bitrate: N/A
        ...     Stream #0:0: Video: png, rgba(pc, gbr/unknown/unknown), 3024x1646 [SAR 5669:5669 DAR 1512:823], 25 fps, 25 tbr, 25 tbn
        ... ''')
        >>> from_uri(fake_ffprobe_stderr_image)
        MediaMeta(fps=25.0, width=3024, height=1646, duration=datetime.timedelta(0), aspect_ratio=Fraction(1512, 823))


        >>> fake_ffprobe_stderr_audio = dedent('''
        ...   Duration: 00:03:32.48, start: 0.025056, bitrate: 322 kb/s
        ...     Stream #0:0: Audio: mp3 (mp3float), 44100 Hz, stereo, fltp, 320 kb/s
        ...     Metadata:
        ...     encoder         : LAME3.97
        ...     Stream #0:1: Video: mjpeg (Baseline), yuvj420p(pc, bt470bg/unknown/unknown), 534x599 [SAR 72:72 DAR 534:599], 90k tbr, 90k tbn (attached pic)
        ... ''')
        >>> from_uri(fake_ffprobe_stderr_audio)
        MediaMeta(fps=0.0, width=534, height=599, duration=datetime.timedelta(seconds=212, microseconds=480000), aspect_ratio=Fraction(534, 599))
        """
        # Can `ffprobe` output json?
        completed_process = _subprocess_run(("ffprobe", uri), capture_output=True)
        if completed_process.returncode:
            log.debug(f'Unable to ffprobe {uri}')
            return cls()
        ffprobe_output = completed_process.stderr.decode('utf8', errors="ignore")

        fps = 0.0
        if match := re.search(r'(\d{1,3}(\.\d+)?) fps', ffprobe_output):
            fps = float(match.group(1))

        width = 0
        height = 0
        if match := re.search(r'((\d{3,4})x(\d{3,4}))', ffprobe_output):
            width, height = int(match.group(2)), int(match.group(3))

        duration = timedelta(seconds=0)
        if match := re.search(r'Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})', ffprobe_output):
            duration = timedelta(
                hours=int(match.group(1)),
                minutes=int(match.group(2)),
                seconds=float(match.group(3)),
            )

        aspect_ratio = Fraction(width or 1, height or 1)
        if match := re.search(r'DAR (\d{1,4}):(\d{1,4})', ffprobe_output):
            aspect_ratio = Fraction(int(match.group(1)), int(match.group(2)))

        return cls(fps, width, height, duration, aspect_ratio)
