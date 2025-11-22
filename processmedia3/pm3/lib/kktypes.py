import logging
import subprocess
import enum
import typing as t
import json
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
        return ":".join(map(str, self.aspect_ratio.as_integer_ratio()))

    @classmethod
    def from_width_height(cls, width: int, height: int) -> "MediaMeta":
        return cls(width=width, height=height, aspect_ratio=Fraction(width, height))

    @classmethod
    def from_uri(
        cls,
        uri,
        _subprocess_run: t.Callable[..., subprocess.CompletedProcess] = subprocess.run,
    ) -> t.Self:
        r"""
        >>> MediaMeta.from_uri("tests/source/test1.mp4")
        MediaMeta(fps=10.0, width=640, height=480, duration=datetime.timedelta(seconds=30), aspect_ratio=Fraction(4, 3))

        >>> MediaMeta.from_uri("tests/source/test2.png")
        MediaMeta(fps=25.0, width=640, height=400, duration=datetime.timedelta(0), aspect_ratio=Fraction(8, 5))

        >>> MediaMeta.from_uri("tests/source/test2.ogg")
        MediaMeta(fps=0.0, width=0, height=0, duration=datetime.timedelta(seconds=15), aspect_ratio=Fraction(1, 1))
        """
        completed_process = _subprocess_run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                uri,
            ],
            capture_output=True,
            check=True,
        )
        ffprobe_output = json.loads(completed_process.stdout.decode("utf8", errors="ignore"))

        try:
            fps = 0.0
            width = 0
            height = 0

            video = next(
                (s for s in ffprobe_output["streams"] if s["codec_type"] == "video"),
                None,
            )
            if video:
                num, denom = map(int, video["r_frame_rate"].split("/"))
                fps = num / denom if denom != 0 else 0.0
                width = video["width"]
                height = video["height"]

            duration = timedelta(seconds=float(ffprobe_output["format"].get("duration", "0.0")))

            if video and "display_aspect_ratio" in video:
                w, h = map(int, video["display_aspect_ratio"].split(":"))
                aspect_ratio = Fraction(w, h)
            else:
                aspect_ratio = Fraction(width or 1, height or 1)

            return cls(fps, width, height, duration, aspect_ratio)
        except Exception as e:
            raise ValueError(f"Could not parse media metadata for {uri}: {e}\n{ffprobe_output}") from e
