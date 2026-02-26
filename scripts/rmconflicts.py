#!/usr/bin/env python3
import argparse
import hashlib
import os
import re
import sys

SYNC_CONFLICT_RE = re.compile(
    r"^(?P<base>.+?)\.sync-conflict-\d{8}-\d{6}-(?P<ext>\..+)$"
)


def file_hash(path, algo="sha256", chunk_size=1024 * 1024):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_files(root, recursive):
    if recursive:
        for dirpath, _, filenames in os.walk(root):
            for name in filenames:
                yield dirpath, name
    else:
        for name in os.listdir(root):
            yield root, name


def main():
    parser = argparse.ArgumentParser(
        description="Delete sync-conflict files if they are identical to their base file"
    )
    parser.add_argument("path", help="Directory to scan")
    parser.add_argument(
        "-r", "--recursive", action="store_true", help="Scan directories recursively"
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without deleting",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--hash", default="sha256", help="Hash algorithm to use (default: sha256)"
    )

    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"Not a directory: {args.path}", file=sys.stderr)
        sys.exit(1)

    deleted = 0
    kept = 0

    for dirpath, filename in iter_files(args.path, args.recursive):
        match = SYNC_CONFLICT_RE.match(filename)
        if not match:
            continue

        base_name = match.group("base") + match.group("ext")
        conflict_path = os.path.join(dirpath, filename)
        base_path = os.path.join(dirpath, base_name)

        if not os.path.exists(base_path):
            if args.verbose:
                print(f"Base file missing, skipping: {conflict_path}")
            continue

        try:
            base_hash = file_hash(base_path, algo=args.hash)
            conflict_hash = file_hash(conflict_path, algo=args.hash)
        except OSError as e:
            print(f"Error reading files: {e}", file=sys.stderr)
            continue

        if base_hash == conflict_hash:
            if args.dry_run:
                print(f"[DRY-RUN] Would delete: {conflict_path}")
            else:
                os.remove(conflict_path)
                print(f"Deleted: {conflict_path}")
            deleted += 1
        else:
            kept += 1
            if args.verbose:
                print(f"Different content, kept: {conflict_path}")

    if args.verbose or args.dry_run:
        print(f"\nSummary: {deleted} deleted, {kept} kept")


if __name__ == "__main__":
    main()
