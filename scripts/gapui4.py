#!/usr/bin/env python3

"""
Enhanced Gap Viewer Features:
- Automatic gap scanning on startup
- Three states (unchecked, confirmed, mistake)
- mpv + Aegisub launch
- SQLite database storage
- Search bar (filter by filename)
- Filters (all / unchecked / confirmed / mistakes)
- Sorting (file / duration / start time)
- Auto-jump to next unchecked gap
"""

import argparse
import re
import sqlite3
import subprocess
import sys
import tkinter as tk
from datetime import timedelta
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any, Dict, List, Optional, Tuple, Union

SRT_TIMESTAMP = re.compile(
    r"(\d\d):(\d\d):(\d\d),(\d\d\d) --> (\d\d):(\d\d):(\d\d),(\d\d\d)"
)


def parse_timestamp(h: str, m: str, s: str, ms: str) -> timedelta:
    return timedelta(hours=int(h), minutes=int(m), seconds=int(s), milliseconds=int(ms))


def analyze_srt(path: Path, threshold: float = 10) -> List[Tuple[float, float]]:
    """Analyze an SRT file and return gaps larger than threshold seconds"""
    gaps = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    times = []
    for line in lines:
        m = SRT_TIMESTAMP.search(line)
        if m:
            start = parse_timestamp(*m.groups()[0:4])
            end = parse_timestamp(*m.groups()[4:8])
            times.append((start, end))

    for (prev_start, prev_end), (next_start, next_end) in zip(times, times[1:]):
        gap = (next_start - prev_end).total_seconds()
        if gap > threshold:
            # Return start and end times as total seconds
            gaps.append((prev_end.total_seconds(), next_start.total_seconds()))

    return gaps


