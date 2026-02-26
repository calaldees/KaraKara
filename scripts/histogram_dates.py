#!/usr/bin/env python3
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def get_year_from_track(track_data):
    """Extract year from track's date or year field.

    Returns (year, tags) tuple or (None, tags) if no valid year found.
    """
    tags = track_data.get("tags", {})

    # Try to get year from 'year' field first
    if "year" in tags and tags["year"]:
        year_values = tags["year"]
        if isinstance(year_values, list) and year_values:
            try:
                year = int(year_values[0])
                return year, tags
            except ValueError:
                pass

    # Try to get year from 'date' field
    if "date" in tags and tags["date"]:
        date_values = tags["date"]
        if isinstance(date_values, list) and date_values:
            date_str = date_values[0]
            # Extract year from date (assumes format like YYYY-MM-DD or YYYY)
            year_str = date_str.split("-")[0]
            try:
                year = int(year_str)
                return year, tags
            except ValueError:
                pass

    return None, tags


def has_tag(tags, tag_to_find):
    """Check if tags dict contains the specified tag in any category."""
    if not tag_to_find:
        return False

    tag_lower = tag_to_find.lower()

    # Check if tag exists as a key
    if tag_lower in tags:
        return True

    # Check if tag exists as a value in any tag category
    for category, values in tags.items():
        if isinstance(values, list):
            if any(tag_lower == str(v).lower() for v in values):
                return True
        elif tag_lower == str(values).lower():
            return True

    return False


def print_histogram(year_counts_all, year_counts_filtered, tag, mode):
    """Print histogram of years with partial coloring.

    Args:
        year_counts_all: Dictionary of year -> count for all tracks
        year_counts_filtered: Dictionary of year -> count for filtered tracks
        tag: Tag being filtered by (or None)
        mode: 'include' or 'exclude'
    """
    if not year_counts_all:
        print("No tracks with dates found.")
        return

    # Find the maximum count for scaling
    max_count = max(year_counts_all.values())
    max_bar_width = 72

    # Sort years
    sorted_years = sorted(year_counts_all.keys())

    # ANSI color codes
    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"

    # Print header
    total_all = sum(year_counts_all.values())
    total_filtered = sum(year_counts_filtered.values())

    if mode == "include":
        filter_desc = f" (green = with '{tag}' tag, white = without)"
        color = GREEN
    elif mode == "exclude":
        filter_desc = f" (white = without '{tag}' tag, red = with)"
        color = RED
    else:
        filter_desc = ""
        color = ""

    print(f"\nHistogram of release years{filter_desc}:")
    print(f"Total tracks with dates: {total_all}")
    if mode in ["include", "exclude"]:
        print(f"Tracks matching filter: {total_filtered}\n")
    else:
        print()

    # Print histogram
    for year in sorted_years:
        count_all = year_counts_all[year]
        count_filtered = year_counts_filtered.get(year, 0)

        # Scale bar width
        bar_width_all = (
            int((count_all / max_count) * max_bar_width) if max_count > 0 else 0
        )
        bar_width_filtered = (
            int((count_filtered / max_count) * max_bar_width) if max_count > 0 else 0
        )

        if mode == "include":
            # Green part at the start for included tracks
            bar_colored = color + "█" * bar_width_filtered + RESET
            bar_uncolored = "█" * (bar_width_all - bar_width_filtered)
            bar = bar_colored + bar_uncolored
            count_display = f"{count_filtered}/{count_all}"
        elif mode == "exclude":
            # White part at start for non-excluded tracks, red at end for excluded
            count_unfiltered = count_all - count_filtered
            bar_width_unfiltered = (
                int((count_unfiltered / max_count) * max_bar_width)
                if max_count > 0
                else 0
            )
            bar_uncolored = "█" * bar_width_unfiltered
            bar_colored = color + "█" * (bar_width_all - bar_width_unfiltered) + RESET
            bar = bar_uncolored + bar_colored
            count_display = f"{count_unfiltered}/{count_all}"
        else:
            # No filtering, just show all
            bar = "█" * bar_width_all
            count_display = str(count_all)

        print(f"{year}: {bar} {count_display}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a histogram of track release years from tracks.json.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s tracks.json
  %(prog)s tracks.json --include retro
  %(prog)s tracks.json --exclude anime
        """,
    )

    parser.add_argument(
        "tracks_json",
        type=Path,
        nargs="?",
        default=Path("tracks.json"),
        help="Path to tracks.json file (default: ./tracks.json)",
    )

    filter_group = parser.add_mutually_exclusive_group()
    filter_group.add_argument(
        "--include",
        metavar="TAG",
        help="Show tracks with the specified tag highlighted (green portion of bar)",
    )
    filter_group.add_argument(
        "--exclude",
        metavar="TAG",
        help="Show tracks without the specified tag highlighted (red portion of bar)",
    )

    args = parser.parse_args()

    if not args.tracks_json.exists():
        print(f"Error: {args.tracks_json} does not exist", file=sys.stderr)
        sys.exit(1)

    if not args.tracks_json.is_file():
        print(f"Error: {args.tracks_json} is not a file", file=sys.stderr)
        sys.exit(1)

    # Determine mode and tag
    if args.include:
        mode = "include"
        tag = args.include
    elif args.exclude:
        mode = "exclude"
        tag = args.exclude
    else:
        mode = "all"
        tag = None

    # Load tracks.json
    try:
        with open(args.tracks_json, "r", encoding="utf-8") as f:
            tracks = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to read file: {e}", file=sys.stderr)
        sys.exit(1)

    year_counts_all = defaultdict(int)
    year_counts_filtered = defaultdict(int)

    for track_id, track_data in tracks.items():
        year, tags = get_year_from_track(track_data)

        if year is None:
            continue

        # Count all tracks with valid years
        year_counts_all[year] += 1

        # Count filtered tracks
        if mode == "include":
            if has_tag(tags, tag):
                year_counts_filtered[year] += 1
        elif mode == "exclude":
            if not has_tag(tags, tag):
                year_counts_filtered[year] += 1
        else:
            # For "all" mode, filtered counts equal all counts
            year_counts_filtered[year] += 1

    print_histogram(year_counts_all, year_counts_filtered, tag, mode)


if __name__ == "__main__":
    main()
