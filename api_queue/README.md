# api_queue

* An API for managing queues
* Users can add tracks to the queue
* Tracks will be validated to make sure one user isn't filling the whole queue, and nobody can add tracks past the end of the event time limit
* Admins can re-order and delete tracks


## data model

Don't need JSON - newline text? split? No need for field names? `test/csv` records? (no heading?)

```csv
track_id,performer_name,session_owner,timestamp_play
abc123,MahName1,xyz456,1661094171425
def456,MahName2,xyz457,1661094271426
```


## curls

```
curl -X GET http://localhost:8000/room/test/tracks.json

curl -X GET http://localhost:8000/room/test/queue.csv
curl -X GET http://localhost:8000/room/test/queue.json
curl -X POST --cookie "session_id=test" http://localhost:8000/room/test/queue.json -d '{"track_id": "KAT_TUN_Your_side_Instrumental", "performer_name": "test"}'

curl -X POST --cookie "session_id=admin" http://localhost:8000/room/test/login.json -d '{"password": "test"}'
curl -X DELETE --cookie "session_id=admin" http://localhost:8000/room/test/queue/8684541502363635.json
curl -X PUT --cookie "session_id=admin" http://localhost:8000/room/test/queue.json -d '{"source": 543, "target": 223}'

curl -X GET http://localhost:8000/room/test/settings.json
curl -X PUT --cookie "session_id=admin" https://karakara.uk/room/test/settings.json -d '{"track_space": 42}'

curl -X GET --cookie "session_id=admin" http://localhost:8000/room/test/command/play.json
curl -X GET --cookie "session_id=admin" http://localhost:8000/room/test/command/stop.json
```


## utils

```
docker compose exec api_queue ./analytics.py
```
