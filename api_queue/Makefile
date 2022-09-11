shell:
	docker-compose build api_queue
	docker-compose run --rm --service-ports api_queue

# /bin/bash


# Standalone api_queue container -----------------------------------------------

DOCKER_IMAGE:=api_queue
DOCKER_RUN_ARGS:=\
	--rm \
	--volume ${PWD}:/app/:ro \
	--env SANIC_PATH_QUEUE=/data/queue/ \
	--publish 8000:8000 \

_run:
	docker build --tag ${DOCKER_IMAGE}_production --target production .
	docker run ${DOCKER_RUN_ARGS} ${DOCKER_IMAGE}_production
_build:
	docker build --tag ${DOCKER_IMAGE} --target test .
_shell:
	docker run ${DOCKER_RUN_ARGS} -it ${DOCKER_IMAGE} /bin/bash

local_run:
	python3 -m sanic api_queue.server.app --host 0.0.0.0 --port 8000 --workers 4 --debug --auto-reload --access-logs


.PHONY: cloc
cloc:
	cloc --vcs=git