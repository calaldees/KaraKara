processmedia2
=============

Encode videos for use with KaraKara.

Efficently monitor and detect changes to source videos, create proccssed media and import into KaraKara track database.

Example input

    source/My Video.avi
    source/My Video.srt
    source/My Video.txt

Example Output

    processed/BIG-HASH1.mp4
    processed/BIG-HASH2.mp4
    processed/BIG-HASH3.jpg
    processed/BIG-HASH4.jpg
    processed/BIG-HASH5.jpg
    processed/BIG-HASH6.jpg
    processed/BIG-HASH7.srt


Processing Steps
----------------

* scan
    * more
* encode
    * more
* import
    * more
* cleanup
    * more


Use
---

Below describes the intended modes of use

* Setup a Dropbox/TorrentSync/SyncThing *source media folder* for your contributors.
* Setup a Dropbox/TorrentSync/SyncThing *processed media folder* for your admins/encoders.
* `make install && make test`
* edit `config.json` to point to *source*, *meta* and *processed* paths
* Setup a __cron to `make run` every 10 mins__ (need to think of more efficent way)


Debuging Tools
--------------

* metaviewer
    * `./metaviewer regex_name`
* logs
    * 