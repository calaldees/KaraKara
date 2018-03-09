How the KaraKara Player interacts with the server:
==================================================

1. Show a splash screen
-----------------------
`/queue/QUEUE_ID/random_images.json` can be useful if you want some images to
use as decorations / previews

Format:

```
{
  "data": {
    "images": [
      [... a bunch strings. TODO: where are these URLs relative to? ...]
    ]
  }
}
```


2. Fetch settings
-----------------
`/queue/QUEUE_ID/settings.json` contains a bunch of server-side settings that
the client might find useful, such as the location of the websocket endpoint.

Format:

```
{
  "data": {
    "settings": {
      [... a bunch of key-value pairs ...]
    }
  }
}
```


3. Fetch the current playlist
-----------------------------
`/queue/QUEUE_ID/queue_items.json`

Format:

```
{
  "data": {
    "queue": [
      {
        "performer_name": "bob",
        "track": {
          "title": "Some Song",
          "duration": 42,
          "attachments": [
            {
              "location": "sdfgsgdsfgdfsgd.jpg",
              "type": "image"  // image, video, tags, srt, preview
            },
            [...]
          ]
        }
      },
      [...]
    ]
  }
}
```


2. Open a WebSocket Control Connection
--------------------------------------
connect via websocket to `https://<server>/<websocket path>` (path defined in settings)
- send an auth token
- wait for a stream of instructions
  - `play`: begin playing the first track in the queue in fullscreen video view
  - `pause`: pause the currently playing track
  - `stop`: stop the currently playing track and go back to playlist view
  - `seek_forwards`: move the video X seconds forwards
  - `seek_backwards`: move the video X seconds backwards
  - `skip`: mark the current song as finished (skipped by an admin)
  - `ended`: mark the current song as finished (having ended natrually)
  - `queue_updated`: the client should re-fetch the latest `queue_items.json`
  - `settings`: the client should re-fetch the latest `settings.json`
