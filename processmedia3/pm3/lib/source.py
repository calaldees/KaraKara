import enum
import logging
import re
import typing as t
from collections.abc import MutableMapping
from datetime import timedelta

from .file_abstraction import AbstractFile
from .kktypes import MediaMeta
from .subtitle_processor import Subtitle, parse_subtitles
from .tag_processor import parse_tags

log = logging.getLogger()
T = t.TypeVar("T")


class SourceType(enum.Enum):
    VIDEO = frozenset({".mp4", ".mkv", ".avi", ".mpg", ".webm"})
    AUDIO = frozenset({".mp3", ".flac", ".ogg", ".aac", ".opus"})
    IMAGE = frozenset({".jpg", ".png", ".webp", ".avif"})
    TAGS = frozenset({".txt"})
    SUBTITLES = frozenset({".srt", ".ssa", ".ass"})


class SourceTypeException(Exception):
    pass


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
        self.variant = variant_match.group(1) if variant_match else "Default"

        if not self.type:
            raise SourceTypeException(f"Can't tell what type of source {self.file.relative} is")

    def __str__(self) -> str:
        return self.file.relative

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
    def subtitles(self) -> list[Subtitle]:
        """
        Load subtitles and apply any opinionated fixes
        (fixes for things which are definitely-wrong should
        go in subtitle_processor.py)
        """
        log.info(f"Parsing subtitles from {self.file.relative}")

        # Normalise invisible encoding differences so that searching
        # works as expected (e.g. replacing Cyrillic 'е' with Latin 'e')
        t = self.file.text
        t = t.replace("\u0435", "e")
        t = t.replace(" ", " ")

        # Remove one-frame blinks between subtitles
        lines = parse_subtitles(t)
        for i in range(len(lines) - 1):
            tdiff = lines[i + 1].start - lines[i].end
            if timedelta(seconds=-0.1) < tdiff < timedelta(seconds=0.1):
                lines[i] = Subtitle(
                    idx=lines[i].idx,
                    start=lines[i].start,
                    end=lines[i + 1].start,
                    text=lines[i].text,
                    top=lines[i].top,
                )
        return lines

    @property
    @_cache
    def tags(self) -> dict[str, list[str]]:
        log.info(f"Parsing tags from {self.file.relative}")
        return parse_tags(self.file.text)
