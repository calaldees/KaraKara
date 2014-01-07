KaraKara README
===============

Installation
------------

Linux - ubuntu
 git clone git://github.com/calaldees/KaraKara.git && cd KaraKara/website && make install


Getting Started
---------------

Linux
git clone <git repo>
make install
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
----

log.info access to files for profiling
flash message:
  query session+queid 'refresh required'
  your up in 'xx' min (client cookie)
per phone limit?
print css
session_owner bound to ip address, reject if they don't match - production only setting (better than obscurning in API for cache reasons+simplicity)
messaging/disabling individual devices
way of recovering tracks that have been played/skipped (just in case of crash or problem)
Responsive layout for tablets and landscape displays for track list.


Bugs
----

status_error message style dose not propergate to flash message with format='redirect'
 - flash message from queue.py error (e.g. duplicate performer) is not styled as error but looks like success. feedback error is displayed appropriately. so what gives?!
 
