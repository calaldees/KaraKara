from pathlib import Path
import logging
import json

from ._utils import harden

log = logging.getLogger(__name__)


class TrackManager:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.mtime = 0
        self._tracks = {}
        if not path.is_file():
            log.error('No tracks.json file present or provided. api_queue WILL NOT FUNCTION IN PRODUCTION. processmedia2 should output this file when encoding is complete')

    @property
    def tracks(self):
        mtime = self.path.stat().st_mtime
        if mtime != self.mtime:
            self.mtime = mtime
            with self.path.open() as filehandle:
                self._tracks = harden(json.load(filehandle))
        return self._tracks
