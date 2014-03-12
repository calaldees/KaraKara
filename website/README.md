KaraKara README
===============

Installation
------------

Linux - ubuntu

git clone git://github.com/calaldees/KaraKara.git && cd KaraKara/website && make test && make run


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


Todo
----

* player
  * prevent popup each change of track
  * rickroll button
* mobile interface
  * message language
    * duplicate performer explanation
    * duplicate track explantion and exirey
    * more detail in rejection messages
  * responsive
    * Responsive layout for tablets and landscape displays for track list.
  * individual devices
    * messaging
    * disabling/rickrolling
  * admin:
    * alerts for feedback messages
    * when remove track - prompt for optional message to user
    * way of recovering tracks that have been played/skipped (just in case of crash or problem)
  * search
    * search id first then tags?
* server
 * multiple queues
 * per phone limit?
 * request limit of assets?
 * session_owner bound to ip address, reject if they don't match - production only setting (better than obscurning in API for cache reasons+simplicity)
 * disbale device on mac address
   * lock mac address to ip address
 * queue
   * validate + limit to badge name
* comunity
  * tag editor (per track importing)
  * encode queue + feedback


flash message:
  query session+queid 'refresh required'
  you're up in 'xx' min (client cookie)


Bugs
----

status_error message style dose not propergate to flash message with format='redirect'
 - flash message from queue.py error (e.g. duplicate performer) is not styled as error but looks like success. feedback error is displayed appropriately. so what gives?!
 
Starting the player interface directly on the 'player.html' before visiting the normal mobile view fails. This is because the access to .html does not generate a session id and admin mode cannot be aquired
