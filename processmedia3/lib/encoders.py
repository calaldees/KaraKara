import logging
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

from .kktypes import Source, SourceType, TargetType
from .subtitle_processor import create_vtt, parse_subtitles

log = logging.getLogger()

# TODO: "-movflags +faststart" to make mp4 streamable?
# TODO: max size for full videos?
# https://trac.ffmpeg.org/wiki/Encode/AAC#HE-AACversion2
# h264 codec can only handle dimension a multiple of 2.
# Some input does not adhere to this and need correction.
IMAGE_QUALITY = 75
IMAGE_SCALE = 256
PREVIEW_SCALE = 320

SCALE_EVEN = ["-vf", "scale=w=floor(iw/2)*2:h=floor(ih/2)*2"]
SCALE_PREVIEW = ["-vf", "scale=w='{0}:h=floor(({0}*(1/a))/2)*2'".format(PREVIEW_SCALE)]
NORMALIZE_AUDIO = ["-af", "loudnorm=I=-23:LRA=1:dual_mono=true:tp=-1"]

CODEC_AV1 = [
    "-vcodec",
    "libsvtav1",
    "-preset",
    "4",
    "-qp",
    "50",
    "-sc_detection",
    "true",
    "-pix_fmt",
    "yuv420p10le",
    "-g",
    "240",
]
CODEC_H265 = ["-vcodec", "libx265", "-crf", "39", "-preset", "slow"]
CODEC_H264 = ["-vcodec", "libx264", "-crf", "39", "-preset", "fast"]

CODEC_OPUS = ["-acodec", "libopus", "-ac", "2"]
CODEC_AAC = ["-acodec", "libfdk_aac", "-ac", "2"]
CODEC_MP3 = ["-acodec", "mp3", "-ac", "2"]


