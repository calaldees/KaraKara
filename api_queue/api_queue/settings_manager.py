import datetime
import typing as t
from pathlib import Path

import annotated_types
import pydantic
import ujson as json

from .type_parsers import parse_datetime, parse_timedelta

type Tag = str


# class Theme(enum.StrEnum):
#    METALGHOSTS = enum.auto()


Timedelta = t.Annotated[
    datetime.timedelta,
    pydantic.PlainValidator(parse_timedelta, json_schema_input_type=int | float | str),
    pydantic.PlainSerializer(lambda td: td.total_seconds() if td else None, return_type=int),
]

OptionalDatetime = t.Annotated[
    datetime.datetime | None,
    pydantic.PlainValidator(parse_datetime, json_schema_input_type=str),
    annotated_types.Timezone(datetime.timezone.utc),
    # pydantic.PlainSerializer(_parse_datetime, json_schema_input_type=str),
]


class QueueSettings(pydantic.BaseModel):
    track_space: Timedelta = datetime.timedelta(seconds=15)
    hidden_tags: t.Sequence[Tag] = ("red:duplicate",)
    forced_tags: t.Sequence[Tag] = ()
    title: str = "KaraKara"
    # theme: Theme = Theme.METALGHOSTS
    preview_volume: t.Annotated[float, annotated_types.Ge(0), annotated_types.Le(1)] = 0.1
    coming_soon_track_count: t.Annotated[int, annotated_types.Gt(0), annotated_types.Lt(10)] = 5
    validation_event_start_datetime: OptionalDatetime = None
    validation_event_end_datetime: OptionalDatetime = None
    # validation_duplicate_performer_timedelta: Timedelta | None = None  # Not implemented
    # validation_duplicate_track_timedelta: Timedelta | None = None  # Not implemented
    validation_performer_names: t.Sequence[str] = ()
    auto_reorder_queue: bool = False


class SettingsManager:
    def __init__(self, path: Path = Path(".")):
        path.mkdir(parents=True, exist_ok=True)  # is this safe?
        assert path.is_dir()
        self.path = path

    def room_exists(self, name: str) -> bool:
        return self.path.joinpath(f"{name}_settings.json").is_file()

    def get_json(self, name: str) -> dict[str, t.Any]:
        path = self.path.joinpath(f"{name}_settings.json")
        json_str = path.read_text() if path.is_file() else QueueSettings().model_dump_json()
        return json.loads(json_str)

    def set_json(self, name: str, settings: dict[str, t.Any]) -> None:
        path = self.path.joinpath(f"{name}_settings.json")
        json_str = QueueSettings(**{**self.get_json(name), **settings}).model_dump_json()
        path.write_text(json_str)

    def get(self, name: str) -> QueueSettings:
        return QueueSettings(**self.get_json(name))
