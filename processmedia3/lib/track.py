import typing as t
from collections import defaultdict
import copy
from pathlib import Path
from collections.abc import Sequence, Mapping, MutableMapping, MutableSequence
from .kktypes import MediaType, TargetType
from .source import Source, SourceType
from .target import Target
from .encoders import find_appropriate_encoder


class TrackAttachment(t.TypedDict):
    mime: str
    path: str


class TrackDict(t.TypedDict):
    id: str
    duration: float
    attachments: Mapping[MediaType, Sequence[TrackAttachment]]
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
        sources: t.Set[Source],
        target_types: Sequence[TargetType],
    ) -> None:
        self.id = id
        self.sources = sources
        targets = []
        for target_type in target_types:
            if enc := find_appropriate_encoder(target_type, sources):
                targets.append(Target(processed_dir, target_type, enc[0], enc[1]))
        self.targets = targets

    def _sources_by_type(self, types: t.Set[SourceType]) -> Sequence[Source]:
        return [s for s in self.sources if s.type in types]

    @property
    def has_tags(self) -> bool:
        return bool(self._sources_by_type({SourceType.TAGS}))

    def to_json(self) -> TrackDict:
        """
        Most of ProcessMedia is fairly generic, creating any set of outputs
        from any set of inputs; this method is where we enforce the specific
        requirements of KaraKara (ie, the assumptions of Browser / Player).
        """
        media_files = self._sources_by_type({SourceType.VIDEO, SourceType.AUDIO})
        duration = media_files[0].meta.duration.total_seconds()

        attachments: MutableMapping[MediaType, MutableSequence[TrackAttachment]] = defaultdict(list)
        for target in self.targets:
            attachments[target.encoder.category].append(
                TrackAttachment({
                    "mime": target.encoder.mime,
                    "path": str(target.path.relative_to(target.processed_dir)),
                })
            )
        assert attachments.get(MediaType.VIDEO), f"{self.id} is missing attachments.video"
        assert attachments.get(MediaType.IMAGE), f"{self.id} is missing attachments.image"

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
        tags["aspect_ratio"] = list(set(
            pxsrc.meta.aspect_ratio_str
            for pxsrc
            in self._sources_by_type({SourceType.VIDEO, SourceType.IMAGE})
        ))

        ds = list(set(
            int(ausrc.meta.duration.total_seconds())
            for ausrc
            in self._sources_by_type({SourceType.VIDEO, SourceType.AUDIO})
        ))
        assert len(ds) == 1, f"{self.id} has inconsistent durations: {ds}"

        if tags.get("date"):
            tags["year"] = [d.split("-")[0] for d in tags["date"]]

        return TrackDict(
            id=self.id,
            duration=round(duration, 1),  # for more consistent unit tests
            attachments=attachments,
            tags=tags,
        )
