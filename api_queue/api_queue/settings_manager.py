import datetime
from pathlib import Path

import ujson as json
from pytimeparse.timeparse import timeparse  # type: ignore


DEFAULT_QUEUE_SETTINGS = {
    "track_space": 15.0,
    "hidden_tags": ["red:duplicate"],
    "forced_tags": [],
    "title": "KaraKara",
    "theme": "metalghosts",
    "preview_volume": 0.2,
    "validation_event_start_datetime": None,
    "validation_event_end_datetime": None,
    "validation_duplicate_performer_timedelta": None,
    "validation_duplicate_track_timedelta": None,
    "validation_performer_names": [],
    "queue_post_processing_function_names": ["validation_default",],
    "coming_soon_track_count": 5,
}
def _parse_isodatetime(isoformatString):
    if not isoformatString:
        return None
    dt = datetime.datetime.fromisoformat(isoformatString)
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt
def _parse_timedelta(durationString):
    return datetime.timedelta(seconds=timeparse(durationString)) if durationString else None
QUEUE_SETTING_TYPES = {
    "track_space": lambda x: datetime.timedelta(seconds=x),
    "validation_event_start_datetime": _parse_isodatetime,
    "validation_event_end_datetime": _parse_isodatetime,
    "validation_duplicate_performer_timedelta": _parse_timedelta,
    "validation_duplicate_track_timedelta": _parse_timedelta,
}
def parse_settings_dict(settings_dict: dict) -> dict:
    return {
        k: QUEUE_SETTING_TYPES.get(k, lambda x: x)(v)
        for k, v in settings_dict.items()
    }
def validate_settings_dict(settings_dict: dict):
    # throw exception if parsed dict (with python types) is not valid
    # settings_dict could be a subset of possible settings_dict fields
    # TODO - Implement Me!
    return
    # Idea?: would it be better to perform the validation on a complete dict before saving?

class SettingsManager():
    def __init__(self, path: Path = Path('.')):
        path = path if isinstance(path, Path) else Path(path)
        path.mkdir(parents=True, exist_ok=True)  # is this safe?
        assert path.is_dir()
        self.path = path

    def room_exists(self, name: str) -> bool:
        return self.path.joinpath(f'{name}_settings.json').is_file()

    def get_json(self, name: str) -> dict:
        path = self.path.joinpath(f'{name}_settings.json')
        if not path.is_file():
            return DEFAULT_QUEUE_SETTINGS
        with path.open('r') as filehandle:
            return {**DEFAULT_QUEUE_SETTINGS, **json.load(filehandle)}

    def set_json(self, name: str, settings: dict) -> None:
        path = self.path.joinpath(f'{name}_settings.json')
        validate_settings_dict(parse_settings_dict(settings))  # new settings should parse without exception
        old_settings = self.get_json(name)
        with path.open('w') as filehandle:
            json.dump({**old_settings, **settings}, filehandle)

    def get(self, name: str) -> dict:
        return parse_settings_dict(self.get_json(name))
