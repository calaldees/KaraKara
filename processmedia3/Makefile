DOCKER_IMAGE:=processmedia3
DOCKER_RUN_ARGS:=\
	--rm \
	--volume ${PWD}:/app/:ro \
	--volume $(realpath ../media/source):/media/source:ro \
	--volume $(realpath ../media/processed):/media/processed:rw \
	--volume ${PWD}/logs:/logs:rw

#run:
#	docker build --tag ${DOCKER_IMAGE}_production --target production .
#	docker run ${DOCKER_RUN_ARGS} ${DOCKER_IMAGE}_production

build:
	docker build --tag ${DOCKER_IMAGE} --target test .
shell: logs
	docker run ${DOCKER_RUN_ARGS} -it ${DOCKER_IMAGE} /bin/sh
logs:
	mkdir logs
run_local:
	python3 main.py --source ../media/source --processed ../media/processed --log-file logs/processmedia3.log --debug

.PHONY: cloc
cloc:
	cloc --vcs=git