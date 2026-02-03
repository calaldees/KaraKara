import json
import logging
import os
import re
import shutil
import sys
import typing as t
import uuid
from datetime import datetime
from glob import glob
from pathlib import Path

import aiofiles
import requests
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from tuspyserver import create_tus_router

TEMP_DIR = Path("/tmp/kk_upload_files")
BASE_PATH = os.environ.get("BASE_PATH", "")
UPLOAD_ROOT = Path(os.environ.get("UPLOAD_DIR", "../media/source/WorkInProgress"))
STATIC_DIR = Path(__file__).parent.parent / "dist" / "static"

TEMP_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = FastAPI(title="FastAPI TUS Upload Server")
app.include_router(create_tus_router(files_dir=TEMP_DIR.as_posix(), prefix="api/files"))
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# Hacky middleware to rewrite Location headers because tuspyserver is serving
# from http://localhost/files but we want https://karakara.uk/upload/files
class PrefixLocationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        if BASE_PATH:
            if "location" in response.headers:
                loc = response.headers["location"]
                loc = loc.replace("/api/files/", BASE_PATH + "/api/files/")
                loc = loc.replace("http://", "https://")
                response.headers["location"] = loc
        return response


app.add_middleware(PrefixLocationMiddleware)


@app.get("/api/health")
async def health() -> JSONResponse:
    """
    Simple test just so that `pytest` doesn't complain about no tests.

    >>> import asyncio
    >>> asyncio.run(health()).body
    b'{"status":"ok"}'
    """
    return JSONResponse({"status": "ok"})


@app.get("/")
async def serve_index() -> FileResponse:
    return FileResponse(STATIC_DIR / ".." / "index.html", media_type="text/html")


# favicon needs its own route because it isn't in the /static/ folder
# (can we make it go in the static folder?)
@app.get("/favicon.svg")
async def serve_favicon() -> FileResponse:
    return FileResponse(STATIC_DIR / ".." / "favicon.svg", media_type="image/svg+xml")


@app.get("/api/wips")
async def list_wips() -> JSONResponse:
    """
    List any .txt files in the upload folder, to give any progress updates.
    """
    metas: list[dict[str, str]] = []
    for fn in glob(os.path.join(UPLOAD_ROOT, "**/*.txt"), recursive=True):
        meta: dict[str, str] = {}
        async with aiofiles.open(fn, "r") as f:
            contents = await f.read()
        for line in contents.splitlines():
            parts = line.split(":", 1)
            if len(parts) == 2:
                key = parts[0].strip()
                if key in ("title", "from", "artist", "status"):
                    meta[key] = parts[1].strip()
        if meta.get("title"):
            metas.append(meta)
    return JSONResponse({"wips": metas})


@app.post("/api/session")
async def begin_upload_session() -> JSONResponse:
    session_id = str(uuid.uuid4())
    return JSONResponse({"session_id": session_id})


def tags_to_id(tags: dict[str, t.Any]) -> str:
    """
    >>> tags_to_id({"title": ["My Song"], "artist": ["The Artist"]})
    'The Artist - My Song'
    >>> tags_to_id({"title": ["My Song"], "from": ["The Show"]})
    'The Show - My Song'
    >>> tags_to_id({"title": ["My Song"]})
    'My Song'
    >>> tags_to_id({"title": ["My/Song: I'm The*Best?"], "artist": ["The/Artist"]})
    'The Artist - My Song Im The Best'
    """
    title = tags.get("title", ["Untitled"])
    if "from" in tags and tags["from"] and tags["from"][0].strip():
        track_id = f"{tags['from'][0].strip()} - {title[0]}"
    elif "artist" in tags and tags["artist"] and tags["artist"][0].strip():
        track_id = f"{tags['artist'][0].strip()} - {title[0]}"
    else:
        track_id = title[0]
    track_id = re.sub(r"[']", "", track_id)
    track_id = re.sub(r"[^a-zA-Z0-9_\-\.]+", " ", track_id)
    return track_id.strip()


async def write_tags_file(meta_path: Path, tags: dict[str, list[str]], status: str) -> None:
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(meta_path, "w") as f:
        for key, values in tags.items():
            for value in values:
                if value:
                    await f.write(f"{key}:{value}\n")
        await f.write(f"added:{datetime.now().strftime('%Y-%m-%d')}\n")
        await f.write(f"status:{status}\n")


