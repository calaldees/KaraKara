DOCKER_IMAGE:=processmedia3
DOCKER_RUN_ARGS:=\
	--rm \
	--volume ${PWD}:/app/:ro

#run:
#	docker build --tag ${DOCKER_IMAGE}_production --target production .
#	docker run ${DOCKER_RUN_ARGS} ${DOCKER_IMAGE}_production

build:
	docker build --tag ${DOCKER_IMAGE} --target test .
shell:
	docker run ${DOCKER_RUN_ARGS} -it ${DOCKER_IMAGE} /bin/sh



.PHONY: cloc
cloc:
	cloc --vcs=git