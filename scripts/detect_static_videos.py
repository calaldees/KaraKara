#!/usr/bin/env python3
"""
Detect videos with no motion (static frames) and optionally extract audio + image.

This script analyzes videos to find those that are essentially static images
with audio, such as when a JPEG is transcoded into a long h264 video.
"""

import argparse
import json
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Generator, Optional, Tuple

from tqdm import tqdm

CACHE_FILE = Path("./detect_static_videos_cache.db")


def init_cache_db() -> None:
    """Initialize the cache database with the required schema."""
    conn = sqlite3.connect(CACHE_FILE, timeout=30.0)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS video_cache (
                path TEXT PRIMARY KEY,
                frozen_percentage REAL NOT NULL,
                duration REAL NOT NULL,
                size INTEGER NOT NULL,
                mtime REAL NOT NULL,
                scan_time REAL NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def get_cache_entry(video_path: Path) -> Optional[Dict[str, Any]]:
    """Get a single cache entry from the database."""
    conn = sqlite3.connect(CACHE_FILE, timeout=30.0)
    try:
        cursor = conn.execute(
            "SELECT frozen_percentage, duration, size, mtime, scan_time FROM video_cache WHERE path = ?",
            (str(video_path.absolute()),),
        )
        row = cursor.fetchone()
        if row:
            return {
                "frozen_percentage": row[0],
                "duration": row[1],
                "size": row[2],
                "mtime": row[3],
                "scan_time": row[4],
            }
        return None
    finally:
        conn.close()


def save_cache_entry(video_path: Path, entry: Dict[str, Any]) -> None:
    """Save a single cache entry to the database."""
    conn = sqlite3.connect(CACHE_FILE, timeout=30.0)
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO video_cache (path, frozen_percentage, duration, size, mtime, scan_time)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(video_path.absolute()),
                entry["frozen_percentage"],
                entry["duration"],
                entry["size"],
                entry["mtime"],
                entry["scan_time"],
            ),
        )
        conn.commit()
    finally:
        conn.close()


def get_cache_stats() -> Dict[str, Any]:
    """Get statistics about the cache."""
    if not CACHE_FILE.exists():
        return {"count": 0, "entries": []}

    conn = sqlite3.connect(CACHE_FILE, timeout=30.0)
    try:
        cursor = conn.execute("SELECT COUNT(*) FROM video_cache")
        count = cursor.fetchone()[0]

        cursor = conn.execute(
            "SELECT path, frozen_percentage, scan_time FROM video_cache ORDER BY path"
        )
        entries = []
        for row in cursor:
            entries.append(
                {
                    "path": row[0],
                    "frozen_percentage": row[1],
                    "scan_time": row[2],
                }
            )

        return {"count": count, "entries": entries}
    finally:
        conn.close()


def clear_cache() -> None:
    """Clear all entries from the cache."""
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()


def get_file_metadata(video_path: Path) -> Dict[str, float]:
    """Get file metadata for cache validation."""
    stat = video_path.stat()
    return {
        "size": stat.st_size,
        "mtime": stat.st_mtime,
    }


def is_cache_valid(cache_entry: Dict[str, Any], video_path: Path) -> bool:
    """Check if a cache entry is still valid."""
    try:
        metadata = get_file_metadata(video_path)
        return (
            cache_entry.get("size") == metadata["size"]
            and cache_entry.get("mtime") == metadata["mtime"]
        )
    except OSError:
        return False


def run_command(
    cmd: list[str], capture_output: bool = True
) -> Optional[subprocess.CompletedProcess]:
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(cmd)}", file=sys.stderr)
        print(f"Error: {e.stderr}", file=sys.stderr)
        return None


