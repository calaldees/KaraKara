DOCKER_IMAGE:=api_queue
DOCKER_RUN_ARGS:=\
	--rm \
	--volume ${PWD}:/app/:ro \
	--publish 1337:1337 \

run:
	docker build --tag ${DOCKER_IMAGE}_production --target production .
	docker run ${DOCKER_RUN_ARGS} ${DOCKER_IMAGE}_production

build:
	docker build --tag ${DOCKER_IMAGE} --target test .

shell:
	docker run ${DOCKER_RUN_ARGS} -it ${DOCKER_IMAGE} /bin/sh
