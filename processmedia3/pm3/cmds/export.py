import gzip
import json
import logging
import os
from pathlib import Path
from collections.abc import Sequence

import brotli
import requests
from tqdm.contrib.concurrent import thread_map

from pm3.lib.track import Track, TrackDict, TrackValidationException


log = logging.getLogger(__name__)


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

    json_list: list[TrackDict] = thread_map(_export, tracks, max_workers=threads, desc="export ", unit="track")

    # Export in alphabetic order
    json_dict: dict[str, TrackDict] = dict(sorted((t["id"], t) for t in json_list if t))

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

        path = processed_dir / "tracks.json.br"
        path.with_suffix(".tmp").write_bytes(brotli.compress(data))
        path.with_suffix(".tmp").rename(path)

        announce(old_tracklist, json_dict)


def announce(
    old_tracklist: dict[str, TrackDict],
    new_tracklist: dict[str, TrackDict],
) -> None:
    added: list[str] = []
    updated: list[str] = []
    removed: list[str] = []
    track_base_url = "https://karakara.uk/browser3/test/tracks"
    for track_id in new_tracklist:
        if track_id not in old_tracklist:
            title = new_tracklist[track_id]["tags"]["title"][0]
            added.append(f"* [{title}]({track_base_url}/{track_id})")
        elif new_tracklist[track_id] != old_tracklist[track_id]:
            new_track = new_tracklist[track_id]
            old_track = old_tracklist[track_id]
            title = new_track["tags"]["title"][0]
            if what_changed := list_changes(old_track, new_track):
                updated.append(f"* [{title}]({track_base_url}/{track_id}) - {what_changed}")
    for track_id in old_tracklist:
        if track_id not in new_tracklist:
            title = old_tracklist[track_id]["tags"]["title"][0]
            removed.append(f"* {title}")
    if not (added or updated or removed):
        return

    content = ""
    if added:
        content += "**Added:**\n" + "\n".join(added) + "\n"
    if updated:
        content += "**Updated:**\n" + "\n".join(updated) + "\n"
    if removed:
        content += "**Removed:**\n" + "\n".join(removed) + "\n"
    try:
        webhook_url = os.getenv("DISCORD_WEBHOOK_UPDATES_URL")
        if webhook_url:
            response = requests.post(
                webhook_url,
                json={
                    "content": content.strip(),
                    "flags": 4,  # avoid URL previews
                },
            )
            if response.status_code != 204:
                log.error(f"Failed to call webhook: {response.status_code} {response.text}")
        else:
            log.warning("Webhook config missing, not sending notification")
    except Exception:
        log.exception("Failed to send notification:")


def list_changes(old_track: TrackDict, new_track: TrackDict) -> str | None:
    """
    Compare two TrackDicts, and return a string describing what changed
    in ways that matter to users (tags and attachments), or None if nothing
    important changed.
    """
    what_changed = []

    if new_track["tags"] != old_track["tags"]:
        old_tags = old_track.get("tags", {})
        new_tags = new_track.get("tags", {})
        all_tag_keys = set(old_tags.keys() | new_tags.keys())
        tag_changes = []
        for tag_key in sorted(all_tag_keys):
            # if the only difference is "new" in the tag keys or values, ignore it
            if tag_key == "new":
                continue
            if set(new_tags.get(tag_key, [])).symmetric_difference(set(old_tags.get(tag_key, []))) == {"new"}:
                continue
            if new_tags.get(tag_key) != old_tags.get(tag_key):
                tag_changes.append(tag_key)
        if tag_changes:
            what_changed.append(f"tags ({', '.join(tag_changes)})")

    old_attachments = old_track.get("attachments", {})
    new_attachments = new_track.get("attachments", {})
    all_categories = set(old_attachments.keys() | new_attachments.keys())
    for att_cat in sorted(all_categories):
        if new_attachments.get(att_cat) != old_attachments.get(att_cat):
            what_changed.append(att_cat)

    return ", ".join(what_changed) if what_changed else None
