processmedia3
=============

Encode media (videos + images) for use with KaraKara.

Efficiently monitor and detect changes to source videos, create processed media and create track datafile.

Example input

    source/My Video.mp4
    source/My Video.srt
    source/My Video.txt

Example Output

    processed/BIG-HASH1.webm (av1)
    processed/BIG-HASH2.mp4 (h265)
    processed/BIG-HASH3.avif * 4
    processed/BIG-HASH4.webp * 4

    # Entire track dataset in single static file (with txt and srt embeded)
    processed/track.json


Processing Steps
----------------

* scan
  * look through the source directory and figure out which tracks exist
* encode
  * ensure that all tracks have their expected attachments in the processed directory
* export
  * write the metadata database into tracks.json
* cleanup
  * delete any files which aren't associated with any known sources

running main.py with no specific subcommand will run scan + encode + export + dry-run cleanup


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
`main.py` has a function for each step (scan, view, encode, export, cleanup),
and will call one or more of those functions, optionally in a loop.

`lib/kktypes.py` has classes for `Source` (a file in the source directory),
`Target` (a file in the processed directory) and Track (an entry in
`tracks.json`, which connects sources to targets)

The above two are all of the high-level workflow; the rest of the code is more
specific implementation details for translating avi to webm, srt to vtt, etc.


Debugging Tools
---------------

* `./main.py view` to show encoding status for all tracks
    * `./main.py view Haruhi` to only show status for Haruhi tracks
* logs
    * `/logs/`
