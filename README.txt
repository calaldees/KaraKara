KaraKara
Karaoke Event System - Attendees view and queue tracks from their mobile phones

Core components:
 -processmedia
    takes folders of source data (video, image+mp3, subtitles)
      creates hard subbed final video
      low bitreate previews
      tumbnail images
      json metadata
 -mediaserver
    nginx webserver to proxy website(pyramid) and serve datafiles
 -website
    jquerymobile web interface to search/preview/queue tracks
      imports data into local db from output from processmedia
      produces printable hard copy track lists for use without mobile interface
 -queueplayer
    html5 event display player
      looks at website/queue
      streams final video from mediaserver
 
Additional components:
 -taginput
    lightweight python web interface to enable external contributors to edit tags
 
