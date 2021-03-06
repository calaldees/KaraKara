processmedia2
=============

Encode videos for use with KaraKara.

Efficiently monitor and detect changes to source videos, create processed media and import into KaraKara track database.

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
* `docker run -v /my/folder:/media/source -v /my/other/folder:/media/processed karakara/processmedia2`
* The container will then monitor the source folder for any type of media files, and write out
  karakara-formatted videos in the processed folder.


Debugging Tools
---------------

* metaviewer
    * `./metaviewer regex_name`
* logs
    *


Future Development Notes
------------------------

    https://hub.docker.com/r/jrottenberg/ffmpeg/
    docker pull jrottenberg/ffmpeg
    docker run --rm -it jrottenberg/ffmpeg

    https://forums.docker.com/t/how-can-i-run-docker-command-inside-a-docker-container/337/2
    docker run -it -v /var/run/docker.sock:/var/run/docker.sock ubuntu:latest sh -c "apt-get update ; apt-get install docker.io -y ; bash"
