shell:
	docker-compose run --rm --service-ports api_queue /bin/sh


# Standalone api_queue container -----------------------------------------------

DOCKER_IMAGE:=api_queue
DOCKER_RUN_ARGS:=\
	--rm \
	--volume ${PWD}:/app/:ro \
	--publish 1337:1337 \

_run:
	docker build --tag ${DOCKER_IMAGE}_production --target production .
	docker run ${DOCKER_RUN_ARGS} ${DOCKER_IMAGE}_production
_build:
	docker build --tag ${DOCKER_IMAGE} --target test .
_shell:
	docker run ${DOCKER_RUN_ARGS} -it ${DOCKER_IMAGE} /bin/sh

local_run:
	python3 -m sanic api_queue.server.app --host 0.0.0.0 --port 1337 --workers 4 --debug
