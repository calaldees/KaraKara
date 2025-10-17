import os
import aiofiles
import uuid
import json
import re
import shutil
import logging
from glob import glob
import typing as t
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.staticfiles import StaticFiles
from tuspyserver import create_tus_router
from datetime import datetime
from pathlib import Path


TEMP_DIR = Path("/tmp/kk_upload_files")
BASE_PATH = os.environ.get("BASE_PATH", "/upload")
UPLOAD_ROOT = Path(os.environ.get("UPLOAD_DIR", "/uploads"))
STATIC_DIR = Path(__file__).parent / "static"

TEMP_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = FastAPI(title="FastAPI TUS Upload Server")
app.include_router(create_tus_router(files_dir=TEMP_DIR.as_posix()))
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# Hacky middleware to rewrite Location headers because tuspyserver is serving
# from http://localhost/files but we want https://karakara.uk/upload/files
class PrefixLocationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        if BASE_PATH:
            if "location" in response.headers:
                loc = response.headers["location"]
                loc = loc.replace("/files/", BASE_PATH + "/files/")
                loc = loc.replace("http://", "https://")
                response.headers["location"] = loc
        return response


app.add_middleware(PrefixLocationMiddleware)


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.get("/")
async def serve_index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html", media_type="text/html")


@app.get("/wips")
async def list_wips() -> JSONResponse:
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


@app.post("/session")
async def create_session() -> JSONResponse:
    session_id = str(uuid.uuid4())
    sess_path = os.path.join(UPLOAD_ROOT, session_id)
    os.makedirs(sess_path, exist_ok=True)
    return JSONResponse({"session_id": session_id})


@app.post("/finalize")
async def finalize(payload: dict[str, t.Any]) -> JSONResponse:
    """
    Expected JSON body:
      {
        "session_id": "uuid",
        "tags": { "title": ["..."], "artist": ["..."], "date": ["..."] },
      }
    Moves files from the temp dir into /uploads/<session_id>/,
    then writes metadata.json there.
    """
    session_id: str | None = payload.get("session_id")
    tags: dict[str, list[str]] = payload.get("tags", {})

    if not session_id:
        raise HTTPException(400, "Missing session_id")

    # create a track ID from tags as either "from - title" or "artist - title"
    title = tags.get("title", ["Untitled"])
    if from_ := tags.get("from"):
        track_id = f"{from_[0]} - {title[0]}"
    elif artist := tags.get("artist"):
        track_id = f"{artist[0]} - {title[0]}"
    else:
        track_id = title[0]
    track_id = re.sub(r"[^a-zA-Z0-9_\-\.]+", " ", track_id)

    session_dir = UPLOAD_ROOT / session_id
    os.makedirs(session_dir, exist_ok=True)

    moved_files: list[str] = []

    # find all files in TEMP_DIR that match the provided session ID
    # (ideally the client would provide a list of file IDs...)
    for info_path in TEMP_DIR.rglob("*.info"):
        async with aiofiles.open(info_path, "r") as f:
            info: dict[str, str] = json.loads(await f.read())["metadata"]
        if info["session_id"] == session_id:
            data_path = info_path.with_suffix("")
            orig_path = Path(info["filename"])
            targ_path = session_dir / Path(track_id).with_suffix(orig_path.suffix).name
            while targ_path.exists():
                targ_path = targ_path.with_stem(targ_path.stem + "_")
            # data_path.move(fname)  # py3.14
            shutil.move(data_path.as_posix(), targ_path.as_posix())
            moved_files.append(orig_path.name)
            info_path.unlink()

    meta_path = session_dir / f"{track_id}.txt"
    async with aiofiles.open(meta_path, "w") as f:
        for key, values in tags.items():
            for value in values:
                if value:
                    await f.write(f"{key}:{value}\n")
        await f.write(f"added:{datetime.now().strftime('%Y-%m-%d')}\n")
        if not moved_files:
            await f.write("status:needs files\n")
        else:
            await f.write("status:awaiting moderator approval\n")

    try:
        mg_base = os.getenv("MG_BASE", "https://api.mailgun.net")
        mg_sandbox = os.getenv("MG_SANDBOX")
        mg_api_key = os.getenv("MG_API_KEY")
        if mg_sandbox and mg_api_key:
            requests.post(
                f"{mg_base}/v3/{mg_sandbox}/messages",
                auth=("api", mg_api_key),
                data={
                    "from": f"KaraKara Uploader <postmaster@{mg_sandbox}>",
                    "to": "Shish <shish+karakara@shishnet.org>",
                    "subject": (
                        f"New Track - {track_id}"
                        if moved_files
                        else f"New Request - {track_id}"
                    ),
                    "text": "Check /media/source/WorkInProgress",
                },
            )
            log.info(f"Sent email notification via {mg_sandbox}")
        else:
            log.warning("Mailgun config missing, not sending notification")
    except Exception:
        log.exception("Failed to send notification:")

    log.info(f"Finalized session {session_id!r}, track id {track_id!r}")

    return JSONResponse(
        {"ok": True, "moved_files": moved_files, "session_id": session_id}
    )
