import itertools
import logging
import shlex
import subprocess
from pathlib import Path
import typing as t
from abc import abstractmethod
from collections.abc import Sequence, Set
import re
import math

import tqdm

from .kktypes import Source, SourceType, TargetType, MediaType, MediaMeta
from .subtitle_processor import create_vtt, parse_subtitles

log = logging.getLogger()

# fmt: off
IMAGE_QUALITY = 50
IMAGE_WIDTH = 256

# Scale down if necessary to fit inside the given box,
# and make sure that everything is a multiple of 2
_RATIO = "force_original_aspect_ratio=decrease:force_divisible_by=2"
SCALE_VIDEO = ["-vf", f"scale=w='min(iw,1280)':h='min(ih,720)':{_RATIO}"]
SCALE_PREVIEW = ["-vf", f"scale=w='min(iw,320)':h='min(ih,240)':{_RATIO}"]

NORMALIZE_AUDIO = ["-af", "loudnorm=I=-23:LRA=1:dual_mono=true:tp=-1", "-ac", "2"]

CONTINER_MP4 = ["-movflags", "faststart"]

VCODEC_AV1 = [
    # https://trac.ffmpeg.org/wiki/Encode/AV1
    #"-c:v", "av1", "-strict", "experimental"  # auto select highest priority AV1 encoder
    "-vcodec", "libsvtav1",     # STV-AV1 software (there are 3 software encoders, but the others are early reference implementations)
    "-pix_fmt", "yuv420p10le",  # 10bit
    #"-b:v", "400k",  # "-bufsize", "4096k", "-maxrate", "1024k", "-minrate", "256k",
    #"-preset", "4",
]
VCODEC_H265 = [
    # https://trac.ffmpeg.org/wiki/Encode/H.265
    "-vcodec", "libx265",
    "-tag:v", "hvc1",  # tag hvc1 needed for apple software to understand it
    "-b:v", "400k", # "-maxrate", "1024k", "-minrate", "256k", "-bufsize", "4096k",
    "-preset", "medium",
]
# yuv420p needed for apple software to understand it
VCODEC_H264 = ["-vcodec", "libx264", "-pix_fmt", "yuv420p"]

ACODEC_OPUS = ["-acodec", "libopus"]
ACODEC_AAC = ["-acodec", "aac"]
ACODEC_MP3 = ["-acodec", "mp3"]
# fmt: on


class Encoder:
    target: TargetType
    sources: Set[SourceType]
    category: MediaType
    ext: str
    mime: str
    priority: int = 1
    conf_audio: Sequence[str] = []
    conf_video: Sequence[str] = []
    conf_container: Sequence[str] = []
    conf_acodec: Sequence[str] = []
    conf_vcodec: Sequence[str] = []

    def salt(self) -> str:
        # sort, concatenate, and flatten all of the conf_* arrays
        confs = [getattr(self, k) for k in sorted(dir(self)) if k.startswith("conf_")]
        confs = list(itertools.chain.from_iterable(confs))
        return str(confs)

    @abstractmethod
    def encode(self, target: Path, sources: Set[Source]) -> None: ...

    def _run(self, *args: str, title: str|None = None, duration: float|None=None) -> None:
        output = []
        with tqdm.tqdm(
            total=int(duration) if duration else None,
            unit="s",
            disable=duration is None,
            leave=False
        ) as pbar:
            pbar.set_description(title)

            log.debug(f"Calling external command: {shlex.join(args)}")
            proc = subprocess.Popen(
                ["nice"] + list(args),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                errors="ignore",  # some files contain non-utf8 metadata
            )

            assert proc.stdout is not None
            while line := proc.stdout.readline():
                output.append(line)
                if match := re.search(r"time=(\d+):(\d+):(\d+.\d+)", line):
                    hours, minutes, seconds = match.groups()
                    current_s = int(int(hours) * 60 * 60 + int(minutes) * 60 + float(seconds))
                    pbar.update(current_s - pbar.n)

        proc.wait()
        if proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode, shlex.join(args), "".join(output))


#######################################################################
# Video to Video

class _Preview(Encoder):
    category = MediaType.PREVIEW
    conf_video = SCALE_PREVIEW


