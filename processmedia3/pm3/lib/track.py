import copy
import datetime
import typing as t
from collections import defaultdict
from pathlib import Path

import dateparser

from .encoders import find_appropriate_encoder
from .kktypes import MediaType, TargetType
from .source import Source, SourceType
from .target import Target


class TrackAttachment(t.TypedDict):
    variant: str
    mime: str
    path: str


class TrackDict(t.TypedDict):
    id: str
    duration: float
    attachments: dict[MediaType, list[TrackAttachment]]
    tags: dict[str, list[str]]


class TrackValidationException(Exception): ...


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
        sources: set[Source],
        target_types: list[TargetType],
    ) -> None:
        self.id = id
        self.sources = sources

        # eg: sources = {"XX [Vocal].mp4", "XX [Instr].ogg", "XX [Instr].jpg", "XX.srt", "XX.txt"}
        targets: list[Target] = []
        for target_type in target_types:
            # eg: variants = {"Vocal", "Instr"}
            for variant in {s.variant for s in sources}:
                # For each variant, we create a set of sources:
                #   variant_sources = ["XX [Vocal].mp4"]
                #   variant_sources = ["XX [Instr].ogg", "XX [Instr].jpg"]
                #   variant_sources = ["XX.srt", "XX.txt"]
                variant_sources = {s for s in sources if s.variant == variant}
                # We then try to find an encoder that can create the target_type
                # from those sources. If we find one, we create a Target for it.
                if enc := find_appropriate_encoder(target_type, variant_sources):
                    targets.append(Target(processed_dir, target_type, enc[0], enc[1], variant))

        self.targets = targets

    def _sources_by_type(self, types: set[SourceType]) -> list[Source]:
        return [s for s in self.sources if s.type in types]

    @property
    def has_tags(self) -> bool:
        return bool(self._sources_by_type({SourceType.TAGS}))

    def _parse_date(self, date_str: str) -> datetime.date:
        if parsed := dateparser.parse(date_str):
            return parsed.date()
        raise TrackValidationException(f"unparseable date: {date_str}")

    def to_json(self) -> TrackDict:
        """
        Most of ProcessMedia is fairly generic, creating any set of outputs
        from any set of inputs; this method is where we enforce the specific
        requirements of KaraKara (ie, the assumptions of Browser / Player).
        """
        attachments: dict[MediaType, list[TrackAttachment]] = defaultdict(list)
        for target in self.targets:
            attachments[target.encoder.category].append(
                TrackAttachment(
                    {
                        "variant": target.variant,
                        "mime": target.encoder.mime,
                        "path": str(target.path.relative_to(target.processed_dir)),
                    }
                )
            )
        if not attachments.get(MediaType.VIDEO):
            raise TrackValidationException("missing attachments.video")
        if not attachments.get(MediaType.IMAGE):
            raise TrackValidationException("missing attachments.image")
        for media_type in attachments:
            attachments[media_type].sort(key=lambda a: a["path"])

        tag_files = self._sources_by_type({SourceType.TAGS})
        if not tag_files:
            raise TrackValidationException("missing tag file")
        if len(tag_files) > 1:
            raise TrackValidationException("multiple tag files found")
        tags: dict[str, list[str]] = copy.deepcopy(tag_files[0].tags)
        if tags.get("title") is None:
            raise TrackValidationException("missing tags.title")
        if tags.get("category") is None:
            raise TrackValidationException("missing tags.category")

        # these are internal tags for the uploader, not for end users
        for internal in ["contact", "status", "info"]:
            if tags.get(internal):
                del tags[internal]

        # not-hard-subs + image + 16:9 = good for splash screen
        if self._sources_by_type({SourceType.SUBTITLES}):
            tags["subs"] = ["soft"]
        else:
            tags["subs"] = ["hard"]
        tags["source_type"] = []
        if self._sources_by_type({SourceType.IMAGE}):
            tags["source_type"].append("image")
        if self._sources_by_type({SourceType.VIDEO}):
            tags["source_type"].append("video")
        pixel_sources = self._sources_by_type({SourceType.VIDEO, SourceType.IMAGE})
        tags["aspect_ratio"] = sorted({s.meta.aspect_ratio_str for s in pixel_sources})

        # duration isn't useful for searching, but having it as a
        # tag means it's visible in the browser UI so singers can
        # see how long a track is before enqueueing it.
        audio_sources = self._sources_by_type({SourceType.VIDEO, SourceType.AUDIO})
        ds = {s.meta.duration.total_seconds() for s in audio_sources}
        tags["duration"] = [f"{int(d // 60)}m{int(d % 60):02}s" for d in ds]
        if max(ds) - min(ds) > 5:
            raise TrackValidationException(f"inconsistent durations: {ds}")

        # date can be a full date, but years are more useful for searching
        if tags.get("date"):
            tags["year"] = [self._parse_date(d).strftime("%Y") for d in tags["date"]]

        # Add "category:new" tag for any track added in the last year
        # and a bit (so that if a convention is held eg Jan 5th 2020,
        # then we get a request to add a track on Jan 6th 2020, it's
        # still "new" when the next convention happens on Jan 12th 2021).
        # Also add a "new:<date>" tag so that when users click "new",
        # they then get a list sorted by date added.
        if tags.get("added"):
            added_date = self._parse_date(tags["added"][0])
            today_date = datetime.date.today()
            if added_date > today_date - datetime.timedelta(days=30):
                tags["category"].append("new")
                tags["new"] = [added_date.strftime("%Y-%m-%d")]
            elif added_date > today_date - datetime.timedelta(days=380):
                tags["category"].append("new")
                tags["new"] = [added_date.strftime("%Y-%m")]

        # Sort all the tags' values because some of our input files are
        # processed in a non-deterministic order but we want the output
        # to be deterministic.
        for k in tags:
            tags[k] = sorted(set(tags[k]))

        # duration=max(durations) because if two variants are very-slightly
        # different, we want to use the longest one when calculating the
        # start-time of the next track in the queue (If they are more than
        # very-sligtly different, that should be an error).
        # duration=round(duration) to avoid floating point issues in unit tests.
        return TrackDict(
            id=self.id,
            duration=round(max(ds), 1),
            attachments=attachments,
            tags=tags,
        )