def send_notification(webhook_url: str | None, content: str) -> None:
    try:
        if webhook_url:
            response = requests.post(
                webhook_url,
                json={
                    "content": content.strip(),
                },
            )
            if response.status_code != 204:
                log.error(f"Failed to call webhook: {response.status_code} {response.text}")
            else:
                log.info("Sent notification via discord")
        else:
            log.warning(f"Webhook config missing, not notifying ({content!r})")
    except Exception:
        log.exception(f"Failed to send notification ({content!r}):")


def sanitize_tags(tags: dict[str, list[str]] | None) -> dict[str, list[str]]:
    """
    >>> sanitize_tags({"title": [" My Song ", ""], "artist": [" The Artist "], "blank": ["   "]})
    {'title': ['My Song'], 'artist': ['The Artist']}
    """
    if not tags:
        raise HTTPException(400, "Missing tags")
    for key in list(tags.keys()):
        tags[key] = [v.strip() for v in tags[key] if v.strip()]
        if not tags[key]:
            del tags[key]
    return tags


def get_unique_path(base_path: Path, base_name: str, suffix: str = "") -> Path:
    """
    Generate a unique path by appending numbers if the path already exists.

    >>> import tempfile
    >>> temp_dir = Path(tempfile.mkdtemp())
    >>> (temp_dir / "test.txt").touch()
    >>> get_unique_path(temp_dir, "test", ".txt")
    PosixPath('.../test (2).txt')
    >>> (temp_dir / "test (2).txt").touch()
    >>> get_unique_path(temp_dir, "test", ".txt")
    PosixPath('.../test (3).txt')
    """
    unique_path = base_path / f"{base_name}{suffix}"
    counter = 2
    while unique_path.exists():
        unique_path = base_path / f"{base_name} ({counter}){suffix}"
        counter += 1
    return unique_path


@app.post("/api/request")
async def request_track(payload: dict[str, t.Any]) -> JSONResponse:
    """
    Expected JSON body:

      {
        "tags": { "title": ["..."], "artist": ["..."], "date": ["..."] },
      }
    """
    tags = sanitize_tags(payload.get("tags"))
    track_id = tags_to_id(tags)
    meta_path = get_unique_path(UPLOAD_ROOT / "Requests", track_id, ".txt")
    await write_tags_file(meta_path, tags, "needs files, lyrics, timings")
    webhook_url = os.getenv("DISCORD_WEBHOOK_REQUESTS_URL")
    send_notification(webhook_url, f"New request: **{track_id}**")
    log.info(f"Logged request for {track_id!r}")
    return JSONResponse({"ok": True})


@app.post("/api/submit")
async def submit_track(payload: dict[str, t.Any]) -> JSONResponse:
    """
    After uploading one-or-more files via TUS, call this endpoint to
    submit the track, moving the files from TEMP_DIR to UPLOAD_ROOT.

    Expected JSON body:

      {
        "session_id": "uuid",
        "tags": { "title": ["..."], "artist": ["..."], "date": ["..."] },
      }
    """
    session_id: str = payload["session_id"]
    tags = sanitize_tags(payload.get("tags"))
    track_id = tags_to_id(tags)

    session_dir = get_unique_path(UPLOAD_ROOT / "Submissions", track_id)
    meta_path = session_dir / f"{track_id}.txt"
    await write_tags_file(meta_path, tags, "awaiting moderator approval")

    moved_files: list[str] = []
    for info_path in TEMP_DIR.rglob("*.info"):
        async with aiofiles.open(info_path, "r") as f:
            info: dict[str, str] = json.loads(await f.read())["metadata"]
        if info["session_id"] == session_id:
            data_path = info_path.with_suffix("")
            orig_path = Path(info["filename"])
            orig_filename = orig_path.name

            targ_path = session_dir / Path(track_id).with_suffix(orig_path.suffix).name
            while targ_path.exists():
                targ_path = targ_path.with_stem(targ_path.stem + "_")
            shutil.move(data_path.as_posix(), targ_path.as_posix())
            moved_files.append(orig_filename)
            info_path.unlink()

    webhook_url = os.getenv("DISCORD_WEBHOOK_SUBMISSIONS_URL")
    contributor = f" ({tags['contributor'][0]}" if "contributor" in tags else ""
    send_notification(webhook_url, f"New submission: **{track_id}**{contributor}")
    log.info(f"Uploaded files for {track_id!r} (session {session_id})")
    return JSONResponse({"ok": True, "moved_files": moved_files, "session_id": session_id})
