#!/usr/bin/env python3

import os
import uuid
import json
from sanic import Sanic, response
from sanic.request import Request
import aiofiles
from typing import Dict

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/uploads")
CHUNK_SIZE = 1024 * 1024  # not used for reading incoming stream which gives us bytes

app = Sanic("kk_upload")

# Simple in-memory registry mapping upload_id -> metadata
# Each entry: {"session_id": str, "filename": str, "upload_length": int, "offset": int, "path": str}
UPLOADS: Dict[str, Dict] = {}

os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/session")
async def create_session(request: Request):
    """Create and return a new session id (UUID).

    The client will upload multiple files to this session. Each session is a directory.
    """
    session_id = str(uuid.uuid4())
    session_path = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(session_path, exist_ok=True)
    return response.json({"session_id": session_id})


@app.post("/files/<session_id>")
async def create_upload(request: Request, session_id):
    """TUS creation endpoint.

    Expected headers:
      - Upload-Length: integer (total bytes)
      - Upload-Metadata: comma-separated key base64 pairs (e.g. filename dGVzdC5tcDM=)

    Responds with 201 Created and Location header pointing to the resource.
    """
    upload_length = request.headers.get("upload-length")
    if upload_length is None:
        return response.text("Missing Upload-Length header", status=400)

    try:
        upload_length = int(upload_length)
    except ValueError:
        return response.text("Invalid Upload-Length", status=400)

    # parse Upload-Metadata
    upload_metadata = request.headers.get("upload-metadata", "")
    filename = None
    if upload_metadata:
        # metadata looks like: key base64,another c2Vjb25k
        parts = [p.strip() for p in upload_metadata.split(",") if p.strip()]
        for part in parts:
            if " " in part:
                k, b64 = part.split(" ", 1)
                if k == "filename":
                    try:
                        filename = b64.encode("utf-8")
                        import base64

                        filename = base64.b64decode(b64).decode("utf-8")
                    except Exception:
                        filename = None
    if not filename:
        # fallback to a random name
        filename = f"upload_{uuid.uuid4().hex}"

    # ensure session directory exists
    session_path = os.path.join(UPLOAD_DIR, session_id)
    if not os.path.exists(session_path):
        return response.text("Session not found", status=404)

    upload_id = str(uuid.uuid4())
    save_path = os.path.join(session_path, filename)

    # create empty file if not exists
    if not os.path.exists(save_path):
        async with aiofiles.open(save_path, "wb") as f:
            await f.flush()

    UPLOADS[upload_id] = {
        "session_id": session_id,
        "filename": filename,
        "upload_length": upload_length,
        "offset": 0,
        "path": save_path,
    }

    # If the file exists and has some bytes (previous partial), set offset accordingly
    try:
        stat = os.stat(save_path)
        UPLOADS[upload_id]["offset"] = stat.st_size
    except Exception:
        UPLOADS[upload_id]["offset"] = 0

    # Resource URL
    location = f"/upload/files/{session_id}/{upload_id}"
    headers = {"Location": location}

    return response.text("", status=201, headers=headers)


@app.head("/files/<session_id>/<upload_id>")
async def head_upload(request: Request, session_id, upload_id):
    """Return Upload-Offset header showing how many bytes have been received so far."""
    entry = UPLOADS.get(upload_id)
    if not entry or entry["session_id"] != session_id:
        return response.text("Not Found", status=404)

    # ensure we report real file size
    try:
        stat = os.stat(entry["path"])
        offset = stat.st_size
        entry["offset"] = offset
    except FileNotFoundError:
        offset = 0

    headers = {
        "Upload-Offset": str(offset),
        "Upload-Length": str(entry["upload_length"]),
    }
    return response.text("", status=200, headers=headers)


@app.patch("/files/<session_id>/<upload_id>")
async def patch_upload(request: Request, session_id, upload_id):
    """Append the received bytes to the target file.

    Client must send 'Upload-Offset' header with the offset they're starting from.
    The request body is the binary chunk to append.
    """
    entry = UPLOADS.get(upload_id)
    if not entry or entry["session_id"] != session_id:
        return response.text("Not Found", status=404)

    upload_offset = request.headers.get("upload-offset")
    if upload_offset is None:
        return response.text("Missing Upload-Offset header", status=400)

    try:
        upload_offset = int(upload_offset)
    except ValueError:
        return response.text("Invalid Upload-Offset", status=400)

    file_path = entry["path"]

    # Ensure the incoming offset matches the actual current file size
    try:
        current_size = os.path.getsize(file_path)
    except FileNotFoundError:
        current_size = 0

    if upload_offset != current_size:
        return response.text(f"Offset mismatch: server={current_size} client={upload_offset}", status=409)

    # read raw bytes from request body (may be large chunk)
    body = request.body
    if not body:
        # nothing to write
        return response.text("No content", status=400)

    # append to file
    try:
        async with aiofiles.open(file_path, "ab") as f:
            await f.write(body)
            await f.flush()
    except Exception as e:
        return response.text(f"Failed to write file: {e}", status=500)

    # update offset
    new_size = os.path.getsize(file_path)
    entry["offset"] = new_size

    # If upload complete, nothing special here — client should call finalize later
    headers = {"Upload-Offset": str(new_size)}
    return response.text("", status=204, headers=headers)


@app.post("/finalize")
async def finalize(request: Request):
    """Finalize a session by writing metadata.json into the session directory.

    Expected JSON body:
    {
      "session_id": "...",
      "metadata": {"title": "...", "artist": "...", "release_date": "..."},
      "files": ["track1.mp3", "track2.flac"]
    }
    """
    try:
        payload = request.json
    except Exception:
        return response.text("Invalid JSON", status=400)

    session_id = payload.get("session_id")
    metadata = payload.get("metadata", {})
    files = payload.get("files", [])

    if not session_id:
        return response.text("Missing session_id", status=400)

    session_path = os.path.join(UPLOAD_DIR, session_id)
    if not os.path.exists(session_path):
        return response.text("Session not found", status=404)

    # Validate that listed files exist
    present_files = []
    for fname in files:
        fpath = os.path.join(session_path, fname)
        if os.path.exists(fpath):
            present_files.append(fname)

    # Write metadata.json
    out = {
        "metadata": metadata,
        "files": present_files,
    }

    meta_path = os.path.join(session_path, "metadata.json")
    async with aiofiles.open(meta_path, "w") as mf:
        await mf.write(json.dumps(out, indent=2))

    return response.json({"ok": True, "written_files": present_files})


@app.get("/")
async def index(request: Request):
    return await response.file("index.html")


@app.get("/static/<path:path>")
async def static_files(request: Request, path):
    return await response.file(f"static/{path}")


@app.get("/health")
async def health(request: Request):
    return response.json({"status": "ok"})
