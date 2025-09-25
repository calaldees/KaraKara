#!/usr/bin/env python3

import argparse
import contextlib
import gzip
import json
import logging
import logging.handlers
import math
import os
import pickle
import re
import sys
import time
import typing as t
from datetime import timedelta
from collections import defaultdict
from pathlib import Path
from collections.abc import Sequence, MutableMapping

from tqdm.contrib.concurrent import thread_map
from tqdm.contrib.logging import logging_redirect_tqdm

from lib.source import Source, SourceType
from lib.target import Target
from lib.track import Track, TrackDict, TrackValidationException
from lib.kktypes import TargetType
from lib.file_abstraction import (
    AbstractFolder,
    AbstractFile,
    AbstractFolder_from_str,
    LocalFile,
)


log = logging.getLogger()

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
    "tracks.json.gz",
    "readme.txt",
    "WorkInProgress",
]


def scan(
    source_folder: AbstractFolder,
    processed_dir: Path,
    match: str,
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

    return tuple(
        filter(
            None,
            thread_map(_load_track, groups, max_workers=threads, desc="scan   ", unit="track"),
        )
    )


def view(tracks: Sequence[Track]) -> None:
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
            if t.path.exists():
                stats = f"{OK} ({int(t.path.stat().st_size / 1024):,} KB)"
            else:
                stats = FAIL
            print(f"  - {t} {stats}")


def lint(tracks: Sequence[Track]) -> None:
    """
    Scan through all the data, looking for things which seem suspicious
    and probably want a human to investigate
    """

    def _lint(track: Track) -> None:
        # for t in track.targets:
        #    if not t.path.exists():
        #        log.error(f"{t.friendly} missing (Sources: {[s.file.relative for s in t.sources]!r})")
        for s in track.sources:
            if s.type == SourceType.TAGS:
                for tag in ["title", "category", "vocaltrack", "lang"]:
                    if not s.tags.get(tag):
                        log.error(f"{s.file.relative} has no {tag} tag")

                if s.tags.get("vocaltrack") == ["on"]:
                    if not s.tags.get("vocalstyle"):
                        log.error(f"{s.file.relative} has vocaltrack:on but no vocalstyle")

                use = s.tags.get("use")
                if use:
                    use = [u.lower() for u in use]
                    for n in range(0, 50):
                        if f"op{n}" in use and "opening" not in use:
                            log.error(f"{s.file.relative} has use:op{n} but no opening tag")
                        if f"en{n}" in use and "ending" not in use:
                            log.error(f"{s.file.relative} has use:ed{n} but no ending tag")

                if "source" in s.tags:
                    if "http" in s.tags["source"] or "https" in s.tags["source"]:
                        log.error(f"{s.file.relative} appears to have an unquoted URL in the source tag")

                if "red" in s.tags:
                    log.error(f"{s.file.relative} has red tag")

            if s.type == SourceType.SUBTITLES:
                ls = s.subtitles

                # Check for weird stuff at the file level
                if len(ls) == 0:
                    log.error(f"{s.file.relative} has no subtitles")
                if len(ls) == 1:
                    log.error(f"{s.file.relative} has only one subtitle: {ls[0].text}")

                # Most lines are on the bottom, but there are a random couple on top,
                # normally means that a title line got added
                top_count = len([s for s in ls if s.top])
                if top_count > 0 and top_count / len(ls) < 0.8:
                    log.error(f"{s.file.relative} has random topline")

                # Check for weird stuff at the line level
                for index, l in enumerate(ls):
                    if "\n" in l.text:
                        log.error(f"{s.file.relative}:{index + 1} line contains newline: {l.text}")

                # Check for weird stuff between lines (eg gaps or overlaps)
                # separate out the top and bottom lines because they may have
                # different timing and we only care about timing glitches
                # within the same area of the screen
                toplines = [l for l in ls if l.top]
                botlines = [l for l in ls if not l.top]
                for ls in [toplines, botlines]:
                    for index, (l1, l2, l3) in enumerate(zip(ls[:-1], ls[1:], ls[2:])):
                        if l1.end == l2.start and l2.end == l3.start and (l1.text == l2.text == l3.text):
                            log.error(f"{s.file.relative}:{index + 1} no gap between 3+ repeats: {l1.text}")
                    for index, (l1, l2) in enumerate(zip(ls[:-1], ls[1:])):
                        if l2.start > l1.end:
                            gap = l2.start - l1.end
                            if gap < timedelta(microseconds=100_000) and not (l1.text == l2.text):
                                log.error(
                                    f"{s.file.relative}:{index + 1} blink between lines: {int(gap.microseconds / 1000)}: {l1.text} / {l2.text}"
                                )
                        elif l2.start < l1.end:
                            gap = l1.end - l2.start
                            log.error(
                                f"{s.file.relative}:{index + 1} overlapping lines {int(gap.microseconds / 1000)}: {l1.text} / {l2.text}"
                            )

    thread_map(_lint, tracks, max_workers=4, desc="lint   ", unit="track")


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


def export(
    processed_dir: Path,
    tracks: Sequence[Track],
    update: bool = False,
    threads: int = 1,
) -> None:
    """
    Take a list of Track objects, and write their metadata into tracks.json
    """

    # Exporting a Track to json can take some time, since we also need
    # to read the tags and the subtitle files in order to include those
    # in the index; so do it multi-threaded.
    def _export(track: Track) -> TrackDict | None:
        try:
            return track.to_json()
        except TrackValidationException as e:
            log.error(f"Error exporting {track.id}: {e}")
            return None
        except Exception:
            log.exception(f"Error exporting {track.id}")
            return None

    json_list = thread_map(_export, tracks, max_workers=threads, desc="export ", unit="track")

    # Export in alphabetic order
    json_dict = dict(sorted((t["id"], t) for t in json_list if t))

    try:
        old_tracklist = json.loads((processed_dir / "tracks.json").read_text())
    except Exception:
        old_tracklist = {}

    # If we've only scanned & encoded a few files, then add
    # those entries onto the end of the current tracks, don't
    # replace the whole database.
    if update:
        json_dict = old_tracklist | json_dict

    # Only write if changed - turns a tiny-but-24/7 amount of
    # disk I/O into zero disk I/O
    if old_tracklist != json_dict:
        # Write to temp file then rename, so if the disk fills up then
        # we don't end up with a half-written tracks.json
        data = json.dumps(json_dict, default=tuple).encode("utf8")

        path = processed_dir / "tracks.json"
        path.with_suffix(".tmp").write_bytes(data)
        path.with_suffix(".tmp").rename(path)

        path = processed_dir / "tracks.json.gz"
        path.with_suffix(".tmp").write_bytes(gzip.compress(data))
        path.with_suffix(".tmp").rename(path)


def cleanup(processed_dir: Path, tracks: Sequence[Track], delete: bool, threads: int = 1) -> None:
    """
    Delete any files from the processed dir that aren't included in any tracks
    """
    expected = {processed_dir / n for n in SCAN_IGNORE}
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

    files = list(processed_dir.glob("**/*"))
    thread_map(_cleanup, files, max_workers=threads, desc="cleanup", unit="file")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=str,
        default="/media/source",
        metavar="DIR/URL",
        help="Where to find source files (Default: %(default)s) (can be local path or http path)",
    )
    parser.add_argument(
        "--processed",
        type=Path,  # TODO: AbstractFolder?
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
        help="Run forever, polling for changes in the source directory this often (in seconds)",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        default=False,
        help="Actually delete files for-real during cleanup",
    )
    parser.add_argument(
        "--reencode",
        action="store_true",
        default=False,
        help="Re-encode files, even if they already exist in the processed directory",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Super-extra verbose logging",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        help="Where to write logs to",
    )
    parser.add_argument(
        "cmd",
        default="all",
        nargs="?",
        help="Sub-process to run (view, encode, test-encode, export, lint, cleanup)",
    )
    parser.add_argument("match", nargs="?", help="Only act upon files matching this pattern")

    args = parser.parse_args()
    # we need to create AbstractFolder lazily, because
    # `default=AbstractFolder("/blah")` crashes when `/blah`
    # doesn't exist, even when we specify `--source ../media/source`
    args.source = AbstractFolder_from_str(args.source)
    return args


