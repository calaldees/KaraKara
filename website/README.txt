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
  your up in 'xx' min (client cookie)
per phone limit?
print css
session_owner bound to ip address, reject if they don't match - production only setting (better than obscurning in API for cache reasons+simplicity)
messaging/disabling individual devices
way of recovering tracks that have been played/skipped (just in case of crash or problem)

status_error message style dose not propergate to flash message with format='redirect'