class _BaseVideoToVideo(Encoder):
    sources = {SourceType.VIDEO}
    category = MediaType.VIDEO
    conf_audio = NORMALIZE_AUDIO
    conf_video = SCALE_VIDEO

    @t.override
    def encode(self, target: Path, sources: Set[Source]) -> None:
        # fmt: off
        source = list(sources)[0]
        # framestep: Reduce framerate down to 30fps max - there is no need for 60fps in karaoke
        framestep = int(1 + math.floor(source.meta.fps / 30))
        self._run(
            "ffmpeg",
            "-hide_banner",
            "-loglevel", "quiet",
            "-stats",
            "-i", source.file.absolute,
            *self.conf_audio,
            *self._append_ffmpeg_video_filter_string(self.conf_video, f'framestep={framestep}'),
            *self.conf_container,
            *self.conf_vcodec,
            *self.additional_vcodec_arguments(source.meta),
            *self.conf_acodec,
            target.as_posix(),
            title=f"{self.__class__.__name__}({source.file.stem})",
            duration=source.meta.duration.total_seconds(),
        )
        # fmt: on

    def additional_vcodec_arguments(self, video_meta: MediaMeta) -> Sequence[str]:
        return []

    @staticmethod
    def _append_ffmpeg_video_filter_string(args: Sequence[str], *filters: str) -> Sequence[str]:
        """
        >>> _BaseVideoToVideo._append_ffmpeg_video_filter_string(('unknown1', '-vf', 'SOME_FILTER', 'unknown2'))
        ('unknown1', '-vf', 'SOME_FILTER', 'unknown2')
        >>> _BaseVideoToVideo._append_ffmpeg_video_filter_string(('unknown1', '-vf', 'SOME_FILTER', 'unknown2'), 'ANOTHER_FILTER', 'MORE_FILTER')
        ('unknown1', '-vf', 'SOME_FILTER,ANOTHER_FILTER,MORE_FILTER', 'unknown2')
        """
        for arg_a, arg_b in itertools.pairwise(args):
            if arg_a in {'-vf', '-filter:v'}:
                replace = arg_b
                replacement = ','.join(itertools.chain((arg_b,), filters))
        return tuple(arg if arg != replace else replacement for arg in args)


class VideoToAV1(_BaseVideoToVideo):
    target = TargetType.VIDEO_AV1
    ext = "webm"
    mime = "video/webm; codecs=av01.0.05M.08,opus"
    conf_vcodec = VCODEC_AV1
    conf_acodec = ACODEC_OPUS

    @t.override
    @classmethod
    def additional_vcodec_arguments(cls, meta: MediaMeta) -> Sequence[str]:
        """
        Goals
        1. per track (per minuet) roughly the same size
        2. per track (per minuet) roughly the same encoding time

        Bigger res == more time to encode + higher filesize
        Correct for resolution
        Preset (encode time) + crf (perceived quality)

        Test videos:
         Prince Valiant    :  480*360 172k 1min  1.6 crf 45 preset 3  0.90 encodefps
         Dynamite Explosion:  960*720 691k 2min  6mb crf 55 preset 4  0.47 encodefps
         FF Endwalker      : 1280*720 921k 4min 15mb crf 60 preset 6  0.55 encodefps

        I think the real solution to this is `total_pixels` -> video `bitrate` == consistent-ish number of bytes per pixel. Out 320x240 videos don't need ultra bitrates, but 1280 should not have turd bitrate.
        The heuristic I've created visibly feels ballpark even if it's unscientific and weird.
        Happy for this to be revisited.

        >>> VideoToAV1.additional_vcodec_arguments(MediaMeta.from_width_height(1280, 720))
        ['-crf', '56', '-preset', '6']
        >>> VideoToAV1.additional_vcodec_arguments(MediaMeta.from_width_height(960, 720))
        ['-crf', '55', '-preset', '5']
        >>> VideoToAV1.additional_vcodec_arguments(MediaMeta.from_width_height(480, 360))
        ['-crf', '52', '-preset', '4']
        >>> VideoToAV1.additional_vcodec_arguments(MediaMeta.from_width_height(720, 520))
        ['-crf', '53', '-preset', '4']
        >>> VideoToAV1.additional_vcodec_arguments(MediaMeta.from_width_height(1920, 1080))
        ['-crf', '56', '-preset', '6']
        """
        class AV1Args(t.NamedTuple):
            total_pixels: int
            crf: int
            preset: int
        _top = AV1Args(total_pixels=1280*720, crf=56, preset=6)
        _bot = AV1Args(total_pixels=960*720, crf=55, preset=5)

        def translate(input_top, input_bot, output_top, output_bot, input_value):
            input_range = input_top - input_bot
            output_range = output_top - output_bot
            return output_bot + (((input_value-input_bot)/input_range)*output_range)

        total_pixels = min(meta.width*meta.height, 1280*720)  # ffmpeg will max width to 1280. See SCALE_VIDEO
        crf = int(translate(_top.total_pixels, _bot.total_pixels, _top.crf, _bot.crf, total_pixels))
        crf = max(crf, 45)
        preset = int(translate(_top.total_pixels, _bot.total_pixels, _top.preset, _bot.preset, total_pixels))
        preset = max(preset, 4)
        return ["-crf", str(crf), "-preset", str(preset)]


