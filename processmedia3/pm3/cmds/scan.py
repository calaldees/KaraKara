import logging
import re
import typing as t
from collections import defaultdict
from pathlib import Path
from collections.abc import Sequence, MutableMapping

from tqdm.contrib.concurrent import thread_map

from pm3.lib.kktypes import TargetType
from pm3.lib.source import Source
from pm3.lib.track import Track
from pm3.lib.file_abstraction import AbstractFolder, AbstractFile

TARGET_TYPES = [
    # TargetType.VIDEO_H264,
    TargetType.VIDEO_AV1,
    TargetType.VIDEO_H265,
    # TargetType.PREVIEW_AV1,
    # TargetType.PREVIEW_H265,
    # TargetType.PREVIEW_H264,
    TargetType.IMAGE_AVIF,
    # TargetType.IMAGE_WEBP,
    TargetType.SUBTITLES_VTT,
    TargetType.SUBTITLES_JSON,
]
SCAN_IGNORE = [
    ".DS_Store",
    ".stfolder",
    ".stversions",
    ".syncthing",
    ".stignore",
    ".stglobalignore",
    ".swp",
    ".tmp",
    ".git",
    ".gitignore",
    "cache.db",
    "tracks.json",
    "tracks.json.br",
    "tracks.json.gz",
    "readme.txt",
    "WorkInProgress",
]

log = logging.getLogger(__name__)


def scan(
    source_folder: AbstractFolder,
    processed_dir: Path,
    match: str | None,
    cache: MutableMapping[str, t.Any],
    threads: int = 1,
) -> Sequence[Track]:
    """
    Look at the source directory and return a list of Track objects,
    where each track has:

    - An ID (eg "My_Song")
    - A list of sources from the "source" directory
      - eg "My Song.mp4", "My Song.srt", "My Song.txt"
    - A list of targets to write to the "processed" directory
      - eg "x/x53t4dg.webm", "6/6sbh34s.mp4"
    """
    # Get a list of source files grouped by Track ID, eg
    # {
    #   "My_Track": [
    #     "My Track [Vocal].mp4",
    #     "My Track [Instrumental].ogg",
    #     "My Track.srt",
    #     "My Track.txt",
    #   ],
    #   ...
    # }
    grouped: dict[str, set[AbstractFile]] = defaultdict(set)
    for file in source_folder.files:
        if any((i in file.relative) for i in SCAN_IGNORE):
            continue
        if match is None or match in file.stem:
            # filename: "My Track (Miku ver) [Instrumental].mp4"
            # track_id: "My_Track_Miku_Ver"
            matches = re.match(r"^(.*?)( \[(.+?)\])?$", file.stem.title())
            assert matches is not None  # ".*" should always match
            track_id = re.sub("[^0-9a-zA-Z]+", "_", matches.group(1)).strip("_")
            grouped[track_id].add(file)
    groups: list[tuple[str, set[AbstractFile]]] = sorted(grouped.items())

    # Turn all the (track_id, list of filenames) tuples into a
    # list of Tracks (log an error and return None if we can't
    # figure out how to turn these files into a valid Track)
    def _load_track(group: tuple[str, set[AbstractFile]]) -> Track | None:
        (track_id, files) = group
        try:
            sources = {Source(file, cache) for file in files}
            return Track(processed_dir, track_id, sources, TARGET_TYPES)
        except Exception:
            log.exception(f"Error calculating track {track_id}")
            return None

    maybe_tracks = thread_map(
        _load_track, groups, max_workers=threads, desc="scan   ", unit="track"
    )
    return [t for t in maybe_tracks if t is not None]