def check_ffmpeg_installed() -> bool:
    """Check if ffmpeg and ffprobe are installed."""
    for tool in ["ffmpeg", "ffprobe"]:
        result = subprocess.run(
            ["which", tool],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            print(f"Error: {tool} is not installed or not in PATH", file=sys.stderr)
            return False
    return True


def get_video_info(video_path: Path) -> Optional[Dict[str, Any]]:
    """Get video stream information using ffprobe."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=codec_name,width,height,nb_frames,duration:format=duration",
        "-of",
        "json",
        str(video_path),
    ]

    result = run_command(cmd)
    if not result:
        return None

    try:
        data = json.loads(result.stdout)
        if "streams" in data and len(data["streams"]) > 0:
            stream_info = data["streams"][0]
            # If stream doesn't have duration, try to get it from format
            if "duration" not in stream_info or stream_info.get("duration") == "N/A":
                if "format" in data and "duration" in data["format"]:
                    stream_info["duration"] = data["format"]["duration"]
            return stream_info
    except json.JSONDecodeError:
        print(f"Error parsing ffprobe output for {video_path}", file=sys.stderr)

    return None


def get_audio_codec(video_path: Path) -> Optional[str]:
    """Get the audio codec name from a video file."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "a:0",
        "-show_entries",
        "stream=codec_name",
        "-of",
        "json",
        str(video_path),
    ]

    result = run_command(cmd)
    if not result:
        return None

    try:
        data = json.loads(result.stdout)
        if "streams" in data and len(data["streams"]) > 0:
            return data["streams"][0].get("codec_name")
    except json.JSONDecodeError:
        return None

    return None


def get_audio_extension(codec_name: str) -> str:
    """Map audio codec name to file extension."""
    codec_to_ext = {
        "aac": "m4a",
        "mp3": "mp3",
        "vorbis": "ogg",
        "opus": "opus",
        "flac": "flac",
        "pcm_s16le": "wav",
        "pcm_s24le": "wav",
        "pcm_s32le": "wav",
        "alac": "m4a",
        "wmav2": "wma",
        "ac3": "ac3",
        "eac3": "eac3",
        "dts": "dts",
        "truehd": "thd",
        "mp2": "mp2",
    }

    return codec_to_ext.get(codec_name, "audio")


