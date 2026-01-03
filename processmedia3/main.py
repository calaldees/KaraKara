#!/usr/bin/env python3
import contextlib
import logging
import logging.handlers
import math
import os
import pickle
import sys
import typing as t
from collections.abc import Generator, Sequence
from pathlib import Path

import tap
from tqdm.contrib.logging import logging_redirect_tqdm

from pm3.cmds.cleanup import cleanup
from pm3.cmds.encode import encode
from pm3.cmds.export import export
from pm3.cmds.lint import lint
from pm3.cmds.scan import scan
from pm3.cmds.status import status
from pm3.lib.file_abstraction import AbstractFolder

log = logging.getLogger()


class PM3Args(tap.Tap):
    # fmt: off
    source: AbstractFolder  # Where to find source files (can be local path or http path)
    processed: Path  # Where to place output files
    threads: int = math.ceil((os.cpu_count() or 1) / 4)  # How many encodes to run in parallel
    loop: int | None = None  # Run forever, polling for changes in the source directory this often (in seconds)
    delete: bool = False  # Actually delete files for-real during cleanup
    reencode: bool = False  # Re-encode files, even if they already exist in the processed directory
    debug: bool = False  # Super-extra verbose logging
    log_file: Path | None = None  # Where to write logs to
    cmd: t.Literal["all", "status", "encode", "export", "lint", "cleanup"] = "all"  # Sub-process to run
    match: str | None = None  # Only act upon files matching this pattern
    # fmt: on

    def configure(self) -> None:
        self.add_argument("cmd", nargs="?")
        self.add_argument("match", nargs="?")
        self.add_argument("--source", type=AbstractFolder.from_str)


@contextlib.contextmanager
def _pickled_var(path: Path) -> Generator[dict[str, t.Any], None, None]:
    """
    Load a variable from a file on startup,
    save the variable to file on shutdown
    """
    try:
        var = pickle.loads(path.read_bytes())
    except Exception as e:
        log.debug(f"Error loading cache: {e}")
        var = {}
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
    for _ in args.source.watch(args.loop):
        with _pickled_var(args.processed / "cache.db") as cache:
            tracks = scan(
                args.source,
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
