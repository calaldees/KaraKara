# KaraKara Upload Service

Allows users to upload tracks for review and submission to the KaraKara platform.

## Run

Dev:
```
uv run uvicorn upload:app --reload
```

Prod:
```
uv run uvicorn upload:app
```

## Settings:
* `UPLOAD_DIR`: Directory to store uploaded files. Default is `../media/source/WorkInProgress`
* `BASE_PATH`: Base path for the upload endpoint. Default is `/`. Set to `/upload` if deployed behind a reverse proxy and mounted at that path.
* `DISCORD_WEBHOOK_SUBMISSIONS_URL`: Discord webhook URL to post a notification when a track is submitted.
* `DISCORD_WEBHOOK_REQUESTS_URL`: Discord webhook URL to post a notification when a track is requested.