class Encoder:
    target: TargetType
    sources: Set[SourceType]
    category: str
    ext: str
    mime: str
    pm2_salt: List[str] = ["", ""]
    settings: Dict[str, Any] = {}

    def salt(self) -> str:
        return self.category + "-" + str(self.settings)

    def encode(self, target: Path, sources: Set[Source]) -> None:
        ...

    def _run(self, *args: str):
        try:

            subprocess.run(
                ["nice"] + list(args),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                errors="ignore",  # some files contain non-utf8 metadata
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise Exception(
                f"Command failed ({e.returncode}): {shlex.join(args)}\n"
                f"{e.stdout}\n"
                f"{e.stderr}"
            )
        except Exception as e:
            raise Exception(f"Command failed {args}\n{e}")


#######################################################################
# Video to Video


class _BaseVideoToVideo(Encoder):
    sources = {SourceType.VIDEO}
    category = "video"

    def encode(self, target: Path, sources: Set[Source]) -> None:
        self._run(
            "ffmpeg",
            "-i",
            list(sources)[0].path.as_posix(),
            *self.settings["vcodec"],
            *self.settings["acodec"],
            *(SCALE_EVEN if self.category == "video" else SCALE_PREVIEW),
            *NORMALIZE_AUDIO,
            target.as_posix(),
        )


class VideoToAV1(_BaseVideoToVideo):
    target = TargetType.VIDEO_AV1
    ext = "webm"
    pm2_salt = [
        "video",
        "{'vcodec': 'libsvtav1', 'preset': 4, 'qp': 50, 'sc_detection': 'true', 'pix_fmt': 'yuv420p10le', 'g': 240, 'acodec': 'libopus', 'ac': 2, 'vf': 'scale=w=floor(iw/2)*2:h=floor(ih/2)*2', 'af': 'loudnorm=I=-23:LRA=1:dual_mono=true:tp=-1'}",
    ]
    mime = "video/webm; codecs=av01.0.05M.08,opus"
    settings = {
        "vcodec": CODEC_AV1,
        "acodec": CODEC_OPUS,
    }


class VideoToAV1Preview(VideoToAV1):
    target = TargetType.PREVIEW_AV1
    category = "preview"
    pm2_salt = [
        "preview_av1",
        """{'vcodec': 'libsvtav1', 'preset': 4, 'qp': 60, 'sc_detection': 'true', 'pix_fmt': 'yuv420p10le', 'g': 240, 'acodec': 'libopus', 'ab': '24k', 'ac': 1, 'vf': "scale=w='320:h=floor((320*(1/a))/2)*2'", 'af': 'loudnorm=I=-23:LRA=1:dual_mono=true:tp=-1'}""",
    ]


class VideoToH265(_BaseVideoToVideo):
    target = TargetType.VIDEO_H265
    ext = "mp4"
    mime = "video/mp4; codecs=avc1.4D401E,mp4a.40.2"
    settings = {
        "vcodec": CODEC_H265,
        "acodec": CODEC_AAC,
    }


class VideoToH265Preview(VideoToH265):
    target = TargetType.PREVIEW_H265
    category = "preview"
    pm2_salt = [
        "preview_h265",
        """{'vcodec': 'libx265', 'crf': 39, 'preset': 'slow', 'acodec': 'libfdk_aac', 'ab': '24k', 'ac': 1, 'vf': "scale=w='320:h=floor((320*(1/a))/2)*2'", 'af': 'loudnorm=I=-23:LRA=1:dual_mono=true:tp=-1'}""",
    ]


class VideoToH264(_BaseVideoToVideo):
    target = TargetType.VIDEO_H264
    ext = "mp4"
    mime = "video/mp4"
    settings = {
        "vcodec": CODEC_H265,
        "acodec": CODEC_MP3,
    }


class VideoToH264Preview(VideoToH264):
    target = TargetType.PREVIEW_H264
    category = "preview"
    pm2_salt = ["preview"]


#######################################################################
# Image + Audio to Video


class _BaseImageToVideo(Encoder):
    sources = {SourceType.AUDIO, SourceType.IMAGE}
    category = "video"

    def encode(self, target: Path, sources: Set[Source]) -> None:
        def source_by_type(type: SourceType) -> Source:
            return [s for s in sources if s.type == type][0]

        self._run(
            "ffmpeg",
            "-loop",
            "1",
            "-i",
            source_by_type(SourceType.IMAGE).path.as_posix(),
            "-i",
            source_by_type(SourceType.AUDIO).path.as_posix(),
            "-t",
            str(source_by_type(SourceType.AUDIO).duration()),
            "-r",
            "1",  # 1 fps
            "-bf",
            "0",  # wha dis do?
            "-qmax",
            "1",  # wha dis do?
            *self.settings["vcodec"],
            *self.settings["acodec"],
            *(SCALE_EVEN if self.category == "video" else SCALE_PREVIEW),
            *NORMALIZE_AUDIO,
            target.as_posix(),
        )


class ImageToAV1(_BaseImageToVideo):
    target = TargetType.VIDEO_AV1
    ext = "webm"
    pm2_salt = [
        "video",
        "{'vcodec': 'libsvtav1', 'preset': 4, 'qp': 50, 'sc_detection': 'true', 'pix_fmt': 'yuv420p10le', 'g': 240, 'acodec': 'libopus', 'ac': 2, 'vf': 'scale=w=floor(iw/2)*2:h=floor(ih/2)*2', 'af': 'loudnorm=I=-23:LRA=1:dual_mono=true:tp=-1'}",
    ]
    mime = "video/webm; codecs=av01.0.05M.08,opus"
    settings = {
        "vcodec": CODEC_AV1,
        "acodec": CODEC_OPUS,
    }


class ImageToAV1Preview(ImageToAV1):
    target = TargetType.PREVIEW_AV1
    category = "preview"
    pm2_salt = [
        "preview_av1",
        """{'vcodec': 'libsvtav1', 'preset': 4, 'qp': 60, 'sc_detection': 'true', 'pix_fmt': 'yuv420p10le', 'g': 240, 'acodec': 'libopus', 'ab': '24k', 'ac': 1, 'vf': "scale=w='320:h=floor((320*(1/a))/2)*2'", 'af': 'loudnorm=I=-23:LRA=1:dual_mono=true:tp=-1'}""",
    ]


class ImageToH265(_BaseImageToVideo):
    target = TargetType.VIDEO_H265
    ext = "mp4"
    mime = "video/mp4; codecs=avc1.4D401E,mp4a.40.2"
    settings = {
        "vcodec": CODEC_H265,
        "acodec": CODEC_AAC,
    }


class ImageToH265Preview(ImageToH265):
    target = TargetType.PREVIEW_H265
    category = "preview"
    pm2_salt = [
        "preview_h265",
        """{'vcodec': 'libx265', 'crf': 39, 'preset': 'slow', 'acodec': 'libfdk_aac', 'ab': '24k', 'ac': 1, 'vf': "scale=w='320:h=floor((320*(1/a))/2)*2'", 'af': 'loudnorm=I=-23:LRA=1:dual_mono=true:tp=-1'}""",
    ]


class ImageToH264(_BaseImageToVideo):
    target = TargetType.VIDEO_H264
    ext = "mp4"
    mime = "video/mp4"
    settings = {
        "vcodec": CODEC_H264,
        "acodec": CODEC_MP3,
    }


class ImageToH264Preview(ImageToH264):
    target = TargetType.PREVIEW_H264
    category = "preview"


#######################################################################
# Video to Image


class _BaseVideoToImage(Encoder):
    sources = {SourceType.VIDEO}
    category = "image"
    settings = {
        "scale": ["-vf", f"thumbnail,scale={IMAGE_SCALE}:-1"],
        "compress": ["-quality", str(IMAGE_QUALITY)],
    }

    def encode(self, target: Path, sources: Set[Source]) -> None:
        # imagemagick supports more formats, so first we get
        # ffmpeg to pick a frame, then convert to compress
        temp_target = target.with_suffix(".bmp")
        self._run(
            "ffmpeg",
            "-i",
            list(sources)[0].path.as_posix(),
            *self.settings["scale"],
            "-vframes",
            "1",
            "-an",
            temp_target.as_posix(),
        )
        self._run(
            "convert",
            temp_target.as_posix(),
            *self.settings["compress"],
            target.as_posix(),
        )
        temp_target.unlink()


class VideoToWebp(_BaseVideoToImage):
    target = TargetType.IMAGE_WEBP
    ext = "webp"
    mime = "image/webp"


class VideoToAvif(_BaseVideoToImage):
    target = TargetType.IMAGE_AVIF
    ext = "avif"
    mime = "image/avif"


#######################################################################
# Image to Image


class _BaseImageToImage(Encoder):
    sources = {SourceType.IMAGE}
    category = "image"
    settings = {
        "size": str(IMAGE_SCALE),
        "compress": ["-quality", str(IMAGE_QUALITY)],
    }

    def encode(self, target: Path, sources: Set[Source]) -> None:
        self._run(
            "convert",
            list(sources)[0].path.as_posix(),
            "-thumbnail",
            f"{self.settings['size']}x{self.settings['size']}",
            *self.settings["compress"],
            target.as_posix(),
        )


class ImageToWebp(_BaseImageToImage):
    target = TargetType.IMAGE_WEBP
    ext = "webp"
    mime = "image/webp"


class ImageToAvif(_BaseImageToImage):
    target = TargetType.IMAGE_AVIF
    ext = "avif"
    mime = "image/avif"


#######################################################################
# Subtitles


class SubtitleToVTT(Encoder):
    target = TargetType.SUBTITLES_VTT
    sources = {SourceType.SUBTITLES}
    ext = "vtt"
    category = "subtitle"
    pm2_salt = ["subtitle", "{}"]
    mime = "text/vtt"

    def encode(self, target: Path, sources: Set[Source]) -> None:
        with open(list(sources)[0].path.as_posix()) as srt:
            with open(target.as_posix(), "w") as vtt:
                vtt.write(create_vtt(parse_subtitles(srt.read())))


class VoidToVTT(Encoder):
    target = TargetType.SUBTITLES_VTT
    sources: Set[SourceType] = set()
    ext = "vtt"
    category = "subtitle"
    pm2_salt = ["subtitle", "{}"]
    mime = "text/vtt"

    def encode(self, target: Path, sources: Set[Source]) -> None:
        with open(target.as_posix(), "w") as vtt:
            vtt.write(create_vtt([]))


#######################################################################


def find_appropriate_encoder(
    type: TargetType, sources: List[Source]
) -> Tuple[Encoder, Set[Source]]:
    def all_subclasses(cls):
        return set(cls.__subclasses__()).union(
            [s for c in cls.__subclasses__() for s in all_subclasses(c)]
        )

    # Sort encoders by how many sources they take, so "combine multiple
    # media" will take priority over "use a single media" which will take
    # priority over "generate a stub file from nothing"
    encoders = all_subclasses(Encoder)
    encoders = [e for e in encoders if e.__name__[0] != "_"]
    encoders = sorted(encoders, key=lambda x: len(x.sources), reverse=True)

    for encoder in encoders:
        if encoder.target == type and encoder.sources.issubset(
            {s.type for s in sources}
        ):
            return encoder(), {s for s in sources if s.type in encoder.sources}
    else:
        source_list = "\n".join(f"  - {s.type}: {s.friendly}" for s in sources)
        raise Exception(
            f"Couldn't find an encoder to make {type} out of:\n{source_list}"
        )
