import datetime
import enum
import typing as t
from pathlib import Path

import annotated_types
import pydantic
import ujson as json

from .type_parsers import parse_datetime, parse_timedelta

type Tag = str


class Theme(enum.StrEnum):
    METALGHOSTS = enum.auto()


Timedelta = t.Annotated[
    datetime.timedelta,
    pydantic.PlainValidator(parse_timedelta, json_schema_input_type=int|float|str),
    pydantic.PlainSerializer(lambda td: td.total_seconds() if td else None, return_type=int),
]

OptionalDatetime = t.Annotated[
    t.Optional[datetime.datetime],
    pydantic.PlainValidator(parse_datetime, json_schema_input_type=str),
    annotated_types.Timezone(datetime.timezone.utc)
    #pydantic.PlainSerializer(_parse_datetime, json_schema_input_type=str),
]
#OptionalDatetime = t.Optional[datetime.datetime]


class GlobalSettings(pydantic.BaseModel):
    tracks_json_mtime: float = 0

class PersistedQueueSettings(pydantic.BaseModel):
    track_space: Timedelta = datetime.timedelta(seconds=15)
    hidden_tags: t.Sequence[Tag] = ("red:duplicate",)
    forced_tags: t.Sequence[Tag] = ()
    title: str = "KaraKara"
    theme: Theme = Theme.METALGHOSTS
    preview_volume: t.Annotated[float, annotated_types.Ge(0), annotated_types.Le(1)] = 0.1
    coming_soon_track_count: t.Annotated[int, annotated_types.Gt(0), annotated_types.Lt(10)] = 5
    validation_event_start_datetime: OptionalDatetime = None
    validation_event_end_datetime: OptionalDatetime = None
    # validation_duplicate_performer_timedelta: t.Optional[Timedelta] = None  # Not implemented
    # validation_duplicate_track_timedelta: t.Optional[Timedelta] = None  # Not implemented
    validation_performer_names: t.Sequence[str] = ()
    auto_reorder_queue: bool = False

class QueueSettings(PersistedQueueSettings, GlobalSettings):
    """
    Unsure if this merges the two Settings class's correctly ... testing required
    """
    ...

class SettingsManager:
    def __init__(self, path: Path = Path(".")):
        path = path if isinstance(path, Path) else Path(path)
        path.mkdir(parents=True, exist_ok=True)  # is this safe?
        assert path.is_dir()
        self.path = path
        self.global_settings = GlobalSettings()

    def room_exists(self, name: str) -> bool:
        return self.path.joinpath(f"{name}_settings.json").is_file()

    def get_json(self, name: str) -> dict:
        path = self.path.joinpath(f"{name}_settings.json")
        json_str = path.read_text() if path.is_file() else PersistedQueueSettings().model_dump_json()
        return json.loads(json_str)

    def set_json(self, name: str, settings: dict) -> None:
        path = self.path.joinpath(f"{name}_settings.json")
        json_str = PersistedQueueSettings(**{**self.get_json(name), **settings}).model_dump_json()
        path.write_text(json_str)

    def get(self, name: str) -> QueueSettings:
        return QueueSettings(**self.get_json(name), **self.global_settings.model_dump())
