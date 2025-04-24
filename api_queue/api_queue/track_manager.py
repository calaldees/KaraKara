from pathlib import Path
import logging
import json
import typing as t
from types import MappingProxyType

log = logging.getLogger(__name__)


type TrackID = str
type TrackDurations = t.Mapping[TrackID, int | float]


class TrackManager:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.mtime: float = 0
        self.track_durations: TrackDurations = MappingProxyType({})
        if not path.is_file():
            log.error('No `tracks.json` file present or provided. api_queue WILL NOT FUNCTION IN PRODUCTION. `processmedia` should output `tracks.json` when encoding is complete')
        self.reload_tracks()

    @property
    def has_tracks_updated(self) -> bool:
        return self.mtime != self.path.stat().st_mtime

    def reload_tracks(self) -> None:
        with self.path.open() as filehandle:
            self.track_durations = MappingProxyType({
                track_id: track_payload['duration']
                for track_id, track_payload in json.load(filehandle).items()
            })
        self.mtime = self.path.stat().st_mtime
