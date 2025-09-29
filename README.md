KaraKara
========

Karaoke Event System - hosted at [karakara.uk](http://karakara.uk/)

* Run small events in your livingroom or big events with multiple karaoke rooms
* Attendees view and queue tracks from their mobile phones
* A projector/TV shows a playlist and subtitled videos
* An optional tablet can show the lyrics for singers to read on stage
* Internet connection is required


Quickstart Guides
-----------------
* [For people running events](docs/for-admins.md)
* [For people adding tracks to the database](docs/for-contributors.md)
* [For people developing the software](docs/for-developers.md)


Overview of a Karaoke Event
---------------------------

* A projector is fired up in a dimly lit room and a microphone stands ready on the mic stand. The PA is buzzing lightly. The attendees slowly enter the room. But this time is different. Attendees see advertised on the projector and "Join at `karakara.uk` room `eventname`" and a QRcode. A mobile / tablet / laptop interface to browse, search, see preview videos of tracks, lists of lyrics, see the current queued tracks with estimated times. Attendees can queue a track themselves. Pass the device to a friend to browse and queue a track under a different name.
* A laptop at the front is connected to the projector. It is running a `karakara.uk` with a pre-processed tagged dataset of tracks in various formats.
* Admins can walk around the room, remotely controlling when tracks are played fullscreen, re-ordering tracks, viewing feedback from attendees. Yet a desk at the front is still taking face to face song requests.


Headline Feature Descriptions
-----------------------------

* Track tagging with multiple exploration paths
    * Rather than just browsing tracks by title, tracks are surfaceable via different routes because they are tagged. e.g:
        * Tracks are in different *languages*. Singers not comfortable with Japanese can select English.
        * Tracks can be listed under multiple *titles*. English and Japanese names.
        * *Vocal style*; female, male, group
        * *track type*; short version, instrumental, full version, megamix version
        * *artist*
    * Tags are cumulative filters e.g.
        * english, group, anime
        * jpop, artist: bob
        * vocal-less, short, male
* Queue obfuscation and segmentation
    * We want users to know if they will be performing soon (configurable number of next tracks is displayed to users).
        * Imagine:
            * We provide attendees with the entire queue list with estimated times
            * an administrator identifies 3 long boring slow songs queued in sequence and decides to reorder the playlist slightly to assist the flow / mood of the event.
            * Some users could see they have been put back a few tracks and become disgruntled (because of course it's their right to queue a track, how dare their sacred performance be postponed for lesser mortals).
    * All later tracks are displayed in a deliberate random/obfuscated order. Users can see there track is queued/acknowledged, yet provides admins with curated control.
* Notable Settings
    * Event end (and start) times
        * We don't want to knowingly allow users to queue tracks to 12:30 when we know the event will be finishing at 12:00. That would lead to lots of disappointed people.
    * Optional: Allowed performer name list
        * A configurable list of allowed performer names can be provided
        * Performer 'bob' can't queue more than 2 tracks within a time-period
    * Automatic queued track reordering
        * WIP - not testing with a real audience yet.
        * The next X tracks are set in stone - everything after that is ordered based on duplicate performers and a song duration time.
    * Track repeat limit
        * Limit how many times a single track can be queued within a time-period. (We don't want 5 Pokemon's in one evening)
* Audio Normalization
    * During processing sound levels are normalized. Some tracks could be slow quiet ballads while others or ripping metal operas. Technical admins needed to often adjust the volume of the microphone at the beginning of a song to compensate for the track volume differences. While normalization does not remove the problem (as different vocalists will use the mic in different ways), it does reduce the problem.
* Wide variety of video/audio/subtitle formats supported
    * Originally videos with subtitle files was the only way to add a track. Some vocal-less versions of the track are published or full length version that are longer than the 1:30 original intro. To facilitate this, the following formats are supported
    * Image + Audio + Subtitle
    * Video + Subtitle
    * Hard-subbed Video
        * Various formats and codecs (including RM, gah!)


Core Components
---------------
* [processmedia3](processmedia3/README.md) ![ProcessMedia3](https://github.com/calaldees/KaraKara/workflows/ProcessMedia3/badge.svg)
  * Takes a folder of all kinds of source data (video, image+audio, subtitles)
  * Create consistently encoded outputs, and a track index in `tracks.json`
* [browser3](browser3/README.md) ![Browser3](https://github.com/calaldees/KaraKara/workflows/Browser3/badge.svg)
  * Mobile app to browse the data in `tracks.json`
  * Users can send tracks to the queue
* [api_queue](api_queue/README.md) ![ApiQueue](https://github.com/calaldees/KaraKara/workflows/ApiQueue/badge.svg)
  * Takes requests from users and commands from admins
  * Publishes the current queue to the player
* [player3](player3/README.md) ![Player3](https://github.com/calaldees/KaraKara/workflows/Player3/badge.svg)
  * Fullscreen video player for the projector
  * Displays the current queue in between tracks
