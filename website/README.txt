KaraKara README
==================

Getting Started
---------------

make setup
make init_db_test
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

ini option to disable track adding my phones (just in case it get abused and needs turning off)
messaging/disabling individual devices