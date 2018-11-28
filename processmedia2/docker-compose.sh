#!/bin/bash
set +x
PATH_HOST=$(pwd)
docker-compose run --rm processmedia2 bash
