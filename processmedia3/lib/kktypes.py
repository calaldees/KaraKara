import base64
import hashlib
import logging
import re
import shutil
import subprocess
import tempfile
import copy
from collections import defaultdict
import enum
from pathlib import Path
import typing as t
from collections.abc import Sequence, Mapping, MutableMapping, MutableSequence, Set
from fractions import Fraction
from datetime import timedelta

from .subtitle_processor import parse_subtitles, Subtitle
from .tag_processor import parse_tags
from .file_abstraction import AbstractFile

log = logging.getLogger()
T = t.TypeVar("T")


class SourceType(enum.Enum):
    VIDEO = frozenset({".mp4", ".mkv", ".avi", ".mpg", ".webm"})
    AUDIO = frozenset({".mp3", ".flac", ".ogg", ".aac"})
    IMAGE = frozenset({".jpg", ".png", ".webp", ".avif"})
    TAGS = frozenset({".txt"})
    SUBTITLES = frozenset({".srt", ".ssa"})


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
    def from_width_height(cls, width, height):
        return cls(width=width, height=height, aspect_ratio=Fraction(width, height))

    @classmethod
    def from_uri(cls, uri, _subprocess_run: t.Callable[...,subprocess.CompletedProcess]=subprocess.run) -> t.Self:
        r"""
        >>> from textwrap import dedent

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


class Source:
    """
    A file in the "source" directory, with some convenience methods
    to parse data out of the file (hash, duration, etc) efficiently
    """

    def __init__(self, file: AbstractFile, cache: MutableMapping[str, t.Any]):
        self.file = file
        self.cache = cache
        self.type: SourceType | None = next((type for type in SourceType if self.file.suffix in type.value), None)
        variant_match = re.search(r"\[(.+?)\]$", self.file.stem)
        self.variant = str(variant_match.group(1)) if variant_match else None
        if not self.type:
            raise Exception(f"Can't tell what type of source {self.file.relative} is")

    @staticmethod
    def _cache(func: t.Callable[["Source"], T]) -> t.Callable[["Source"], T]:
        """
        if `self.cache[self.file.name self.file.mtime func.name]` is set,
        return that, else call func() and add the value to the cache
        """

        def inner(self: "Source") -> T:
            # Normalise mtime to accuracy of 1min. This enables remote and local timestamps to match
            # Technically there is a possibility of an update that is missed, but it's pretty edge case for our usecase
            mtime = int(self.file.mtime.replace(second=0, microsecond=0).timestamp())
            key = f"{self.file.relative}-{mtime}-{func.__name__}"
            cached = self.cache.get(key)
            if not cached:
                cached = func(self)
                self.cache[key] = cached
            return cached

        return inner

    @property
    @_cache
    def hash(self) -> str:
        log.info(f"Hashing {self.file.relative}")
        return self.file.hash

    @property
    @_cache
    def meta(self) -> MediaMeta:
        log.info(f"Parsing meta from {self.file.relative}")
        return MediaMeta.from_uri(self.file.absolute)

    @property
    @_cache
    def subtitles(self) -> Sequence[Subtitle]:
        log.info(f"Parsing subtitles from {self.file.relative}")
        return parse_subtitles(self.file.text)

    @property
    def lyrics(self) -> Sequence[str]:
        return [l.text for l in self.subtitles]

    @property
    @_cache
    def tags(self) -> Mapping[str, Sequence[str]]:
        log.info(f"Parsing tags from {self.file.relative}")
        return parse_tags(self.file.text)


class Target:
    """
    A file in the "processed" directory, with a method to figure out
    the target name (based on the hash of the source files + encoder
    settings), and a method to create that file if it doesn't exist.
    """

    def __init__(
        self,
        processed_dir: Path,
        type: TargetType,
        sources: Set[Source],
        variant: str | None,
    ) -> None:
        from .encoders import find_appropriate_encoder  # circular import :(

        self.processed_dir = processed_dir
        self.type = type
        self.variant = variant
        if variant:
            sources = {s for s in sources if s.variant == variant}
        self.encoder, self.sources = find_appropriate_encoder(type, sources)

        parts = [self.encoder.salt] + [s.hash for s in self.sources]
        hasher = hashlib.sha256()
        hasher.update("".join(sorted(parts)).encode("ascii"))
        hash = re.sub("[+/=]", "_", base64.b64encode(hasher.digest()).decode("ascii"))
        self.friendly = hash[0].lower() + "/" + hash[:11] + "." + self.encoder.ext
        self.path = (
            processed_dir / hash[0].lower() / (hash[:11] + "." + self.encoder.ext)
        )
        log.debug(
            f"Filename for {self.encoder.__class__.__name__} = {self.friendly} based on {parts}"
        )

    def encode(self) -> None:
        log.info(
            f"{self.encoder.__class__.__name__}("
            f"{self.friendly!r}, "
            f"{[s.file.relative for s in self.sources]})"
        )
        with tempfile.TemporaryDirectory() as tempdir:
            temppath = Path(tempdir) / ("out." + self.encoder.ext)
            try:
                self.encoder.encode(temppath, self.sources)
                if not temppath.exists():
                    raise Exception("Encoder didn't return any error, but failed to create an output file")
                if temppath.stat().st_size == 0:
                    raise Exception("Encoder didn't return any error, but created an empty file")
                self.path.parent.mkdir(exist_ok=True)
                log.debug(f"Moving {temppath} to {self.path}")
                shutil.move(temppath.as_posix(), self.path.as_posix())
            except Exception as e:
                log.error(f"Error while encoding {self.friendly!r}: {e}")

    def __str__(self):
        source_list = [s.file.relative for s in self.sources]
        var = f"[{self.variant}]" if self.variant else ""
        return f"{self.type.name}{var}: {self.friendly!r} = {self.encoder.__class__.__name__}({source_list!r})"

class TrackAttachment(t.TypedDict):
    variant: str | None
    mime: str
    path: str
class TrackDict(t.TypedDict):
    id: str
    duration: float
    attachments: Mapping[MediaType, Sequence[TrackAttachment]]
    lyrics: Sequence[str]
    tags: Mapping[str, Sequence[str]]


class Track:
    """
    An entry in tracks.json, keeping track of which source files are
    used to build the track, which target files should be generated,
    and a method to dump all the metadata into a json dict.
    """

    def __init__(
        self,
        processed_dir: Path,
        id: str,
        sources: Set[Source],
        target_types: Sequence[TargetType],
    ) -> None:
        self.id = id
        self.sources = sources
        video_variants = self._variants_by_type({SourceType.VIDEO, SourceType.AUDIO})
        video_target_types = {t for t in target_types if t.name.startswith("VIDEO_")}
        preview_target_types = {t for t in target_types if t.name.startswith("PREVIEW_")}
        subtitle_variants = self._variants_by_type({SourceType.SUBTITLES})
        subtitle_target_types = {t for t in target_types if t.name.startswith("SUBTITLES_")}
        image_target_types = {t for t in target_types if t.name.startswith("IMAGE_")}
        targets = set()
        import itertools
        for variant, type in itertools.product(video_variants, video_target_types):
            targets.add(Target(processed_dir, type, sources, variant))
        for type in preview_target_types:
            targets.add(Target(processed_dir, type, sources, None))
        for variant, type in itertools.product(subtitle_variants, subtitle_target_types):
            targets.add(Target(processed_dir, type, sources, variant))
        for type in image_target_types:
            targets.add(Target(processed_dir, type, sources, None))
        self.targets = list(targets)

    def _variants_by_type(self, types: Set[SourceType]) -> Set[str|None]:
        variants = {s.variant for s in self.sources if s.type in types}
        if None in variants:
            if len(variants) > 1:
                raise Exception(f"Mixing variant and non-variant sources of type {types} in track {self.id}")
        return variants

    def _sources_by_type(self, types: Set[SourceType]) -> Sequence[Source]:
        return [s for s in self.sources if s.type in types]

    @property
    def has_tags(self) -> bool:
        return bool(self._sources_by_type({SourceType.TAGS}))

    def to_json(self) -> TrackDict:
        media_files = self._sources_by_type({SourceType.VIDEO, SourceType.AUDIO})
        duration = media_files[0].meta.duration.total_seconds()

        attachments: MutableMapping[MediaType, MutableSequence[TrackAttachment]] = defaultdict(list)
        for target in self.targets:
            attachments[target.encoder.category].append(
                TrackAttachment({
                    "variant": target.variant,
                    "mime": target.encoder.mime,
                    "path": str(target.path.relative_to(target.processed_dir)),
                })
            )
        assert attachments.get(MediaType.VIDEO), f"{self.id} is missing attachments.video"
        #assert attachments.get(MediaType.PREVIEW), f"{self.id} is missing attachments.preview"
        assert attachments.get(MediaType.IMAGE), f"{self.id} is missing attachments.image"

        sub_files = self._sources_by_type({SourceType.SUBTITLES})
        lyrics = sub_files[0].lyrics if sub_files else []

        tag_files = self._sources_by_type({SourceType.TAGS})
        tags: MutableMapping[str, MutableSequence[str]] = copy.deepcopy(tag_files[0].tags)  # type: ignore[arg-type]
        assert tags.get("title") is not None, f"{self.id} is missing tags.title"
        assert tags.get("category") is not None, f"{self.id} is missing tags.category"

        if self._sources_by_type({SourceType.SUBTITLES}):
            tags["subs"] = ["soft"]
        else:
            tags["subs"] = ["hard"]
        tags["source_type"] = []
        if self._sources_by_type({SourceType.IMAGE}):
            tags["source_type"].append("image")
        if self._sources_by_type({SourceType.VIDEO}):
            tags["source_type"].append("video")
        pxsrc = self._sources_by_type({SourceType.VIDEO, SourceType.IMAGE})[0]
        tags["aspect_ratio"] = [pxsrc.meta.aspect_ratio_str]

        ausrc = self._sources_by_type({SourceType.VIDEO, SourceType.AUDIO})[0]
        d = int(ausrc.meta.duration.total_seconds())
        tags["duration"] = [f"{d//60}m{d%60:02}s"]

        if tags.get("date"):
            tags["year"] = [d.split("-")[0] for d in tags["date"]]

        return TrackDict(
            id=self.id,
            duration=round(duration, 1),  # for more consistent unit tests
            attachments=attachments,
            lyrics=lyrics,
            tags=tags,
        )
