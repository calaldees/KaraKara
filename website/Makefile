help:
	# build:
	# build_prod:
	# run:
	# test:
	# shell:

build:
	docker build \
		--tag karakara:local \
		--target test \
		.

build_prod:
	docker build \
		--tag karakara:prod \
		--target production \
		.

DOCKER_RUN_LOCAL:=docker run -it --rm \
	--publish 6543:6543 \
	--volume=${PWD}:/app/:ro \
	karakara:local \
run:
	${DOCKER_RUN_LOCAL} pserve /appdata/config/development.ini
test:
	${DOCKER_RUN_LOCAL} pytest --ini_file=/appdata/config/test.ini
shell:
	${DOCKER_RUN_LOCAL} /bin/bash
