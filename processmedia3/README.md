processmedia3
=============

Encode media (videos + images) for use with KaraKara.

Efficiently monitor and detect changes to source videos, create processed media and create track datafile.

Example input:
```
source/My Video.mp4
source/My Video.srt
source/My Video.txt
```

Example output:
```
processed/z/zrYVkuc0Sn1.webm
processed/g/gESd0tcze9O.mp4
processed/x/xP_WJ0_44mv.avif
processed/x/xP_WJ0_44mv.webp
processed/tracks.json
processed/tracks.json.gz
```

Use
---

Below describes the intended modes of use

* Setup a Dropbox/TorrentSync/SyncThing *source media folder* for your contributors.
* Setup a Dropbox/TorrentSync/SyncThing *processed media folder* for your admins/encoders.
* `docker run -v /my/folder:/media/source -v /my/other/folder:/media/processed karakara/processmedia3`
* The container will then monitor the source folder for any type of media files, and write out
  karakara-formatted videos in the processed folder.


Architecture
------------
All of the processing revolves around a single "track list" data structure,
which looks like this:

```python
tracks = [
    # A Track represents an entry in tracks.json
    Track(
        id="My_Video",
        targets=[
            # A Target represents a file in the output directory
            Target(
                type=VIDEO_AV1,
                sources=[
                    # A Source is file in the input directory
                    Source(type=VIDEO, path="Anime/My Video.mp4")
                ]
            ),
            Target(
                type=SUBTITLE,
                sources=[
                    Source(type=SUBTITLE, path="Anime/My Video.srt")
                ]
            ),
            Target(
                type=IMAGE_WEBP,
                sources=[
                    Source(type=VIDEO, path="Anime/My Video.mp4")
                ]
            ),
        ]
    ),
    Track(
        id="Novid",
        targets=[
            Target(
                type=VIDEO_AV1,
                sources=[
                    Source(type=AUDIO, path="JPop/Novid.ogg")
                    Source(type=IMAGE, path="JPop/Novid.jpg")
                ]
            ),
            ...
        ]
    ),
    ...
]
```

`main.py` has a function for each step in the process:
- `scan()` looks at the input directory and creates the above list of Tracks
- `view()` iterates over each Track, and prints out data about them
- `encode()` iterates over each Track, and makes sure that each `Target` file
  exists, calling `target.encode()` to create it if needed
- `export()` iterates over each Track, converts it to JSON, and writes `tracks.json`
- `cleanup()` iterates over each Track, collecs a list of all Target filenames,
  and deletes any file in the output directory that we aren't expecting to exist

`lib/kktypes.py` has classes for `Source` / `Target` / `Track`

The above two are all of the high-level workflow; the rest of the code is more
specific implementation details for translating avi to webm, srt to vtt, etc.


Debugging Tools
---------------

* Raw python: `./main.py <command>`
    * You'll need to make sure the `--source` / `--processed` flags are set appropriately
* In docker: `docker compose run -ti processmedia3 <command>`
    * Docker automatically sets the `--source` / `--processed` flags based on `.env`
* Testing subtitle encoding
    * `./lib/subtitle_processor.py input.srt output.vtt`
* Encoding a single file into various formats to test with
    * `./main.py test-encode --reencode ~/Videos/kk-stress-test/demo.webm`

Commands: scan, view, encode, export, cleanup


Dev Setup
---------
```
python3 -m venv venv
source venv/bin/activate
pip install -e .
./main.py --help
```
