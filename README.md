KaraKara
========

Karaoke Event System - Attendees view and queue tracks from their mobile phones

    git clone https://github.com/calaldees/KaraKara.git


Setup
-----

* Copy video dataset OR Process video dataset from avi/mpg/srt/png/mp3 files with processmedia
* Option 1 - Vagrant (Linux/Mac/Windows)
   1. install VirtualBox: <http://www.virtualbox.org/>
   2. install Vagrant: <http://www.vagrantup.com/>
   3. navigate to data folder
   4. Download Vagrantfile and Bootstrap: (Linux/Mac can use `curl -O https://raw.github.com/calaldees/KaraKara/master/vagrant/Vagrantfile && curl -O https://raw.github.com/calaldees/KaraKara/master/vagrant/vagrant_bootstrap.sh`) (Windows just download the files)
   5. `vagrant up`
   5. view <http://localhost:6543/> and <http://localhost:6543/player/player.html/>
* Option 2 - Linux/Mac (native with sqllite dev db)
   1. navigate to data folder
   2. `git clone https://github.com/calaldees/KaraKara.git && ln -s . KaraKara/mediaserver/www/files && cd KaraKara/website && make setup && make test && make import_tracks_dev && make run`
   3. view <http://localhost:6543/> and <http://localhost:6543/player/player.html/>



Core components
---------------

* processmedia
  * takes folders of source data (video, image+mp3, subtitles)
  * creates hard subbed final video
  * low bitreate previews
  * tumbnail images
  * json metadata
* website
  * jquerymobile web interface to search/preview/queue tracks
    * imports data into local db from output from processmedia
    * produces printable hard copy track lists for use without mobile interface
  * queueplayer
    * html5 event display player (browser must support mp4 video)
    * looks at website/queue api
    * streams final video from mediaserver
* mediaserver
  * nginx webserver to proxy website(pyramid) and serve datafiles efficently
  * postgresql database for prouction.ini configuration


Additional components
---------------------

* taginput
  * lightweight python web interface to enable external contributors to edit tags
 
 
Setup (extended)
----------------

* Each component has it's own readme.txt and requirements.
* Makfiles are provided for Linux setup