@contextlib.contextmanager
def _pickled_var(path: Path, default: t.Any):
    """
    Load a variable from a file on startup,
    save the variable to file on shutdown
    """
    try:
        var = pickle.loads(path.read_bytes())
    except Exception as e:
        log.debug(f"Error loading cache: {e}")
        var = default
    yield var
    try:
        path.with_suffix(".tmp").write_bytes(pickle.dumps(var))
        path.with_suffix(".tmp").rename(path)
    except Exception as e:
        log.debug(f"Error saving cache: {e}")


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s %(message)s",
    )
    if args.log_file:
        handler = logging.handlers.RotatingFileHandler(args.log_file, maxBytes=65535, backupCount=3)
        logging.getLogger().addHandler(handler)

    if args.cmd == "test-encode":
        with logging_redirect_tqdm():
            cache: MutableMapping[str, t.Any] = {}
            path = Path(args.match)
            local_file = LocalFile(path, path.parent)
            tracks: Sequence[Track] = [
                Track(
                    local_file.root,
                    local_file.stem,
                    {Source(local_file, cache)},
                    [
                        TargetType.VIDEO_H264,
                        TargetType.VIDEO_AV1,
                        TargetType.VIDEO_H265,
                    ],
                )
            ]
            encode(tracks, args.reencode, args.threads)
            return 0

    while True:
        with (
            _pickled_var(args.processed / "cache.db", {}) as cache,
            logging_redirect_tqdm(),
        ):
            tracks = scan(args.source, args.processed, args.match, cache, args.threads)
            tracks = tuple(track for track in tracks if track.has_tags)  # only encode tracks that have a tag.txt file

            # If no specific command is specified, then encode,
            # export, and cleanup with the default settings
            update = args.match is not None
            if args.cmd == "all":
                encode(tracks, args.reencode, args.threads)
                export(args.processed, tracks, update, args.threads)
                if not args.match:
                    cleanup(args.processed, tracks, args.delete, args.threads)
            elif args.cmd == "view":
                view(tracks)
            elif args.cmd == "lint":
                lint(tracks)
            elif args.cmd == "encode":
                encode(tracks, args.reencode, args.threads)
            elif args.cmd == "export":
                export(args.processed, tracks, update, args.threads)
            elif args.cmd == "cleanup":
                if args.match:
                    raise ValueError("Can't use cleanup with --match")
                cleanup(args.processed, tracks, args.delete, args.threads)

        if args.loop:
            log.info(f"Sleeping for {args.loop}s before checking for new inputs")
            time.sleep(args.loop)
        else:
            break

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
