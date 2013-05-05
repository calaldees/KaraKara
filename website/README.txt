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

queue track order + admin change + list obscure

todo
log.info access to files for profiling
flash message:
  query session+queid 'refresh required'
  your up in 'xx' min
per phone limit?
duplicate name warning - one track
print css
session_owner bound to ip address, reject if they don't match - production only setting (better than obscurning in API for cache reasons+simplicity)
ini option to disable track adding by phones (just in case it get abused and needs turning off)
messaging/disabling individual devices

status_error message style dose not propergate to flash message with format='redirect'