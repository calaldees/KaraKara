from pathlib import Path
import logging
import json
import typing as t

from ._utils import harden

log = logging.getLogger(__name__)


type Tracks = t.Mapping[str, t.Mapping[str, t.Any]]


class TrackManager:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.mtime: float = 0
        self._tracks: Tracks = {}
        if not path.is_file():
            log.error('No tracks.json file present or provided. api_queue WILL NOT FUNCTION IN PRODUCTION. `processmedia` should output this file when encoding is complete')

    @property
    def tracks(self) -> Tracks:
        mtime = self.path.stat().st_mtime
        if mtime != self.mtime:
            self.mtime = mtime
            with self.path.open() as filehandle:
                self._tracks = harden(json.load(filehandle))   # type: ignore[assignment]
        return self._tracks
