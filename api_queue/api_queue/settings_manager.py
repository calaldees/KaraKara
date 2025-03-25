import datetime
import enum
import typing as t
from pathlib import Path

import pydantic
import ujson as json
import pytimeparse2  # type: ignore
import dateparser

type Tag = str


class Theme(enum.StrEnum):
    METALGHOSTS = enum.auto()


def _parse_timedelta(duration: int | float | str | datetime.timedelta) -> t.Optional[datetime.timedelta]:
    if not duration:
        return None
    if isinstance(duration, datetime.timedelta):
        return duration
    seconds = pytimeparse2.parse(duration) if isinstance(duration, str) else duration
    return datetime.timedelta(seconds=seconds)

Timedelta = t.Annotated[
    datetime.timedelta,
    pydantic.PlainValidator(_parse_timedelta, json_schema_input_type=int|float|str),
    pydantic.PlainSerializer(lambda td: td.total_seconds() if td else None, return_type=int),
]

def _parse_datetime(value: str | int) -> t.Optional[datetime.datetime]:
    #dt = datetime.datetime.fromisoformat(isoformatString)
    dt: t.Optional[datetime.datetime] = None
    if isinstance(value, int):
        dt = datetime.datetime.fromtimestamp(value, tz=datetime.timezone.utc)
    if isinstance(value, str):
        dt = dateparser.parse(value)
        if not dt:
            raise ValueError(f'unable to parse datetime {value}')
    if not dt:
        return None
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt

OptionalDatetime = t.Annotated[
    t.Optional[datetime.datetime],
    pydantic.PlainValidator(_parse_datetime, json_schema_input_type=str),
    #pydantic.PlainSerializer(_parse_datetime, json_schema_input_type=str),
]
#OptionalDatetime = t.Optional[datetime.datetime]


class QueueSettings(pydantic.BaseModel):
    track_space: Timedelta = datetime.timedelta(seconds=15)
    hidden_tags: t.Sequence[Tag] = ("red:duplicate",)
    forced_tags: t.Sequence[Tag] = ()
    title: str = "KaraKara"
    theme: Theme = Theme.METALGHOSTS
    preview_volume: float = 0.1
    coming_soon_track_count: int = 5
    validation_event_start_datetime: OptionalDatetime = None
    validation_event_end_datetime: OptionalDatetime = None
    validation_duplicate_performer_timedelta: t.Optional[Timedelta] = None
    validation_duplicate_track_timedelta: t.Optional[Timedelta] = None
    validation_performer_names: t.Sequence[str] = ()
    queue_post_processing_function_names: t.Sequence[str] = ("validation_default", )


class SettingsManager:
    def __init__(self, path: Path = Path(".")):
        path = path if isinstance(path, Path) else Path(path)
        path.mkdir(parents=True, exist_ok=True)  # is this safe?
        assert path.is_dir()
        self.path = path

    def room_exists(self, name: str) -> bool:
        return self.path.joinpath(f"{name}_settings.json").is_file()

    def get_json(self, name: str) -> dict:
        path = self.path.joinpath(f"{name}_settings.json")
        json_str = path.read_text() if path.is_file() else QueueSettings().model_dump_json()
        return json.loads(json_str)

    def set_json(self, name: str, settings: dict) -> None:
        path = self.path.joinpath(f"{name}_settings.json")
        json_str = QueueSettings(**{**self.get_json(name), **settings}).model_dump_json()
        path.write_text(json_str)

    def get(self, name: str) -> QueueSettings:
        return QueueSettings(**self.get_json(name))
