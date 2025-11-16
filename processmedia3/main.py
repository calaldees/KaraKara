#!/usr/bin/env python3

import argparse
import contextlib
import logging
import logging.handlers
import math
import os
import pickle
import sys
import time
import typing as t
from pathlib import Path
from collections.abc import Sequence, MutableMapping
from typing import TypeVar, Generator

from tqdm.contrib.logging import logging_redirect_tqdm

from lib.source import Source
from lib.track import Track
from lib.kktypes import TargetType
from lib.file_abstraction import AbstractFolder_from_str, LocalFile

from cmds.cleanup import cleanup
from cmds.encode import encode
from cmds.export import export
from cmds.lint import lint
from cmds.scan import scan
from cmds.view import view

log = logging.getLogger()
T = TypeVar("T")


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
    parser.add_argument(
        "match", nargs="?", help="Only act upon files matching this pattern"
    )

    args = parser.parse_args(argv[1:])
    # we need to create AbstractFolder lazily, because
    # `default=AbstractFolder("/blah")` crashes when `/blah`
    # doesn't exist, even when we specify `--source ../media/source`
    args.source = AbstractFolder_from_str(args.source)
    return args


@contextlib.contextmanager
def _pickled_var(path: Path, default: T) -> Generator[T, None, None]:
    """
    Load a variable from a file on startup,
    save the variable to file on shutdown
    """
    try:
        var: T = pickle.loads(path.read_bytes())
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
        handler = logging.handlers.RotatingFileHandler(
            args.log_file, maxBytes=65535, backupCount=3
        )
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
            tracks = tuple(
                track for track in tracks if track.has_tags
            )  # only encode tracks that have a tag.txt file

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
