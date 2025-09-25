api_queue
=========

* no database
* sqlite3 for community login tokens?

* asgi
    * [sanic](https://sanic.dev/en/plugins/sanic-ext/getting-started.html#features)
    * [sanic-jwt](https://sanic-jwt.readthedocs.io/en/latest/pages/simpleusage.html)
* mqtt
    * [aiormq](https://github.com/mosquito/aiormq) - Pure python AMQP 0.9.1 asynchronous client library
    * [paho-mqtt](https://pypi.org/project/paho-mqtt/) - MQTT version 5.0/3.1.1 client class


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

* /room/
    * GET (admin)
        * list
    * POST
        * new room (demo - 10 tracks?)
        * new room (transient)
        * new named room (admin)
* /room/XYZ/
    * DELETE room
* /room/XYZ/settings
    * GET
    * POST/PUT (admin)
        * queue limit model (priority token or points)
* /room/XYZ/tracks
    * GET
        * 302 redirect to static track_datafile from hash of filter_tags
* /room/XYZ/items
    * GET (only used for testing - this is pushed to mqtt)
    * POST (limit performer_name or admin)
        * name, trackid
        * return id
* /room/XYZ/items/ABC
    * DELETE (session_id or admin only)
    * PUT (admin)
        * (weight, timestamp_play)


curls
-----

```
curl -X GET http://localhost:8000/room/test/tracks.json

curl -X GET http://localhost:8000/room/test/queue.csv
curl -X GET http://localhost:8000/room/test/queue.json
curl -X POST --cookie "session_id=test" http://localhost:8000/room/test/queue.json -d '{"track_id": "KAT_TUN_Your_side_Instrumental_", "performer_name": "test"}'
curl -X DELETE --cookie "session_id=admin" http://localhost:8000/room/test/queue/8684541502363635.json
curl -X PUT --cookie "session_id=admin" http://localhost:8000/room/test/queue.json -d '{"source": 543, "target": 223}'

curl -X GET http://localhost:8000/room/test/settings.json
curl -X PUT --cookie "session_id=admin" https://karakara.uk/room/test/settings.json -d '{"track_space": 42}'

curl -X GET --cookie "session_id=admin" http://localhost:8000/room/test/command/play.json
curl -X GET --cookie "session_id=admin" http://localhost:8000/room/test/command/stop/json
```
