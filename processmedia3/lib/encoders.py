import itertools
import logging
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

from .kktypes import Source, SourceType, TargetType
from .subtitle_processor import create_vtt, parse_subtitles

log = logging.getLogger()

# fmt: off
IMAGE_QUALITY = 75
IMAGE_WIDTH = 256

# Scale down if necessary to fit inside the given box,
# and make sure that everything is a multiple of 2
_RATIO = "force_original_aspect_ratio=decrease:force_divisible_by=2"
SCALE_VIDEO = ["-vf", f"scale=w='min(iw,1280)':h='min(ih,720)':{_RATIO}"]
SCALE_PREVIEW = ["-vf", f"scale=w='min(iw,320)':h='min(ih,240)':{_RATIO}"]

NORMALIZE_AUDIO = ["-af", "loudnorm=I=-23:LRA=1:dual_mono=true:tp=-1", "-ac", "2"]

CONTINER_MP4 = ["-movflags", "faststart"]

VCODEC_AV1 = ["-vcodec", "libsvtav1", "-pix_fmt", "yuv420p10le"]
# tag hvc1 needed for apple software to understand it
VCODEC_H265 = ["-vcodec", "libx265", "-tag:v", "hvc1"]
# yuv420p needed for apple software to understand it
VCODEC_H264 = ["-vcodec", "libx264", "-pix_fmt", "yuv420p"]

ACODEC_OPUS = ["-acodec", "libopus"]
ACODEC_AAC = ["-acodec", "libfdk_aac"]
ACODEC_MP3 = ["-acodec", "mp3"]
# fmt: on


class Encoder:
    target: TargetType
    sources: Set[SourceType]
    category: str
    ext: str
    mime: str
    priority: int = 1
    conf_audio: List[str] = []
    conf_video: List[str] = []
    conf_container: List[str] = []
    conf_acodec: List[str] = []
    conf_vcodec: List[str] = []

    def salt(self) -> str:
        # sort, concatenate, and flatten all of the conf_* arrays
        confs = [getattr(self, k) for k in sorted(dir(self)) if k.startswith("conf_")]
        confs = list(itertools.chain.from_iterable(confs))
        return str(confs)

    def encode(self, target: Path, sources: Set[Source]) -> None:
        ...

    def _run(self, *args: str):
        try:
            log.debug(f"Calling external command: {shlex.join(args)}")
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


class _Preview(Encoder):
    category = "preview"
    conf_video = SCALE_PREVIEW


class _BaseVideoToVideo(Encoder):
    sources = {SourceType.VIDEO}
    category = "video"
    conf_audio = NORMALIZE_AUDIO
    conf_video = SCALE_VIDEO

    def encode(self, target: Path, sources: Set[Source]) -> None:
        # fmt: off
        self._run(
            "ffmpeg",
            "-i", list(sources)[0].path.as_posix(),
            *self.conf_audio,
            *self.conf_video,
            *self.conf_container,
            *self.conf_vcodec,
            *self.conf_acodec,
            target.as_posix(),
        )
        # fmt: on


class VideoToAV1(_BaseVideoToVideo):
    target = TargetType.VIDEO_AV1
    ext = "webm"
    mime = "video/webm; codecs=av01.0.05M.08,opus"
    conf_vcodec = VCODEC_AV1
    conf_acodec = ACODEC_OPUS


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
    category = "video"
    conf_audio = NORMALIZE_AUDIO
    conf_video = SCALE_VIDEO

    def encode(self, target: Path, sources: Set[Source]) -> None:
        def source_by_type(type: SourceType) -> Source:
            return [s for s in sources if s.type == type][0]

        # fmt: off
        self._run(
            "ffmpeg",
            "-loop", "1",
            "-i", source_by_type(SourceType.IMAGE).path.as_posix(),
            "-i", source_by_type(SourceType.AUDIO).path.as_posix(),
            "-t", str(source_by_type(SourceType.AUDIO).duration()),
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
    category = "image"
    conf_video = ["-vf", f"scale={IMAGE_WIDTH}:-1,thumbnail", "-vsync", "vfr"]
    conf_vcodec = ["-quality", str(IMAGE_QUALITY)]

    def encode(self, target: Path, sources: Set[Source]) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            tmpdir = Path(td)
            # imagemagick supports more formats, so first we get
            # ffmpeg to pick a frame, then convert to compress
            # fmt: off
            self._run(
                "ffmpeg",
                "-i", list(sources)[0].path.as_posix(),
                *self.conf_video,
                "-an",
                (tmpdir / "out%03d.bmp").as_posix(),
            )
            thumbs = list(tmpdir.glob("*.bmp"))
            best = select_best_image(thumbs)
            self._run(
                "convert",
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
    category = "image"
    conf_video = ["-thumbnail", f"{IMAGE_WIDTH}x{IMAGE_WIDTH}"]
    conf_vcodec = ["-quality", str(IMAGE_QUALITY)]
    priority = 2

    def encode(self, target: Path, sources: Set[Source]) -> None:
        # fmt: off
        self._run(
            "convert",
            list(sources)[0].path.as_posix(),
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
    category = "subtitle"
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
    mime = "text/vtt"
    priority = 0

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
        source_list = "\n".join(f"  - {s.type}: {s.friendly}" for s in sources)
        raise Exception(
            f"Couldn't find an encoder to make {type} out of:\n{source_list}"
        )


def select_best_image(paths: List[Path]) -> Path:
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
