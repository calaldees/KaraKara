KaraKara README
===============

Getting Started
---------------

```bash
    # local standalone dev version
    make build
    make run
    # http://localhost:6543/
```
(TODO: resolve this)
* docker run --rm -p 0.0.0.0:6543:6543 -t $(docker build -q .)
* open http://localhost:6543/


Features
--------

API


Todo
----

* mobile interface
  * general design
  * fix message/token layout issue (!)
  * message language
    * duplicate performer explanation
    * duplicate track explantion and exirey (!)
    * more detail in rejection messages (!)
  * responsive (tablet support)
    * Responsive layout for tablets and landscape displays for track list. (!)
  * individual devices
    * messaging - save to cookie, notifications in top tray (2)
    * disabling/rickrolling
  * admin:
    * alerts for feedback messages
    * when remove track - prompt for optional message to user (2)
    * way of recovering tracks that have been played/skipped (just in case of crash or problem)
    * rejected messages (duplicate performer limit, etc) (log 2)
    * priority token assignment (log 2)
* server
  * multiple queues
    * create (if superuser)(private/public queue)
    * destroy (if owning superuser)
  * per phone limit?
  * request limit of assets?
  * session_owner bound to ip address, reject if they don't match - production only setting (better than obscurning in API for cache reasons+simplicity)
  * year tag and year range
  * items other than videos in queue (text annoncements, images)
  * archive songs played for reference later (log 2)
  * message system to class messages (both community and mobile)
* community (!)
  * tag editor (per track importing)
    * tag warning if missing list
    * video qa checked
    * known isues list, unchecked list
  * encode queue + progress feedback
  * delete/rename track
  * played tracks list (partof admin? or community?)
    * score = (times actually played * 10) + (times requested * 5) + (page views * 1)
* admin panel
  * log statistics to es (2)
  * provides
    * page views ranked
    * track requests
    * number played
    * user device history (could be interface with device messaging, disabling, live updating)
    * events (errors, messages)
    * device disabling
    * name devices
    * event summary (scoring system) (partof admin? or community?)


flash message:
  query session+queid 'refresh required'
  you're up in 'xx' min (client cookie)


Bugs
----


status_error message style dose not propergate to flash message with format='redirect'
 - flash message from queue.py error (e.g. duplicate performer) is not styled as error but looks like success. feedback error is displayed appropriately. so what gives?!



Karakara Community
==================

Web interface for managing a closed community to curate the track dataset

Improve dataset
  * Tagging tracks for exploration
    * Multiple titles (eng/jap names)
    * Artists + extra data (where possible)
  * Quality checking
    * Timing
    * Subtitle size/colour/readabilty
    * Video quality (working state?)
  * Upgrading quality of old source footage
  * Adding alternate versions
    * Instrumental (vocal off)
    * Long/Short versions


Flags
 * Broken
 *
