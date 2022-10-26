processmedia2
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
    * more
* encode
    * more
* export
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
    * `/logs/`


References
----------

* https://dev.to/faraixyz/converting-video-into-animated-images-using-ffmpeg-3cng
* https://jakearchibald.com/2020/avif-has-landed/
    * https://lobste.rs/s/hjz9uo/avif_has_landed
        * rant about why av1 has not reached penetration yet
* https://darekkay.com/blog/avif-images/
* https://evilmartians.com/chronicles/better-web-video-with-av1-codec
    * video sourceset with codec in mime
* https://www.contentful.com/blog/2021/11/29/load-avif-webp-using-html/

* https://en.wikipedia.org/wiki/FFmpeg#Image_formats
* https://caniuse.com/?search=image%20format

* avifenc # https://github.com/AOMediaCodec/libavif/blob/master/apps/avifenc.c
* apk add libavif-apps (or something - search the alpine package repo)
* avifenc test.bmp test.avif # 13k

* https://askubuntu.com/questions/1189174/how-do-i-use-ffmpeg-and-rav1e-to-create-high-quality-av1-files
* https://www.mlug-au.org/lib/exe/fetch.php?media=av1_presentation.pdf

* https://codepen.io/cloudunder/post/hevc-html5-video
* https://streaminglearningcenter.com/codecs/encoding-vp9-in-ffmpeg-an-update.html

* https://caniuse.com/?search=video%20gformat
    * https://trac.ffmpeg.org/wiki/Encode/AV1
    * https://trac.ffmpeg.org/wiki/Encode/VP9
    * https://trac.ffmpeg.org/wiki/Encode/H.265
