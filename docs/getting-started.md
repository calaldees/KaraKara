Getting Started with KaraKara
=============================

unfinished...

karakara.uk Tour
-----------

* https://karakara.uk/
    Room: test
* https://karakara.uk/player2/
* double click title banner
    * username: test, password: test
* Developers
    * https://karakara.uk/docs
    * https://karakara.uk/community2/queue_view.html#test


Run it locally
--------------

https://gitpod.io#https://github.com/calaldees/KaraKara

```bash
python3 media/get_example_media.py
docker-compose up --build

# see encoding progress
docker-compose exec processmedia2 /bin/bash
    python3 metaviewer.py
    top
    # KAT-TUN took 8min, Captain America took 25min (cpu is throttled after light use)

# api_queue -> track_id invalid
# when encoding complete - api_queue must be restarted to load new `tracks.json`
docker-compose restart api_queue
```