def calculate_frozen_percentage(
    video_path: Path,
    noise_threshold: int = -60,
    min_duration: float = 0.5,
    verbose: bool = False,
    use_cache: bool = True,
) -> float:
    """
    Calculate what percentage of a video is frozen/static.

    Args:
        video_path: Path to the video file
        noise_threshold: Noise threshold in dB (default: -60dB)
        min_duration: Minimum freeze duration to count (default: 0.5s)
        verbose: Print detailed information
        use_cache: Whether to use cached results (default: True)

    Returns:
        float: Percentage of video that is frozen (0-100)

    Raises:
        RuntimeError: If video info cannot be retrieved or duration is invalid
    """
    video_path = Path(video_path)

    # Check cache first
    if use_cache:
        cache_entry = get_cache_entry(video_path)
        if cache_entry and is_cache_valid(cache_entry, video_path):
            if verbose:
                print(f"  [CACHED] Frozen: {cache_entry['frozen_percentage']:.1f}%")
            return cache_entry["frozen_percentage"]

    # Get video duration
    info = get_video_info(video_path)
    if not info:
        raise RuntimeError(f"Failed to get video info for {video_path}")

    try:
        duration_value = info.get("duration")
        if duration_value is None or duration_value == "N/A":
            raise RuntimeError(f"Video has no duration metadata: {video_path}")
        duration = float(duration_value)
        if duration == 0:
            raise RuntimeError(f"Video has zero duration: {video_path}")
    except (ValueError, TypeError) as e:
        raise RuntimeError(
            f"Video has invalid duration value '{duration_value}': {video_path}"
        ) from e

    # Use freezedetect to find all frozen sections
    cmd = [
        "ffmpeg",
        "-i",
        str(video_path),
        "-vf",
        f"freezedetect=n={noise_threshold}dB:d={min_duration}",
        "-f",
        "null",
        "-",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    # Parse freeze durations from stderr
    stderr = result.stderr
    total_frozen_time = 0.0

    for line in stderr.split("\n"):
        if "lavfi.freezedetect.freeze_duration:" in line:
            try:
                duration_str = line.split("lavfi.freezedetect.freeze_duration:")[
                    1
                ].strip()
                frozen_duration = float(duration_str)
                total_frozen_time += frozen_duration
            except IndexError, ValueError:
                continue

    frozen_percentage = (total_frozen_time / duration) * 100

    if verbose:
        print(
            f"  Duration: {duration:.2f}s, Frozen time: {total_frozen_time:.2f}s, Frozen: {frozen_percentage:.1f}%"
        )

    # Update cache
    if use_cache:
        metadata = get_file_metadata(video_path)
        save_cache_entry(
            video_path,
            {
                "frozen_percentage": frozen_percentage,
                "duration": duration,
                "size": metadata["size"],
                "mtime": metadata["mtime"],
                "scan_time": time.time(),
            },
        )

    return frozen_percentage


def extract_audio_and_image(
    video_path: Path,
    output_dir: Optional[str] = None,
    dry_run: bool = False,
    verbose: bool = False,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract audio (stream copy with correct extension) and first frame to .jpg from a video.

    Args:
        video_path: Path to input video
        output_dir: Directory for output files (default: same as video)
        dry_run: If True, don't actually extract, just show what would be done
        verbose: Print detailed information

    Returns:
        tuple: (audio_path, image_path) or (None, None) on failure
    """
    video_path = Path(video_path)

    output_path: Path
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = video_path.parent

    base_name = video_path.stem
    image_path_obj = output_path / f"{base_name}.jpg"

    # Get audio codec to determine correct extension
    audio_codec = get_audio_codec(video_path)

    audio_path_obj: Optional[Path]
    if audio_codec:
        audio_ext = get_audio_extension(audio_codec)
        audio_path_obj = output_path / f"{base_name}.{audio_ext}"
    else:
        audio_path_obj = None

    if dry_run:
        print(f"[DRY-RUN] Would extract from {video_path}:")
        if audio_path_obj:
            print(f"  Audio ({audio_codec}) -> {audio_path_obj}")
        else:
            print(f"  No audio stream found")
        print(f"  Image -> {image_path_obj}")
        return str(audio_path_obj) if audio_path_obj else None, str(image_path_obj)

    # Extract audio
    if audio_codec:
        cmd = [
            "ffmpeg",
            "-i",
            str(video_path),
            "-vn",  # No video
            "-acodec",
            "copy",  # Stream copy (no re-encoding)
            "-y",  # Overwrite output file
            str(audio_path_obj),
        ]

        if verbose:
            print(f"Extracting audio ({audio_codec}) to {audio_path_obj}...")

        result = run_command(cmd, capture_output=not verbose)
        if not result:
            print(f"Failed to extract audio from {video_path}", file=sys.stderr)
            audio_path_obj = None
    else:
        if verbose:
            print(f"No audio stream found in {video_path}")
        audio_path_obj = None

    # Extract first frame
    cmd = [
        "ffmpeg",
        "-i",
        str(video_path),
        "-vframes",
        "1",  # Extract one frame
        "-q:v",
        "2",  # High quality JPEG
        "-y",  # Overwrite
        str(image_path_obj),
    ]

    if verbose:
        print(f"Extracting image to {image_path_obj}...")

    result = run_command(cmd, capture_output=not verbose)
    if not result:
        print(f"Failed to extract image from {video_path}", file=sys.stderr)
        image_path_obj = None

    return str(audio_path_obj) if audio_path_obj else None, str(
        image_path_obj
    ) if image_path_obj else None


def find_videos(path: Path, recursive: bool = True) -> Generator[Path, None, None]:
    """Find all video files in a directory."""
    video_extensions = {
        ".mp4",
        ".mkv",
        ".avi",
        ".mov",
        ".flv",
        ".wmv",
        ".webm",
        ".m4v",
        ".mpg",
        ".mpeg",
        ".3gp",
        ".ogv",
    }

    path = Path(path)

    if path.is_file():
        if path.suffix.lower() in video_extensions:
            yield path
        return

    if recursive:
        for video_path in path.rglob("*"):
            if video_path.is_file() and video_path.suffix.lower() in video_extensions:
                yield video_path
    else:
        for video_path in path.iterdir():
            if video_path.is_file() and video_path.suffix.lower() in video_extensions:
                yield video_path


def parse_threshold(threshold_str: str) -> Tuple[float, float]:
    """Parse threshold string into min and max values.

    Args:
        threshold_str: Either a single number (e.g., "90") or a range (e.g., "80-90")

    Returns:
        Tuple of (min_threshold, max_threshold)
        For single value "90", returns (90, 100)
        For range "80-90", returns (80, 90)
    """
    if "-" in threshold_str:
        parts = threshold_str.split("-")
        if len(parts) != 2:
            raise ValueError(f"Invalid threshold range format: {threshold_str}")
        min_val = float(parts[0])
        max_val = float(parts[1])
        if min_val >= max_val:
            raise ValueError(
                f"Invalid threshold range: min ({min_val}) must be less than max ({max_val})"
            )
        if min_val < 0 or max_val > 100:
            raise ValueError(f"Threshold values must be between 0 and 100")
        return min_val, max_val
    else:
        val = float(threshold_str)
        if val < 0 or val > 100:
            raise ValueError(f"Threshold value must be between 0 and 100")
        return val, 100.0


def interactive_convert_videos(
    folder: Path,
    threshold_min: float = 95.0,
    threshold_max: float = 100.0,
    use_cache: bool = True,
) -> None:
    """Interactive mode to manually review and convert videos detected as static

    Args:
        folder: Directory to scan for videos
        threshold_min: Minimum frozen frame percentage threshold (0-100)
        threshold_max: Maximum frozen frame percentage threshold (0-100)
        use_cache: Whether to use cached motion detection results
    """
    folder = folder.expanduser()

    if not folder.exists():
        print(f"Error: Folder not found: {folder}")
        return

    video_extensions = [".mkv", ".mp4", ".avi", ".mov", ".webm", ".flv", ".wmv", ".m4v"]
    video_files = []

    # Find all video files
    print(f"Scanning for videos in: {folder}")
    for ext in video_extensions:
        video_files.extend(folder.rglob(f"*{ext}"))

    if not video_files:
        print(f"No video files found in {folder}")
        return

    print(f"\nFound {len(video_files)} video file(s)")
    if threshold_min == threshold_max:
        print(f"Analyzing videos for motion (threshold: {threshold_min}% frozen)...")
    else:
        print(
            f"Analyzing videos for motion (threshold: {threshold_min}-{threshold_max}% frozen)..."
        )
    print("=" * 60)

    # First pass: detect which videos are static
    static_videos = []
    for video_path in tqdm(
        sorted(video_files), desc="Detecting static videos", unit="video"
    ):
        try:
            relative_path = video_path.relative_to(folder)
        except ValueError:
            relative_path = video_path

        # Check if audio+image already exist
        if False:
            audio_codec = get_audio_codec(video_path)
            if audio_codec:
                audio_ext = get_audio_extension(audio_codec)
                audio_path = video_path.with_suffix(f".{audio_ext}")
            else:
                audio_path = video_path.with_suffix(".opus")
            image_path = video_path.with_suffix(".jpg")

            if audio_path.exists() and image_path.exists():
                continue

        # Check if video is static
        try:
            frozen_percentage = calculate_frozen_percentage(
                video_path, verbose=False, use_cache=use_cache
            )
            if threshold_min <= frozen_percentage <= threshold_max:
                static_videos.append((video_path, frozen_percentage))
        except Exception as e:
            tqdm.write(f"Error analyzing {relative_path}: {e}")
            continue

    if not static_videos:
        if threshold_min == threshold_max:
            print(f"\nNo static videos found (threshold: {threshold_min}%)")
        else:
            print(
                f"\nNo static videos found (threshold: {threshold_min}-{threshold_max}%)"
            )
        return

    print(f"\nFound {len(static_videos)} static video(s) to review")
    print("=" * 60)

    converted_count = 0
    skipped_count = 0

    for idx, (video_path, frozen_percentage) in enumerate(static_videos, 1):
        try:
            relative_path = video_path.relative_to(folder)
        except ValueError:
            relative_path = video_path

        print(f"\n[{idx}/{len(static_videos)}] {relative_path}")
        print(f"  Static score: {frozen_percentage:.1f}% frozen")

        # Play the video with mpv
        print("  Playing video with mpv (press 'q' to close)...")
        try:
            subprocess.run(["mpv", str(video_path), "--loop=no"], check=False)
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            print(f"Converted: {converted_count}, Skipped: {skipped_count}")
            return

        # Ask user what to do
        while True:
            response = (
                input("\n  Convert to audio+image and delete video? [y/n/q]: ")
                .strip()
                .lower()
            )

            if response == "q":
                print("\nExiting interactive mode")
                print(f"Converted: {converted_count}, Skipped: {skipped_count}")
                return
            elif response == "n":
                print("  → Keeping video as-is")
                skipped_count += 1
                break
            elif response == "y":
                # Extract audio and image
                print("  Extracting audio and image...")
                audio_str, image_str = extract_audio_and_image(
                    video_path, output_dir=None, dry_run=False, verbose=True
                )

                if audio_str is not None and image_str is not None:
                    # Convert strings to Path objects and verify files were created successfully
                    audio_path_extracted = Path(audio_str)
                    image_path_extracted = Path(image_str)
                    if audio_path_extracted.exists() and image_path_extracted.exists():
                        # Delete original video
                        # try:
                        #    video_path.unlink()
                        #    print(f"  ✓ Converted and deleted original video")
                        # except Exception as e:
                        #    print(f"  ✗ Error deleting video: {e}")
                        #    print(f"    Audio and image were created successfully")
                        converted_count += 1
                    else:
                        print(f"  ✗ Extraction failed - files not created")
                        skipped_count += 1
                else:
                    print(f"  ✗ Extraction failed")
                    skipped_count += 1
                break
            else:
                print("  Invalid response. Please enter 'y', 'n', or 'q'")

    print("\n" + "=" * 60)
    print(f"Conversion complete!")
    print(f"Converted: {converted_count}")
    print(f"Skipped: {skipped_count}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Detect videos with no motion and optionally extract audio + image"
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="Video file or directory to scan",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        default=True,
        help="Scan directories recursively (default: True)",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_false",
        dest="recursive",
        help="Don't scan directories recursively",
    )
    parser.add_argument(
        "-e",
        "--extract",
        action="store_true",
        help="Extract audio (stream copy with correct extension) and image (.jpg) from static videos",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        help="Output directory for extracted files (default: same as video)",
    )
    parser.add_argument(
        "--delete-original",
        action="store_true",
        help="Delete the original video file after successful extraction (requires --extract)",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually doing it",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Quiet mode - only show static videos and errors",
    )
    parser.add_argument(
        "-t",
        "--threshold",
        type=str,
        default="95",
        help="Frozen frame percentage threshold. Can be a single value (e.g., '90' for >=90%%) or a range (e.g., '80-90' for 80-90%%). Default: 95",
    )
    parser.add_argument(
        "-f",
        "--filter",
        type=str,
        help="Only process files whose names contain this string (case insensitive)",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Don't use cached results, always recalculate",
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear the cache and exit",
    )
    parser.add_argument(
        "--cache-info",
        action="store_true",
        help="Show cache information and exit",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Interactive mode: manually review each video and decide whether to convert",
    )

    args = parser.parse_args()

    # Validate delete-original requires extract
    if args.delete_original and not args.extract:
        print("Error: --delete-original requires --extract", file=sys.stderr)
        sys.exit(1)

    # Handle cache management commands
    if args.clear_cache:
        clear_cache()
        print(f"Cache cleared: {CACHE_FILE}")
        sys.exit(0)

    if args.cache_info:
        stats = get_cache_stats()
        print(f"Cache file: {CACHE_FILE}")
        print(f"Cache entries: {stats['count']}")
        if stats["entries"]:
            print("\nCached videos:")
            for entry in stats["entries"]:
                scan_time = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(entry["scan_time"])
                )
                print(
                    f"  {entry['frozen_percentage']:4.1f}% - {entry['path']} (scanned: {scan_time})"
                )
        sys.exit(0)

    # Interactive mode
    if args.interactive:
        if not args.path:
            print(
                "Error: path argument is required for interactive mode", file=sys.stderr
            )
            sys.exit(1)

        # Check dependencies
        if not check_ffmpeg_installed():
            sys.exit(1)

        path = Path(args.path)
        if not path.exists():
            print(f"Error: Path does not exist: {path}", file=sys.stderr)
            sys.exit(1)

        # Initialize cache database if needed
        use_cache = not args.no_cache
        if use_cache:
            init_cache_db()

        # Parse threshold
        try:
            threshold_min, threshold_max = parse_threshold(args.threshold)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        interactive_convert_videos(path, threshold_min, threshold_max, use_cache)
        sys.exit(0)

    # Validate path is provided for non-cache commands
    if not args.path:
        print("Error: path argument is required", file=sys.stderr)
        sys.exit(1)

    # Check dependencies
    if not check_ffmpeg_installed():
        sys.exit(1)

    # Validate path
    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path does not exist: {path}", file=sys.stderr)
        sys.exit(1)

    # Parse threshold
    try:
        threshold_min, threshold_max = parse_threshold(args.threshold)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Initialize cache database
    use_cache = not args.no_cache
    if use_cache:
        init_cache_db()

    cache_hits = 0
    cache_misses = 0

    # Find and process videos
    static_videos: Dict[Path, float] = {}

    print(f"Scanning for videos in: {path}")
    if args.verbose:
        print(f"Recursive: {args.recursive}")
        if threshold_min == threshold_max:
            print(f"Frozen threshold: {threshold_min}%")
        else:
            print(f"Frozen threshold: {threshold_min}-{threshold_max}%")
        if use_cache:
            stats = get_cache_stats()
            print(f"Cache: enabled ({stats['count']} entries)")
        else:
            print(f"Cache: disabled")
        print()

    # Collect all videos first to get total count for progress bar
    video_list = list(find_videos(path, args.recursive))

    # Apply filter if specified
    if args.filter:
        filter_lower = args.filter.lower()
        original_count = len(video_list)
        video_list = [v for v in video_list if filter_lower in v.name.lower()]
        if args.verbose:
            print(
                f"Filter: '{args.filter}' (matched {len(video_list)}/{original_count} videos)"
            )
        else:
            print(f"Filter: '{args.filter}' ({len(video_list)} matches)")

    total_videos = len(video_list)

    # Process videos with progress bar
    base_path = Path(args.path)
    for video_path in tqdm(
        video_list, desc="Processing videos", unit="video", disable=args.quiet
    ):
        # Calculate relative path for display
        try:
            video_path_rel = video_path.relative_to(base_path)
        except ValueError:
            video_path_rel = video_path

        if args.verbose:
            tqdm.write(f"Checking: {video_path_rel}")

        # Check if this was a cache hit
        was_cached = False
        if use_cache:
            cache_entry = get_cache_entry(video_path)
            if cache_entry and is_cache_valid(cache_entry, video_path):
                was_cached = True

        if was_cached:
            cache_hits += 1
        else:
            cache_misses += 1

        try:
            frozen_percentage = calculate_frozen_percentage(
                video_path,
                verbose=args.verbose,
                use_cache=use_cache,
            )
        except Exception as e:
            if args.verbose:
                tqdm.write(f"  Error: {e}")
            else:
                tqdm.write(f"{video_path_rel} [ERROR: {e}]")
            continue

        is_static = threshold_min <= frozen_percentage <= threshold_max

        if is_static:
            if args.verbose:
                tqdm.write(f"  Result: STATIC ({frozen_percentage:.1f}%)")
            elif not args.quiet:
                tqdm.write(f"{video_path_rel} [STATIC: {frozen_percentage:.1f}%]")
            else:
                tqdm.write(f"{video_path_rel}")

            static_videos[video_path] = frozen_percentage

            if args.extract:
                audio_path, image_path = extract_audio_and_image(
                    video_path,
                    args.output_dir,
                    args.dry_run,
                    args.verbose,
                )
                if not args.dry_run:
                    if audio_path:
                        tqdm.write(f"  Extracted audio: {audio_path}")
                    if image_path:
                        tqdm.write(f"  Extracted image: {image_path}")

                    # Delete original video if requested and extraction was successful
                    if args.delete_original and audio_path and image_path:
                        try:
                            video_path.unlink()
                            if args.verbose:
                                tqdm.write(f"  Deleted original: {video_path}")
                            else:
                                tqdm.write(f"  Deleted: {video_path_rel}")
                        except OSError as e:
                            tqdm.write(f"  Error deleting {video_path}: {e}")
                elif args.dry_run and args.delete_original:
                    tqdm.write(f"  [DRY-RUN] Would delete: {video_path}")
        else:
            if args.verbose:
                tqdm.write(f"  Result: Has motion ({frozen_percentage:.1f}%)")
            elif not args.quiet:
                tqdm.write(f"{video_path_rel} [OK: {frozen_percentage:.1f}%]")

    # Summary
    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  Total videos scanned: {total_videos}")
    print(f"  Static videos found: {len(static_videos)}")
    if use_cache:
        print(f"  Cache hits: {cache_hits}")
        print(f"  Cache misses: {cache_misses}")

    if static_videos:
        print(f"\nStatic videos:")
        for video, percentage in sorted(
            static_videos.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  - {percentage:5.1f}% - {video}")


if __name__ == "__main__":
    main()
