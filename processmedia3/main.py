#!/usr/bin/env python3

import argparse
import contextlib
import gzip
import json
import logging
import math
import os
import pickle
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from tqdm.contrib.concurrent import thread_map
from tqdm.contrib.logging import logging_redirect_tqdm

from lib.kktypes import Source, TargetType, Track

log = logging.getLogger()

TARGET_TYPES = [
    # TargetType.VIDEO_H264,
    TargetType.VIDEO_AV1,
    # TargetType.VIDEO_H265,
    TargetType.PREVIEW_AV1,
    TargetType.PREVIEW_H265,
    # TargetType.PREVIEW_H264,
    TargetType.IMAGE_AVIF1,
    TargetType.IMAGE_AVIF2,
    TargetType.IMAGE_AVIF3,
    TargetType.IMAGE_AVIF4,
    TargetType.IMAGE_WEBP1,
    TargetType.IMAGE_WEBP2,
    TargetType.IMAGE_WEBP3,
    TargetType.IMAGE_WEBP4,
    TargetType.SUBTITLES_VTT,
]
SCAN_IGNORE = [
    ".DS_Store",
    ".stfolder",
    ".stversions",
]


def scan(
    source_dir: Path,
    processed_dir: Path,
    match: str,
    cache: Dict[str, Any],
    threads: int = 1,
) -> List[Track]:
    """
    Look at the source directory and return a list of Track objects,
    where each track has:

    - An ID (eg "My_Song")
    - A list of sources from the "source" directory
      - eg "My Song.mp4", "My Song.srt", "My Song.txt"
    - A list of targets to write to the "processed" directory
      - eg "x/x53t4dg.webm", "6/6sbh34s.mp4"
    """

    # Get a list of source files grouped by basename, eg
    # {
    #   "My Track": ["My Track.mp4", "My Track.srt", "My Track.txt"],
    #   ...
    # }
    grouped = defaultdict(list)
    for path in source_dir.glob("**/*"):
        posix = path.to_posix()
        if any((i in posix) for i in SCAN_IGNORE):
            continue
        if path.is_file() and (match is None or match in path.stem):
            grouped[path.stem].append(path)

    # Turn a basename and list of filenames into a Track
    def _load_track(group: Tuple[str, List[Path]]) -> Optional[Track]:
        (basename, paths) = group
        try:
            sources = []
            for path in paths:
                source = Source(source_dir, path, cache)
                source.hash()  # force hashing now
                sources.append(source)
            return Track(processed_dir, basename, sources, TARGET_TYPES)
        except Exception:
            log.exception(f"Error calculating track {basename}")
            return None

    # Turn all the files into a list of Tracks
    groups = sorted(grouped.items())
    maybe_tracks = thread_map(_load_track, groups, max_workers=threads, desc="scan  ")
    return [t for t in maybe_tracks if t]


def view(tracks: List[Track]) -> None:
    """
    Print out a list of Tracks, marking whether or not each Target (ie, each
    file in the "processsed" directory) exists
    """
    GREEN = "\033[92m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    OK = GREEN + "✔" + ENDC
    FAIL = RED + "✘" + ENDC

    for track in tracks:
        print(track.id)
        for t in track.targets:
            source_list = [s.friendly for s in t.sources]
            print(
                f"  - {t.type.name}: {t.friendly!r} = "
                + f"{t.encoder.__class__.__name__}({repr(source_list)}) "
                + (OK if t.path.exists() else FAIL)
            )


def encode(tracks: List[Track], threads: int = 1) -> None:
    """
    Take a list of Track objects, and make sure that every Target exists
    """

    def _encode(track: Track):
        try:
            for target in track.targets:
                target.encode()
        except Exception:
            log.exception(f"Error encoding {track.id}")

    tracks_todo = [t for t in tracks if t.needs_work()]
    thread_map(_encode, tracks_todo, max_workers=threads, desc="encode")


