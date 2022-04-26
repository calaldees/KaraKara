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
```
QUEUE_KEY: [
    {
        "track_id": "BASE64HASH",
        "performer_name": 'str',
        "session_owner": '',
        "weight": float,
    }
    "timestamp_play": int,
]
```

api
---

* queue
    * new
        * new queue (demo - 10 tracks?)
        * new queue (transient)
        * new named queue (admin)
    * get_settings
    * set_settings (admin)
        * queue limit model (priority token or points)
    * del queue
    * get_tracks
        * redirect to static track_datafile from hash of filter_tags
* queue_items operations
    * get (only used for testing - this is pushed to mosquito)
    * add (limit owner or admin)
        * No validation of track_id
    * del (owner or admin only)
    * update (admin)
        * (weight, timestamp_play)
* root
    * queues (admin)
