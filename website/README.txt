KaraKara README
==================

Installation
------------

Linux - ubuntu 12.10
 git clone git://github.com/calaldees/KaraKara.git && cd KaraKara && make setup && make test


Getting Started
---------------

git clone <git repo>
make setup
make test
make run
http://localhost:6543/


Features
--------

API
  User
    Browse
    Que(+/-)
    Fave(+/-)
    QueView
    TrackView(id)
    QueItemTouch(queid)
    TracksPrintable()
  Admin
    QueItemMove(queid,?)
    
todo
log.info access to files for profiling
flash message:
  query session+queid 'refresh required'
  your up in 'xx' min
per phone limit?
duplicate name warning - one track
queue track order + admin change + list obscure
print css

ini option to disable track adding by phones (just in case it get abused and needs turning off)
messaging/disabling individual devices