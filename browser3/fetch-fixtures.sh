#!/bin/sh
curl https://karakara.uk/files/tracks.json -o cypress/fixtures/tracks.json
curl https://karakara.uk/room/minami/settings.json -o cypress/fixtures/settings.json
curl https://karakara.uk/room/minami/queue.json -o cypress/fixtures/queue.json
