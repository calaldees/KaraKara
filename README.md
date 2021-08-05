KaraKara
========

Karaoke Event System - hosted at [karakara.uk](http://karakara.uk/)

* Run small events in your livingroom or big events with multiple karaoke rooms
* Attendees view and queue tracks from their mobile phones
* A Projector/TV shows a HTML5 player
* Internet connection is required

Overview of a karaoke event
---------------------------

A projector is fired up in a dimly lit room and a microphone stands ready on the mic stand. The PA is buzzing lightly. The attendees slowly enter the room. But this time is different. They look at the familiar paper printed list of tracks on the tables but also notice signs on the walls and a title-sheet that says *use your mobile*. Some continue to peruse the paper printouts while others are greeted with a mobile / tablet / laptop web interface to browse, search, see preview videos of tracks, lists of lyrics, see the current queued tracks with estimated times. Queue a track themselves. Pass the device to a friend to browse and queue a track under a different name.

A laptop at the front is connected to the projector. It is running a karakara.uk with a pre-processed tagged dataset of tracks in various formats.

Admins can walk around the room, remotely controlling when tracks are played fullscreen, re-ordering tracks, viewing feedback from attendees. Yet a desk at the front is still taking face to face song requests.

(When the project was started we could not rely on a venues reliable free wifi and 4g didnt exist. A pysical server and wireless router were needed in the room. Since then the project has evolved to be 'Karaoke as a service' run on an external webserver.)


### Headline Feature Descriptions ###

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
* Priority Token System
    * We want to prevent the situation where an event opens at 7pm and within 10 minuets we have a full queue till 11pm. Users will know their track will start at 9:45, leave then room, and only return for their track.
    * When adding a track once the queue becomes full (e.g 30 mins [configurable] of tracks), the user gets issued a 'priority token' and informed that in 'x minuets' their device will have priority to queue a track.
    * Visual feedback counts down for the user to identify this time window.
    * When in the 'priority' period the device ui highlights informing the user 'you can queue a track'.
    * These 'time window' tokens ensure that users who are diligent are guaranteed a time-slot over abusive users just hammering 'queue track' repeatedly.
    * It is worth noting that we do not know the length of the track the priority user may pick in advance. Tokens by default are issued 5 minutes (default) apart. Some users might pick tracks 1:30 long or maybe 5:50 long or even miss their priority slot. Users without a priority token may still be able to queue a track in if the total queue length is short enough, but at least the 'priority token users' are consistently informed of a guaranteed behaviour.
* Queue obfuscation and segmentation
    * We want users to know if they will be performing within the next 30 minuets (configurable) to know a rough time. If we provide the entire queue list with estimated times and an administrator identifies 3 long boring slow songs queued next to each other and decides to reorder the playlist slightly to assist the flow / mood of the event. Some users could see they have been put back a few tracks and become disgruntled (because of course it's their god given right to queue a track, how dare their sacred performance be postponed for lesser mortals).
    * Track estimations are displayed up to a configurable time (e.g 30 mins). After that point tracks are displayed in a deliberate random order. Users who have queued track passed this 'obfuscation threshold' see their request clearly listed and acknowledged, yet provides admins with curated control.
* Notable Settings
    * Disable mobile queuing
        * If the mobile interface is being abused or an event organiser wants to engage with users face to face before queuing a track, users can still view tracks / lyrics with their mobiles but not queue them directly.
    * Disable mobile interface
        * If the interface is being abused or is causing a performance problem for the projector. The system can remain running for admins and the interface can be disabled.
    * Performer name limit
        * Performer 'bob' can't queue more than 2 tracks within a time-period
    * Track repeat limit
        * Limit how many times a single track can be queued within a time-period. (We don't want 5 Pokemon's in one evening)
    * Event end
        * We don't want to knowingly allow users to queue tracks to 12:30 when we know the event will be finishing at 12:00. That would lead to lots of disappointed people.
* Audio Normalization
    * During processing sound levels are normalized. Some tracks could be slow quiet ballads while others or ripping metal operas. Technical admins needed to often adjust the volume of the microphone at the beginning of a song to compensate for the track volume differences. While normalization does not remove the problem (as different vocalists will use the mic in different ways), it does reduce the problem.
* Wide variety of data formats supported
    * Originally videos with subtitle files was the only way to add a track. Some vocal-less versions of the track are published or full length version that are longer than the 1:30 original intro. To facilitate this, the following formats are supported
    * Image + MP3 + SRT
    * Video + SRT
        * Various formats and codecs (including RM, gah!)


Local Machine Setup
-------------------

Configure site settings (eg which folders contain your media):
```
$ cp .env.example .env
```
Then edit settings in .env

Pre-built software, if you just want to run the site:
```console
$ docker-compose pull
$ docker-compose up
```

Compile your own software, if you want to make customisations or build new features:
```console
$ docker-compose build
$ docker-compose up
```

Core components
---------------

![Diagram](https://raw.githubusercontent.com/calaldees/KaraKara/master/docs/architecture.png)

* processmedia2 ![ProcessMedia2](https://github.com/calaldees/KaraKara/workflows/ProcessMedia2/badge.svg)
  * Takes folders of source data (video, image+mp3, subtitles)
  * Hard subbed final video
    * this high bitrate mp4 is presented via the player interface.
  * Low bitrate previews for mobile devices
    * Currently just mp4 but could support other formats in future.
  * Thumbnail images
    * Each video has 4 images taken at even intervals
  * SRT subtitles
    * regardless of input format, a normalised srt will be created for each video
  * JSON metadata
    * Once scanned, each item will have JSON data containing the hashes of
      source data
  * Pushes / Imports track data by calling `website` api.
* website ![Website](https://github.com/calaldees/KaraKara/workflows/Website/badge.svg)
  * API server
    * `track`, `search`, `queue`, `settings`
    * `track_import` endpoint (for imports from processmedia2)
  * Produces printable hard copy track lists for use without mobile interface
  * Community interface
    * A dynamic web app to facilitate the duration of track content
      * preview high and low res encoded videos
      * tag videos
      * edit subtitles
* browser2 ![Browser2](https://github.com/calaldees/KaraKara/workflows/Browser2/badge.svg)
  * Mobile webapp interface to search / preview / queue tracks
  * Gets data from website / `track_list` api
* player2 ![Player2](https://github.com/calaldees/KaraKara/workflows/Player2/badge.svg)
  * Displays the current queue for use on a projector
  * Gets data from website / `queue` api
  * Streams final video from `nginx` in fullscreen mode.
  * Can be controlled via hotkeys or remotely with websockets
  * Automatically updates track list when the queue is changed.
  * Queue order is obscured past a configurable time
* nginx ![Nginx](https://github.com/calaldees/KaraKara/workflows/Nginx/badge.svg)
  * Accepts HTTP requests and forwards them to the API / various GUIs as appropriate
* postgres ![Postgres](https://github.com/calaldees/KaraKara/workflows/Postgres/badge.svg)
  * Main database / long-term data storage for the track database and queues
