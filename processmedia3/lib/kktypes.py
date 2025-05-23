import base64
import hashlib
import logging
import re
import shutil
import subprocess
import tempfile
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Set, Tuple, TypeVar
from fractions import Fraction
from datetime import datetime, timedelta

from .subtitle_processor import parse_subtitles, Subtitle
from .tag_processor import parse_tags

log = logging.getLogger()
T = TypeVar("T")


class SourceType(Enum):
    VIDEO = {".mp4", ".mkv", ".avi", ".mpg", ".webm"}
    AUDIO = {".mp3", ".flac", ".ogg"}
    IMAGE = {".jpg", ".png"}
    TAGS = {".txt"}
    SUBTITLES = {".srt", ".ssa"}


class TargetType(Enum):
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


class Source:
    """
    A file in the "source" directory, with some convenience methods
    to parse data out of the file (hash, duration, etc) efficiently
    """

    def __init__(self, source_dir: Path, path: Path, cache: Dict[str, Any]):
        self.source_dir = source_dir
        self.path = path
        self.cache = cache
        self.friendly = str(path.relative_to(source_dir))
        self.path.stat
        for type in SourceType:
            if self.path.suffix in type.value:
                self.type = type
                break
        else:
            raise Exception(f"Can't tell what type of source {self.friendly} is")

    @staticmethod
    def _cache(func: Callable[["Source"], T]) -> Callable[["Source"], T]:
        """
        if `self.cache[self.file.name self.file.mtime func.name]` is set,
        return that, else call func() and add the value to the cache
        """

        def inner(self: "Source") -> T:
            mtime = self.path.stat().st_mtime
            key = (
                f"{str(self.path.relative_to(self.source_dir))}-{mtime}-{func.__name__}"
            )
            cached = self.cache.get(key)
            if not cached:
                cached = func(self)
                self.cache[key] = cached
            return cached

        return inner

    @_cache
    def hash(self) -> str:
        log.info(f"Hashing {self.friendly}")
        return hashlib.sha256(self.path.read_bytes()).hexdigest()

    @_cache
    def duration(self) -> float:
        log.info(f"Parsing duration from {self.friendly}")
        probe_proc = subprocess.run(
            ["ffprobe", self.path.as_posix()],
            stderr=subprocess.PIPE,
            text=True,
            errors="ignore",  # some files contain non-utf8 metadata
            check=True,
        )
        raw_duration = re.search(r"Duration: (\d+):(\d+):(\d+.\d+)", probe_proc.stderr)
        if not raw_duration:
            raise Exception(f"Failed to find duration in probe:\n{probe_proc.stderr}")
        hours = float(raw_duration.group(1)) * 60.0 * 60.0
        minutes = float(raw_duration.group(2)) * 60.0
        seconds = float(raw_duration.group(3))
        return hours + minutes + seconds

    @_cache
    def aspectratio(self) -> str:
        log.info(f"Parsing aspectratio from {self.friendly}")
        probe_proc = subprocess.run(
            # fmt: off
            [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,display_aspect_ratio",
                "-of", "csv=s=,:p=0",
                self.path.as_posix(),
            ],
            # fmt: on
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="ignore",  # some files contain non-utf8 metadata
            check=True,
        )
        w, h, dar = probe_proc.stdout.strip().split(",")[:3]
        if dar != "N/A":
            return dar
        f = Fraction(int(w), int(h))
        return f"{f.numerator}:{f.denominator}"

    def lyrics(self) -> List[str]:
        return [l.text for l in self.subtitles()]

    @_cache
    def subtitles(self) -> List[Subtitle]:
        log.info(f"Parsing subtitles from {self.friendly}")
        return parse_subtitles(self.path.read_text())

    @_cache
    def tags(self) -> Dict[str, List[str]]:
        log.info(f"Parsing tags from {self.friendly}")
        return parse_tags(self.path.read_text())


class Target:
    """
    A file in the "processed" directory, with a method to figure out
    the target name (based on the hash of the source files + encoder
    settings), and a method to create that file if it doesn't exist.
    """

    def __init__(
        self, processed_dir: Path, type: TargetType, sources: List[Source]
    ) -> None:
        from .encoders import find_appropriate_encoder  # circular import :(

        self.processed_dir = processed_dir
        self.type = type
        self.encoder, self.sources = find_appropriate_encoder(type, sources)

        parts = [self.encoder.salt()] + [s.hash() for s in self.sources]
        hasher = hashlib.sha256()
        hasher.update("".join(sorted(parts)).encode("utf-8"))
        hash = re.sub("[+/=]", "_", base64.b64encode(hasher.digest()).decode("utf8"))
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
            f"{[s.friendly for s in self.sources]})"
        )

        with tempfile.TemporaryDirectory() as tempdir:
            temppath = Path(tempdir) / ("out." + self.encoder.ext)
            self.encoder.encode(temppath, self.sources)
            if not temppath.exists():
                log.error(f"Encoder failed to create {temppath}")
                return
            self.path.parent.mkdir(exist_ok=True)
            log.debug(f"Moving {temppath} to {self.path}")
            shutil.move(temppath.as_posix(), self.path.as_posix())


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
        sources: List[Source],
        target_types: List[TargetType],
    ) -> None:
        self.id = id
        self.sources = sources
        self.targets = [Target(processed_dir, type, sources) for type in target_types]

    def _sources_by_type(self, types: Set[SourceType]) -> List[Source]:
        return [s for s in self.sources if s.type in types]

    def to_json(self) -> Dict[str, Any]:
        media_files = self._sources_by_type({SourceType.VIDEO, SourceType.AUDIO})
        duration = media_files[0].duration()

        attachments = defaultdict(list)
        for t in self.targets:
            attachments[t.encoder.category].append(
                {
                    "mime": t.encoder.mime,
                    "path": str(t.path.relative_to(t.processed_dir)),
                }
            )
        assert attachments.get("video"), f"{self.id} is missing attachments.video"
        assert attachments.get("preview"), f"{self.id} is missing attachments.preview"
        assert attachments.get("image"), f"{self.id} is missing attachments.image"

        sub_files = self._sources_by_type({SourceType.SUBTITLES})
        lyrics = sub_files[0].lyrics() if sub_files else []

        tag_files = self._sources_by_type({SourceType.TAGS})
        tags = tag_files[0].tags()
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
        tags["aspect_ratio"] = [pxsrc.aspectratio()]

        ausrc = self._sources_by_type({SourceType.VIDEO, SourceType.AUDIO})[0]
        d = int(ausrc.duration())
        tags["duration"] = [f"{d//60}m{d%60:02}s"]

        if tags.get("date"):
            tags["year"] = [d.split("-")[0] for d in tags["date"]]

        return {
            "id": self.id,
            "duration": round(duration, 1),  # for more consistent unit tests
            "attachments": attachments,
            "lyrics": lyrics,
            "tags": tags,
        }
