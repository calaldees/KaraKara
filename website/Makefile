DOCKER_IMAGE:=karakara/website:local

.PHONY: help
.DEFAULT_GOAL:=help
help:	## display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-8s\033[0m %s\n", $$1, $$2 } END{print ""}' $(MAKEFILE_LIST)

build:  ##
	docker build \
		--tag ${DOCKER_IMAGE} \
		--target test \
		.

build_prod:  ##
	docker build \
		--tag karakara/website \
		.

DOCKER_RUN_LOCAL:=docker run -it --rm \
	--publish 6543:6543 \
	--volume=${PWD}:/app/:ro \
	${DOCKER_IMAGE}
run:  ##
	${DOCKER_RUN_LOCAL} pserve /appdata/config/development.ini
test:  ##
	${DOCKER_RUN_LOCAL} pytest --ini_file=/appdata/config/test.ini
shell:  ##
	${DOCKER_RUN_LOCAL} /bin/bash
