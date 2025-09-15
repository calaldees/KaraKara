import enum
import typing as t
import logging
from collections.abc import Sequence, Mapping, MutableMapping

from .subtitle_processor import parse_subtitles, Subtitle
from .tag_processor import parse_tags
from .file_abstraction import AbstractFile
from .kktypes import MediaMeta

log = logging.getLogger()
T = t.TypeVar("T")


class SourceType(enum.Enum):
    VIDEO = frozenset({".mp4", ".mkv", ".avi", ".mpg", ".webm"})
    AUDIO = frozenset({".mp3", ".flac", ".ogg", ".aac"})
    IMAGE = frozenset({".jpg", ".png", ".webp", ".avif"})
    TAGS = frozenset({".txt"})
    SUBTITLES = frozenset({".srt", ".ssa"})


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
        if not self.type:
            raise SourceTypeException(f"Can't tell what type of source {self.file.relative} is")

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
