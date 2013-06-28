h1. KaraKara

* Karaoke Event System - Attendees view and queue tracks from their mobile phones *


h2. Core components

* processmedia
    ** takes folders of source data (video, image+mp3, subtitles)
    ** creates hard subbed final video
    ** low bitreate previews
    ** tumbnail images
    ** json metadata
* website
    ** jquerymobile web interface to search/preview/queue tracks
        *** imports data into local db from output from processmedia
        *** produces printable hard copy track lists for use without mobile interface
    ** queueplayer
        *** html5 event display player (browser must support mp4 video)
        *** looks at website/queue api
        *** streams final video from mediaserver
* mediaserver
    ** nginx webserver to proxy website(pyramid) and serve datafiles efficently


h2. Additional components

* taginput
    ** lightweight python web interface to enable external contributors to edit tags
 
 
h2. Setup

* Each component has it's own readme.txt and requirements.
* Makfiles are provided for Linux setup
* Windows/Mac
** install http://www.vagrantup.com/
** vagrant box add precise32 http://files.vagrantup.com/precise32.box
** vagrant up
* copy/mount media files to mediaserver/www/files