class VideoToAV1Preview(_Preview, VideoToAV1):
    target = TargetType.PREVIEW_AV1


class VideoToH265(_BaseVideoToVideo):
    target = TargetType.VIDEO_H265
    ext = "mp4"
    mime = "video/mp4; codecs=avc1.4D401E,mp4a.40.2"
    conf_vcodec = VCODEC_H265
    conf_acodec = ACODEC_AAC


class VideoToH265Preview(_Preview, VideoToH265):
    target = TargetType.PREVIEW_H265


class VideoToH264(_BaseVideoToVideo):
    target = TargetType.VIDEO_H264
    ext = "mp4"
    mime = "video/mp4"
    conf_vcodec = VCODEC_H264
    conf_acodec = ACODEC_MP3


class VideoToH264Preview(_Preview, VideoToH264):
    target = TargetType.PREVIEW_H264


#######################################################################
# Image + Audio to Video


class _BaseImageToVideo(Encoder):
    sources = {SourceType.AUDIO, SourceType.IMAGE}
    category = MediaType.VIDEO
    conf_audio = NORMALIZE_AUDIO
    conf_video = SCALE_VIDEO

    @t.override
    def encode(self, target: Path, sources: Set[Source]) -> None:
        def source_by_type(type: SourceType) -> Source:
            return [s for s in sources if s.type == type][0]

        # fmt: off
        self._run(
            "ffmpeg",
            "-loop", "1",
            "-i", source_by_type(SourceType.IMAGE).file.absolute,
            "-i", source_by_type(SourceType.AUDIO).file.absolute,
            "-t", str(source_by_type(SourceType.AUDIO).meta.duration.total_seconds()),
            "-r", "1",  # 1 fps
            *self.conf_audio,
            *self.conf_video,
            *self.conf_container,
            *self.conf_vcodec,
            *self.conf_acodec,
            target.as_posix(),
        )
        # fmt: on


class ImageToAV1(_BaseImageToVideo):
    target = TargetType.VIDEO_AV1
    ext = "webm"
    mime = "video/webm; codecs=av01.0.05M.08,opus"
    conf_vcodec = VCODEC_AV1
    conf_acodec = ACODEC_OPUS


class ImageToAV1Preview(_Preview, ImageToAV1):
    target = TargetType.PREVIEW_AV1


class ImageToH265(_BaseImageToVideo):
    target = TargetType.VIDEO_H265
    ext = "mp4"
    mime = "video/mp4; codecs=avc1.4D401E,mp4a.40.2"
    conf_container = CONTINER_MP4
    conf_vcodec = VCODEC_H265
    conf_acodec = ACODEC_AAC


class ImageToH265Preview(_Preview, ImageToH265):
    target = TargetType.PREVIEW_H265


class ImageToH264(_BaseImageToVideo):
    target = TargetType.VIDEO_H264
    ext = "mp4"
    mime = "video/mp4"
    conf_container = CONTINER_MP4
    conf_vcodec = VCODEC_H264
    conf_acodec = ACODEC_MP3


class ImageToH264Preview(_Preview, ImageToH264):
    target = TargetType.PREVIEW_H264


#######################################################################
# Video to Image


class _BaseVideoToImage(Encoder):
    sources = {SourceType.VIDEO}
    category = MediaType.IMAGE
    conf_video = ["-vf", f"scale={IMAGE_WIDTH}:-1,thumbnail", "-vsync", "vfr"]
    conf_vcodec = ["-quality", str(IMAGE_QUALITY)]

    @t.override
    def encode(self, target: Path, sources: Set[Source]) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            tmpdir = Path(td)
            # imagemagick supports more formats, so first we get
            # ffmpeg to pick a frame, then convert to compress
            # fmt: off
            self._run(
                "ffmpeg",
                "-i", list(sources)[0].file.absolute,
                *self.conf_video,
                # TODO: fps for images? possible every 20 seconds?
                "-an",
                (tmpdir / "out%03d.bmp").as_posix(),
            )
            thumbs = list(tmpdir.glob("*.bmp"))
            best = select_best_image(thumbs)
            # TODO: handle/return error code
            self._run(
                "magick",
                best.as_posix(),
                *self.conf_vcodec,
                target.as_posix(),
            )
            # fmt: on


class VideoToWebp(_BaseVideoToImage):
    target = TargetType.IMAGE_WEBP
    ext = "webp"
    mime = "image/webp"


class VideoToAvif(_BaseVideoToImage):
    target = TargetType.IMAGE_AVIF
    ext = "avif"
    mime = "image/avif"


