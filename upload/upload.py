import os
import aiofiles
import shutil
import uuid
import json
import re
from glob import glob
import typing as t
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.staticfiles import StaticFiles
from tuspyserver import create_tus_router
from datetime import datetime


TEMP_DIR = "/tmp/kk_upload_files"
BASE_PATH = os.environ.get("BASE_PATH", "/upload")
UPLOAD_ROOT = os.environ.get("UPLOAD_DIR", "/uploads")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(UPLOAD_ROOT, exist_ok=True)

app = FastAPI(title="FastAPI TUS Upload Server")
app.include_router(create_tus_router(files_dir=TEMP_DIR))
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# Hacky middleware to rewrite Location headers because
# tuspyserver is serving from /files but we want /upload/files
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
async def health():
    return {"status": "ok"}


@app.get("/")
async def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    return FileResponse(index_path, media_type="text/html")


@app.get("/favicon.ico")
async def serve_favicon():
    ico_path = os.path.join(STATIC_DIR, "favicon.ico")
    return FileResponse(ico_path, media_type="image/x-icon")


@app.get("/wips")
async def list_wips():
    # find all .txt files in UPLOAD_ROOT, check them for "title:" tags,
    # return a list
    metas = []
    for fn in glob(os.path.join(UPLOAD_ROOT, "**/*.txt"), recursive=True):
        meta = {}
        async with aiofiles.open(fn, "r") as f:
            contents = await f.read()
        for line in contents.splitlines():
            parts = line.split(":", 1)
            if len(parts) == 2:
                key = parts[0].strip()
                if key in ("title", "artist", "status"):
                    meta[key] = parts[1].strip()
        if meta.get("title"):
            metas.append(meta)
    return {"wips": metas}


@app.post("/session")
async def create_session():
    session_id = str(uuid.uuid4())
    sess_path = os.path.join(UPLOAD_ROOT, session_id)
    os.makedirs(sess_path, exist_ok=True)
    return {"session_id": session_id}


@app.post("/finalize")
async def finalize(payload: dict[str, t.Any]):
    """
    Expected JSON body:
      {
        "session_id": "uuid",
        "tags": { "title": "...", "artist": "...", "release_date": "..." },
      }
    Moves files from the temp dir into /uploads/<session_id>/,
    then writes metadata.json there.
    """
    session_id = payload.get("session_id")
    tags = payload.get("tags", {})

    if not session_id:
        raise HTTPException(400, "Missing session_id")

    # create a track ID from tags as either "from - title" or "artist - title"
    title = tags.get("title", "Untitled")
    if from_ := tags.get("from"):
        track_id = f"{from_} - {title}"
    elif artist := tags.get("artist"):
        track_id = f"{artist} - {title}"
    else:
        track_id = title
    track_id = re.sub(r"[^a-zA-Z0-9 _-\.]+", " ", track_id)

    session_dir = os.path.join(UPLOAD_ROOT, session_id)
    os.makedirs(session_dir, exist_ok=True)

    moved_files = []

    # find all files in TEMP_DIR that match the provided session ID
    # (ideally the client would provide a list of file IDs...)
    for info_path in glob(os.path.join(TEMP_DIR, "*.info")):
        async with aiofiles.open(info_path, "r") as f:
            info = json.loads(await f.read())["metadata"]
        if info.get("session_id") == session_id:
            data_path = info_path[:-5]  # remove .info
            fname = os.path.basename(info.get("filename", data_path))
            dest = os.path.join(session_dir, fname)
            shutil.move(data_path, dest)
            moved_files.append(fname)
            os.remove(info_path)

    meta_path = os.path.join(session_dir, f"{track_id}.txt")
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

    return JSONResponse(
        {"ok": True, "moved_files": moved_files, "session_id": session_id}
    )