def export(processed_dir: Path, tracks: List[Track], threads: int = 1) -> None:
    """
    Take a list of Track objects, and write their metadata into tracks.json
    """

    def _export(track: Track) -> Optional[Dict[str, Any]]:
        try:
            return track.to_json()
        except Exception:
            log.exception(f"Error exporting {track.id}")
            return None

    json_list = thread_map(_export, tracks, max_workers=threads, desc="export")

    data = json.dumps(dict(sorted((t["id"], t) for t in json_list if t)), default=tuple)
    with open(os.path.join(processed_dir, "tracks.json"), "w") as fp:
        fp.write(data)
    with gzip.open(os.path.join(processed_dir, "tracks.json.gz"), "w") as fpz:
        fpz.write(data.encode("utf8"))


def cleanup(
    processed_dir: Path, tracks: List[Track], delete: bool, threads: int = 1
) -> None:
    """
    Delete any files from the processed dir that aren't included in any tracks
    """
    expected = {
        processed_dir / "tracks.json",
        processed_dir / "tracks.json.gz",
    }
    for track in tracks:
        for target in track.targets:
            expected.add(target.path)

    def _cleanup(path: Path) -> None:
        if path.is_file() and path not in expected:
            rel = path.relative_to(processed_dir)
            if delete:
                log.info(f"Cleaning up {rel}")
                path.unlink()
            else:
                log.info(f"{rel} due to be cleaned up")

    files = processed_dir.glob("**/*")
    thread_map(_cleanup, files, max_workers=threads, desc="cleanup")


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("/media/source"),
        metavar="DIR",
        help="Where to find source files (Default: %(default)s)",
    )
    parser.add_argument(
        "--cache",
        type=Path,
        default=Path("/tmp/cache.db"),
        metavar="FILE",
        help="Where to store temporary data (Default: %(default)s)",
    )
    parser.add_argument(
        "--processed",
        type=Path,
        default=Path("/media/processed"),
        metavar="DIR",
        help="Where to place output files (Default: %(default)s)",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=math.ceil((os.cpu_count() or 1) / 4),
        metavar="N",
        help="How many encodes to run in parallel (Default: %(default)s)",
    )
    parser.add_argument(
        "--loop",
        type=int,
        default=None,
        metavar="SECONDS",
        help="Run forever, polling for changes in the source directory this often",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        default=False,
        help="Actually delete files for-real during cleanup",
    )
    parser.add_argument(
        "cmd", nargs="?", help="Sub-process to run (view, encode, export, cleanup)"
    )
    parser.add_argument(
        "match", nargs="?", help="Only act upon files matching this pattern"
    )

    return parser.parse_args()


@contextlib.contextmanager
def _pickled_var(filename: str, default: Any):
    """
    Load a variable from a file on startup,
    save the variable to file on shutdown
    """
    try:
        with open(filename, "rb") as fp:
            var = pickle.loads(fp.read())
    except Exception:
        var = default
    yield var
    with open(filename, "wb") as fp:
        fp.write(pickle.dumps(var))


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    last_source_change = None

    while True:
        source_change = os.stat(args.source).st_mtime
        if source_change != last_source_change:
            last_source_change = source_change

            with _pickled_var(args.cache, {}) as cache:
                with logging_redirect_tqdm():
                    tracks = scan(
                        args.source, args.processed, args.match, cache, args.threads
                    )

                    # If no specific command is specified, then encode,
                    # export, and cleanup with the default settings
                    if args.cmd == None:
                        encode(tracks, args.threads)
                        export(args.processed, tracks, args.threads)
                        cleanup(args.processed, tracks, False, args.threads)
                    elif args.cmd == "view":
                        view(tracks)
                    elif args.cmd == "encode":
                        encode(tracks, args.threads)
                    elif args.cmd == "export":
                        export(args.processed, tracks, args.threads)
                    elif args.cmd == "cleanup":
                        if args.match:
                            raise Exception("Can't use cleanup with --match")
                        cleanup(args.processed, tracks, args.delete, args.threads)

        if args.loop:
            log.info(f"Sleeping for {args.loop}s before checking for new inputs")
            time.sleep(args.loop)
        else:
            break

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))