class VideoToJpeg(_BaseVideoToImage):
    target = TargetType.IMAGE_JPEG
    ext = "jpeg"
    mime = "image/jpeg"


#######################################################################
# Image to Image


class _BaseImageToImage(Encoder):
    sources = {SourceType.IMAGE}
    category = MediaType.IMAGE
    conf_video = ["-thumbnail", f"{IMAGE_WIDTH}x{IMAGE_WIDTH}"]
    conf_vcodec = ["-quality", str(IMAGE_QUALITY)]
    priority = 2

    @t.override
    def encode(self, target: Path, sources: Set[Source]) -> None:
        # fmt: off
        self._run(
            "convert",
            list(sources)[0].file.absolute,  # TODO: double check `convert` can take url as input
            *self.conf_video,
            *self.conf_vcodec,
            target.as_posix(),
        )
        # fmt: on


class ImageToWebp(_BaseImageToImage):
    target = TargetType.IMAGE_WEBP
    ext = "webp"
    mime = "image/webp"


class ImageToAvif(_BaseImageToImage):
    target = TargetType.IMAGE_AVIF
    ext = "avif"
    mime = "image/avif"


class ImageToJpeg(_BaseImageToImage):
    target = TargetType.IMAGE_JPEG
    ext = "jpeg"
    mime = "image/jpeg"


#######################################################################
# Subtitles


class SubtitleToVTT(Encoder):
    target = TargetType.SUBTITLES_VTT
    sources = {SourceType.SUBTITLES}
    ext = "vtt"
    category = MediaType.SUBTITLE
    mime = "text/vtt"

    @t.override
    def encode(self, target: Path, sources: Set[Source]) -> None:
        srt = list(sources)[0].file.text
        with open(target.as_posix(), "w") as vtt:
            vtt.write(create_vtt(parse_subtitles(srt)))


class VoidToVTT(Encoder):
    target = TargetType.SUBTITLES_VTT
    sources: Set[SourceType] = set()
    ext = "vtt"
    category = MediaType.SUBTITLE
    mime = "text/vtt"
    priority = 0

    @t.override
    def encode(self, target: Path, sources: Set[Source]) -> None:
        with open(target.as_posix(), "w") as vtt:
            vtt.write(create_vtt([]))


#######################################################################


def find_appropriate_encoder(type: TargetType, sources: Set[Source]) -> t.Tuple[Encoder, Set[Source]]:
    def all_subclasses(cls):
        return set(cls.__subclasses__()).union(
            [s for c in cls.__subclasses__() for s in all_subclasses(c)]
        )

    # Sort encoders by priority, highest first. Priority is manually specified
    # so that:
    # - encoders who generate empty stubs are low-priority
    # - most encoders are mid-priority
    # - image-to-image is high priority (so that if we have a choice of
    #   "generate thumbnail from video" or "generate thumbnail from image",
    #   we assume that a human chose the image sensibly)
    encoders = all_subclasses(Encoder)
    encoders = [e for e in encoders if e.__name__[0] != "_"]
    encoders = sorted(encoders, key=lambda x: x.priority, reverse=True)

    for encoder in encoders:
        if encoder.target == type and encoder.sources.issubset(
            {s.type for s in sources}
        ):
            return encoder(), {s for s in sources if s.type in encoder.sources}
    else:
        source_list = "\n".join(f"  - {s.type}: {s.file.relative}" for s in sources)
        raise Exception(
            f"Couldn't find an encoder to make {type} out of:\n{source_list}"
        )


def select_best_image(paths: Sequence[Path]) -> Path:
    def score(p: Path) -> float:
        from PIL import Image
        img = Image.open(p.as_posix()).convert("L")
        # r, g, b = img.split()
        h = img.histogram()
        px_cnt = sum(h) # total number of pixels in the image

        # if blacks make up most of the image, or if whites make up most of the image
        thresh = 0.5
        if sum(h[:32]) > px_cnt * thresh or sum(h[-32:]) > px_cnt * thresh:
            score = 0.0
        else:
            score = (sum(h[:128]) * sum(h[128:])) / sum(h)
        # print(p, score)
        return score

    if len(paths) == 0:
        raise Exception("Can't select best of zero thumbs")
    scored_paths = [(score(p), p) for p in sorted(paths)]
    ok_paths = [(score, p) for (score, p) in scored_paths if score > 0]
    if ok_paths:
        scored_paths = ok_paths
    return sorted(scored_paths, reverse=True)[0][1]


if __name__ == "__main__":
    import sys
    print(select_best_image(list(Path(sys.argv[1]).glob("*.bmp"))))
