#!/usr/bin/env python3
import contextlib
import logging
import logging.handlers
import math
import os
import pickle
import sys
import typing as t
from collections.abc import Generator, MutableMapping, Sequence
from pathlib import Path
from this import d
from typing import TypeVar

import tap
from tqdm.contrib.logging import logging_redirect_tqdm

from pm3.cmds.cleanup import cleanup
from pm3.cmds.encode import encode
from pm3.cmds.export import export
from pm3.cmds.lint import lint
from pm3.cmds.scan import scan
from pm3.cmds.status import status
from pm3.lib.file_abstraction import AbstractFolder, LocalFile
from pm3.lib.kktypes import TargetType
from pm3.lib.source import Source
from pm3.lib.track import Track

log = logging.getLogger()
T = TypeVar("T")


class PM3Args(tap.Tap):
    # fmt: off
    source: str = "/media/source"  # Where to find source files (can be local path or http path)
    processed: Path = Path("/media/processed")  # Where to place output files
    threads: int = math.ceil((os.cpu_count() or 1) / 4)  # How many encodes to run in parallel
    loop: int | None = None  # Run forever, polling for changes in the source directory this often (in seconds)
    delete: bool = False  # Actually delete files for-real during cleanup
    reencode: bool = False  # Re-encode files, even if they already exist in the processed directory
    debug: bool = False  # Super-extra verbose logging
    log_file: Path | None = None  # Where to write logs to
    cmd: str | None = "all"  # Sub-process to run (status, encode, test-encode, export, lint, cleanup)
    match: str | None = None  # Only act upon files matching this pattern
    # fmt: on

    def configure(self) -> None:
        cmds = ["all", "status", "encode", "export", "lint", "cleanup", "test-encode"]
        self.add_argument("cmd", nargs="?", choices=cmds)
        self.add_argument("match", nargs="?", default=None)
        self.add_argument("--log-file", type=Path, default=None)


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
    """
    Argument parsing / logging / setup / error handling
    """
    try:
        args = PM3Args().parse_args(argv[1:])

        logging.basicConfig(
            level=logging.DEBUG if args.debug else logging.INFO,
            format="%(asctime)s %(message)s",
        )
        if args.log_file:
            handler = logging.handlers.RotatingFileHandler(args.log_file, maxBytes=65535, backupCount=3)
            logging.getLogger().addHandler(handler)

        with logging_redirect_tqdm():
            return _main(args)
    except KeyboardInterrupt:
        return 130


def _main(args: PM3Args) -> int:
    """
    Main program logic
    """
    if args.cmd == "test-encode":
        if args.match is None:
            raise ValueError("test-encode requires --match to be specified")
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

    source = AbstractFolder.from_str(args.source)
    assert source is not None, f"Could not open source folder {args.source}"
    for _ in source.watch(args.loop):
        with _pickled_var(args.processed / "cache.db", {}) as cache:
            tracks = scan(
                source,
                args.processed,
                args.match,
                cache,
                args.threads,
            )
            # only encode tracks that have a tag.txt file
            tracks = [track for track in tracks if track.has_tags]

            # If no specific command is specified, then encode,
            # export, and cleanup with the default settings
            update = args.match is not None
            if args.cmd == "all":
                encode(tracks, args.reencode, args.threads)
                export(args.processed, tracks, update, args.threads)
                if not args.match:
                    cleanup(args.processed, tracks, args.delete, args.threads)
            elif args.cmd == "status":
                status(tracks)
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

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