class GapViewerApp:
    def __init__(self, root: tk.Tk, db_path: str, folder: str) -> None:
        self.root = root
        self.db_path = Path(db_path)
        self.folder = Path(folder).expanduser()
        self.root.title("SRT Gap Viewer")

        self.all_gaps = []  # Raw extracted gaps
        self.view_gaps = []  # Filtered + sorted output

        self.build_ui()
        self.scan_for_gaps()
        self.load_gaps()

    def get_db_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def scan_for_gaps(self) -> int:
        """Scan the folder for SRT files and update the database with new gaps"""
        if not self.folder.exists():
            messagebox.showwarning("Warning", f"Folder not found: {self.folder}")
            return

        conn = self.get_db_connection()
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gaps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                start_time REAL NOT NULL,
                end_time REAL NOT NULL,
                correct BOOLEAN DEFAULT NULL,
                UNIQUE(filename, start_time)
            )
        """)

        new_gaps_count = 0

        # Process files
        for file in self.folder.rglob("*.srt"):
            gaps = analyze_srt(file)
            relative_path = file.relative_to(self.folder)
            for start, end in gaps:
                # Check if gap with same filename and start_time exists
                cursor.execute(
                    "SELECT id, end_time FROM gaps WHERE filename = ? AND start_time = ?",
                    (str(relative_path), start),
                )
                existing = cursor.fetchone()

                if existing:
                    # Update end_time if it has changed
                    existing_id, existing_end = existing
                    if end != existing_end:
                        cursor.execute(
                            "UPDATE gaps SET end_time = ? WHERE id = ?",
                            (end, existing_id),
                        )
                        new_gaps_count += 1  # Count as a change
                else:
                    # Insert new gap
                    cursor.execute(
                        "INSERT INTO gaps (filename, start_time, end_time, correct) VALUES (?, ?, ?, ?)",
                        (str(relative_path), start, end, None),
                    )
                    new_gaps_count += 1

        conn.commit()
        conn.close()

        return new_gaps_count

    def load_gaps(self) -> None:
        """Load all gaps from the SQLite database"""
        self.all_gaps = []

        conn = self.get_db_connection()
        cursor = conn.cursor()

        # Ensure table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gaps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                start_time REAL NOT NULL,
                end_time REAL NOT NULL,
                correct BOOLEAN DEFAULT NULL,
                UNIQUE(filename, start_time)
            )
        """)

        cursor.execute("""
            SELECT id, filename, start_time, end_time, correct
            FROM gaps
            ORDER BY filename, start_time
        """)

        for row in cursor.fetchall():
            gap_id, filename, start_time, end_time, correct = row
            self.all_gaps.append(
                {
                    "id": gap_id,
                    "filename": filename,
                    "start_time": start_time,
                    "end_time": end_time,
                    "correct": correct,  # None, 0 (False), or 1 (True)
                }
            )

        conn.close()
        self.apply_filters()

    def update_gap_status(self, gap_id: int, correct_value: Optional[int]) -> None:
        """Update the correct status of a gap in the database"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE gaps SET correct = ? WHERE id = ?", (correct_value, gap_id)
        )
        conn.commit()
        conn.close()

    def build_ui(self) -> None:
        top = tk.Frame(self.root)
        top.pack(fill="x", pady=5)

        tk.Label(top, text=f"Database: {self.db_path}").pack(anchor="w")
        tk.Label(top, text=f"Folder: {self.folder}").pack(anchor="w")

        control = tk.Frame(self.root)
        control.pack(fill="x", padx=5, pady=5)

        # Search bar
        tk.Label(control, text="Search:").grid(row=0, column=0, sticky="w")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.apply_filters())
        tk.Entry(control, textvariable=self.search_var, width=30).grid(
            row=0, column=1, padx=5
        )

        # Filter dropdown
        tk.Label(control, text="Filter:").grid(row=0, column=2)
        self.filter_var = tk.StringVar(value="All")
        ttk.OptionMenu(
            control,
            self.filter_var,
            "All",
            "All",
            "Unchecked",
            "Confirmed",
            "Mistakes",
            command=lambda *_: self.apply_filters(),
        ).grid(row=0, column=3, padx=5)

        # Sort dropdown
        tk.Label(control, text="Sort:").grid(row=0, column=4)
        self.sort_var = tk.StringVar(value="File")
        ttk.OptionMenu(
            control,
            self.sort_var,
            "File",
            "File",
            "Duration",
            "Start Time",
            command=lambda *_: self.apply_filters(),
        ).grid(row=0, column=5, padx=5)

        # Buttons
        btns = tk.Frame(self.root)
        btns.pack(fill="x", pady=5)

        tk.Button(btns, text="Launch mpv", command=self.launch_mpv).pack(
            side="left", padx=5
        )
        tk.Button(btns, text="Launch Aegisub", command=self.launch_aegisub).pack(
            side="left", padx=5
        )
        tk.Button(btns, text="Rescan for Gaps", command=self.rescan).pack(
            side="left", padx=5
        )
        tk.Button(btns, text="Mark Confirmed", command=self.mark_confirmed).pack(
            side="left", padx=5
        )
        tk.Button(btns, text="Mark Mistake", command=self.mark_mistake).pack(
            side="left", padx=5
        )
        tk.Button(btns, text="Mark Unchecked", command=self.mark_unchecked).pack(
            side="left", padx=5
        )
        tk.Button(btns, text="Next Unchecked", command=self.jump_next_unchecked).pack(
            side="right", padx=5
        )

        # Listbox
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(frame, width=100, height=25)
        self.listbox.pack(fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.update_details)

        self.details = tk.Label(self.root, text="", justify="left", anchor="w")
        self.details.pack(fill="x", pady=5)

    # --------------------
    # Filtering + sorting
    # --------------------
    def apply_filters(self) -> None:
        self.view_gaps = []

        search = self.search_var.get().lower()
        mode = self.filter_var.get()

        for g in self.all_gaps:
            filename = g["filename"]
            correct = g["correct"]

            # Search filter
            if search and search not in filename.lower():
                continue

            # Category filter
            if mode == "Unchecked" and correct is not None:
                continue
            if mode == "Confirmed" and correct != 1:
                continue
            if mode == "Mistakes" and correct != 0:
                continue

            self.view_gaps.append(g)

        # Sorting
        if self.sort_var.get() == "File":
            self.view_gaps.sort(key=lambda g: (g["filename"].lower(), g["start_time"]))
        elif self.sort_var.get() == "Duration":
            self.view_gaps.sort(
                key=lambda g: g["end_time"] - g["start_time"], reverse=True
            )
        elif self.sort_var.get() == "Start Time":
            self.view_gaps.sort(key=lambda g: g["start_time"])

        self.update_listbox()

    def update_listbox(self) -> None:
        self.listbox.delete(0, tk.END)
        for idx, g in enumerate(self.view_gaps):
            filename = g["filename"]
            start_time = g["start_time"]
            end_time = g["end_time"]
            duration = end_time - start_time
            correct = g["correct"]

            # Format times as HH:MM:SS
            start_str = self.format_time(start_time)
            end_str = self.format_time(end_time)

            label = f"{filename} | {start_str} -> {end_str} ({duration:.1f}s)"

            if correct == 1:
                color = "#c8f7c5"
                label += " [OK]"
            elif correct == 0:
                color = "#f7c5c5"
                label += " [MISTAKE]"
            else:
                color = "#ffffff"

            self.listbox.insert(tk.END, label)
            self.listbox.itemconfig(idx, bg=color)

    def update_details(self, evt: Optional[tk.Event]) -> None:
        sel = self.listbox.curselection()
        if not sel:
            return
        g = self.view_gaps[sel[0]]
        correct_str = {None: "Unchecked", 0: "Mistake", 1: "Confirmed"}.get(
            g["correct"], "Unknown"
        )
        duration = g["end_time"] - g["start_time"]
        start_str = self.format_time(g["start_time"])
        end_str = self.format_time(g["end_time"])
        self.details.config(
            text=f"File: {g['filename']}\nStart: {start_str}\nEnd: {end_str}\n"
            f"Duration: {duration:.2f}s\nStatus: {correct_str}"
        )

    # --------------------
    # Helpers
    # --------------------
    def format_time(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS.mmmmmm format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:09.6f}"

    def find_media(self, srt_path: str) -> Optional[Union[Path, Dict[str, Path]]]:
        """Find corresponding media file for an SRT file, ignoring bracketed text differences

        Returns either:
        - A Path object (video file)
        - A dict with 'audio' and 'image' keys (for audio+image combination)
        - None (no media found)
        """
        srt = Path(srt_path)
        if not srt.is_absolute():
            # Relative path - resolve relative to input folder
            srt = self.folder / srt_path

        import re

        base = srt.with_suffix("")
        base_name = srt.stem
        base_name_without_brackets = re.sub(r"\s*\[.*?\]\s*", " ", base_name).strip()
        parent_dir = srt.parent

        video_exts = [".mkv", ".mp4", ".avi", ".mov"]
        audio_exts = [".mp3", ".m4a", ".ogg", ".flac", ".wav", ".opus"]
        image_exts = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]

        # First try exact match for video
        for ext in video_exts:
            if base.with_suffix(ext).exists():
                return base.with_suffix(ext)

        # Try exact match for audio + image
        audio_file = None
        image_file = None
        for ext in audio_exts:
            if base.with_suffix(ext).exists():
                audio_file = base.with_suffix(ext)
                break
        for ext in image_exts:
            if base.with_suffix(ext).exists():
                image_file = base.with_suffix(ext)
                break
        if audio_file and image_file:
            return {"audio": audio_file, "image": image_file}

        # If no exact match, try ignoring bracketed text
        if parent_dir.exists():
            found_video = None
            found_audio = None
            found_image = None

            for media_file in parent_dir.iterdir():
                media_name_without_brackets = re.sub(
                    r"\s*\[.*?\]\s*", " ", media_file.stem
                ).strip()
                if base_name_without_brackets == media_name_without_brackets:
                    if media_file.suffix.lower() in video_exts:
                        found_video = media_file
                    elif media_file.suffix.lower() in audio_exts:
                        found_audio = media_file
                    elif media_file.suffix.lower() in image_exts:
                        found_image = media_file

            # Prefer video if found
            if found_video:
                return found_video
            # Otherwise return audio+image if both exist
            if found_audio and found_image:
                return {"audio": found_audio, "image": found_image}

        return None

    def get_selected_gap(self) -> Optional[Dict[str, Any]]:
        sel = self.listbox.curselection()
        if not sel:
            return None
        return self.view_gaps[sel[0]]

    # --------------------
    # Actions
    # --------------------
    def launch_mpv(self) -> None:
        g = self.get_selected_gap()
        if not g:
            return

        srt_path = g["filename"]
        end_time = g["end_time"]

        # Construct full path to SRT
        srt = Path(srt_path)
        if not srt.is_absolute():
            srt = self.folder / srt_path

        if not srt.exists():
            messagebox.showerror("Error", f"SRT file not found: {srt}")
            return

        media = self.find_media(srt_path)
        if not media:
            messagebox.showerror("Error", "No matching media file found")
            return

        # Start shortly seconds before the gap end
        start_seconds = end_time - 2
        if start_seconds < 0:
            start_seconds = 0

        # Convert to HH:MM:SS format for mpv
        start_hours = int(start_seconds // 3600)
        start_minutes = int((start_seconds % 3600) // 60)
        start_secs = int(start_seconds % 60)
        start_str = f"{start_hours:02d}:{start_minutes:02d}:{start_secs:02d}"

        # Handle audio+image case
        if isinstance(media, dict):
            audio_file = media["audio"]
            image_file = media["image"]
            subprocess.Popen(
                [
                    "mpv",
                    str(audio_file),
                    f"--cover-art-files={image_file}",
                    f"--start={start_str}",
                    f"--sub-file={srt}",
                ]
            )
        else:
            # Regular video file
            subprocess.Popen(
                ["mpv", str(media), f"--start={start_str}", f"--sub-file={srt}"]
            )

    def launch_aegisub(self) -> None:
        g = self.get_selected_gap()
        if not g:
            return

        srt_path = g["filename"]

        # Construct full path to SRT
        srt = Path(srt_path)
        if not srt.is_absolute():
            srt = self.folder / srt_path

        if not srt.exists():
            messagebox.showerror("Error", f"SRT file not found: {srt}")
            return

        media = self.find_media(srt_path)

        cmd = ["aegisub", str(srt)]
        if media:
            # Handle audio+image case - aegisub only needs the audio file
            if isinstance(media, dict):
                cmd.append(str(media["audio"]))
            else:
                cmd.append(str(media))
        subprocess.Popen(cmd)

    def mark_confirmed(self) -> None:
        g = self.get_selected_gap()
        if not g:
            return

        self.update_gap_status(g["id"], 1)
        g["correct"] = 1
        self.apply_filters()
        self.jump_next_unchecked()

    def mark_mistake(self) -> None:
        g = self.get_selected_gap()
        if not g:
            return

        self.update_gap_status(g["id"], 0)
        g["correct"] = 0
        self.apply_filters()
        self.jump_next_unchecked()

    def mark_unchecked(self) -> None:
        g = self.get_selected_gap()
        if not g:
            return

        self.update_gap_status(g["id"], None)
        g["correct"] = None
        self.apply_filters()

    # --------------------
    # Auto-jump feature
    # --------------------
    def jump_next_unchecked(self) -> None:
        for idx, g in enumerate(self.view_gaps):
            if g["correct"] is None:
                self.listbox.select_clear(0, tk.END)
                self.listbox.select_set(idx)
                self.listbox.see(idx)
                self.update_details(None)
                return

        messagebox.showinfo("Done", "No unchecked gaps left.")

    def rescan(self) -> None:
        """Manually trigger a rescan of the folder"""
        new_count = self.scan_for_gaps()
        self.load_gaps()
        messagebox.showinfo("Rescan Complete", f"Found or updated {new_count} gap(s).")


# --------------------
# Main
# --------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="View and manage SRT gaps from database"
    )
    parser.add_argument(
        "--database",
        "-d",
        default="./gaps.db",
        help="Path to SQLite database file (default: ./gaps.db)",
    )
    parser.add_argument(
        "--folder",
        "-f",
        default="~/Videos/KaraKara/",
        help="Base folder for SRT files (default: ~/Videos/KaraKara/)",
    )

    args = parser.parse_args()

    root = tk.Tk()
    app = GapViewerApp(root, args.database, args.folder)
    root.mainloop()
