api_queue
=========

* no database
    * Redis datastore for queues.
    * (no need to have any info/coupling about tracks)
* sqlite3 for community login tokens?



* asgi
    * [sanic](https://sanic.dev/en/plugins/sanic-ext/getting-started.html#features)
    * https://aioredis.readthedocs.io/en/latest/getting-started/
    * [sanic-jwt](https://sanic-jwt.readthedocs.io/en/latest/pages/simpleusage.html)
* mqtt
    * [aiormq](https://github.com/mosquito/aiormq) - Pure python AMQP 0.9.1 asynchronous client library 
    * [paho-mqtt](https://pypi.org/project/paho-mqtt/) - MQTT version 5.0/3.1.1 client class
* redis
    * [redis-py](https://github.com/redis/redis-py) - aoi?


queue datamodel
---------------

Don't need JSON - newline text? split? No need for field names? `test/csv` records? (no heading?)

```csv
track_id,performer_name,session_owner,timestamp_play
abc123,MahName1,xyz456,1661094171425
def456,MahName2,xyz457,1661094271426
```


api
---

* /queue/
    * GET (admin)
        * list
    * POST
        * new queue (demo - 10 tracks?)
        * new queue (transient)
        * new named queue (admin)
* /queue/XYZ/
    * DELETE queue
* /queue/XYZ/settings
    * GET
    * POST/PUT (admin)
        * queue limit model (priority token or points)
* /queue/XYZ/tracks
    * GET
        * 302 redirect to static track_datafile from hash of filter_tags
* /queue/XYZ/items
    * GET (only used for testing - this is pushed to mqtt)
    * POST (limit owner or admin)
        * name, trackid
        * return id
* /queue/XYZ/items/ABC
    * DELETE (owner or admin only)
    * PUT (admin)
        * (weight, timestamp_play)
