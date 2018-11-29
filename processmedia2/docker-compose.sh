#!/bin/bash
set +x
PATH_HOST_REPO=$(pwd)
docker-compose run --rm processmedia2 bash
