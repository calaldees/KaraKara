import logging
from collections.abc import Sequence

from tqdm.contrib.concurrent import thread_map

from lib.target import Target
from lib.track import Track


log = logging.getLogger(__name__)


def encode(tracks: Sequence[Track], reencode: bool = False, threads: int = 1) -> None:
    """
    Take a list of Track objects, and make sure that every Target exists
    """

    # Come up with a single list of every Target object that we can imagine
    targets = tuple(target for track in tracks for target in track.targets)

    # Only check if the file exists at the last minute, not at the start,
    # because somebody else might have finished this encode while we still
    # had it in our own queue.
    def _encode(target: Target) -> None:
        try:
            if reencode or not target.path.exists() or target.path.stat().st_size == 0:
                target.encode()
        except Exception:
            log.exception(f"Error encoding {target.friendly}")

    thread_map(_encode, targets, max_workers=threads, desc="encode ", unit="file")
