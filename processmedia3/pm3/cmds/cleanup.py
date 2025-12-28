import logging
from pathlib import Path
from collections.abc import Sequence

from tqdm.contrib.concurrent import thread_map

from pm3.lib.track import Track
from .scan import SCAN_IGNORE


log = logging.getLogger(__name__)


def cleanup(processed_dir: Path, tracks: Sequence[Track], delete: bool, threads: int = 1) -> None:
    """
    Delete any files from the processed dir that aren't included in any tracks
    """
    expected = set()
    for track in tracks:
        for target in track.targets:
            expected.add(target.path)

    def _cleanup(path: Path) -> None:
        if path.is_file() and path not in expected:
            rel = str(path.relative_to(processed_dir))
            if any((i in rel) for i in SCAN_IGNORE):
                return
            if delete:
                log.info(f"Cleaning up {rel}")
                path.unlink()
            else:
                log.info(f"{rel} due to be cleaned up")

    files = list(processed_dir.glob("**/*"))
    thread_map(_cleanup, files, max_workers=threads, desc="cleanup", unit="file")
