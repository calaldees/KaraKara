import datetime
import typing as t
from pathlib import Path

import msgspec

from .type_parsers import parse_datetime, parse_timedelta

type Tag = str


# class Theme(enum.StrEnum):
#    METALGHOSTS = enum.auto()


class QueueSettings(msgspec.Struct):
    track_space: datetime.timedelta = datetime.timedelta(seconds=15)
    hidden_tags: t.Sequence[Tag] = ("red:duplicate",)
    forced_tags: t.Sequence[Tag] = ()
    title: str = "KaraKara"
    # theme: Theme = Theme.METALGHOSTS
    preview_volume: t.Annotated[float, msgspec.Meta(ge=0, le=1)] = 0.1
    coming_soon_track_count: t.Annotated[int, msgspec.Meta(gt=0, lt=10)] = 5
    validation_event_start_datetime: t.Annotated[datetime.datetime | None, msgspec.Meta(tz=True)] = None
    validation_event_end_datetime: t.Annotated[datetime.datetime | None, msgspec.Meta(tz=True)] = None
    # validation_duplicate_performer_timedelta: datetime.timedelta | None = None  # Not implemented
    # validation_duplicate_track_timedelta: datetime.timedelta | None = None  # Not implemented
    validation_performer_names: t.Sequence[str] = ()
    auto_reorder_queue: bool = False


class SettingsManager:
    def __init__(self, path: Path = Path(".")):
        path.mkdir(parents=True, exist_ok=True)  # is this safe?
        assert path.is_dir()
        self.path = path

    def room_exists(self, name: str) -> bool:
        return self.path.joinpath(f"{name}_settings.json").is_file()

    def set(self, name: str, settings: QueueSettings) -> None:
        path = self.path.joinpath(f"{name}_settings.json")
        path.write_bytes(msgspec.json.encode(settings))

    def get(self, name: str) -> QueueSettings:
        path = self.path.joinpath(f"{name}_settings.json")
        if path.is_file():
            msgspec.json.decode(path.read_bytes(), type=QueueSettings)
        return QueueSettings()
