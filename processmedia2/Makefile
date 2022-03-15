.PHONY: help
.DEFAULT_GOAL:=help
help:	## display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-8s\033[0m %s\n", $$1, $$2 } END{print ""}' $(MAKEFILE_LIST)

# Variables --------------------------------------------------------------------

DOCKER_IMAGE:=karakara/processmedia2:local

# Docker -----------------------------------------------------------------------

build:  ##
	docker build \
		--tag ${DOCKER_IMAGE} \
		--target test \
		.

build_prod:  ##
	docker build --tag ${DOCKER_IMAGE} .

DOCKER_RUN_LOCAL:=docker run -it --rm \
	--volume=${PWD}:/processmedia2/:ro \
	${DOCKER_IMAGE}
run:  ##
	${DOCKER_RUN_LOCAL} processmedia2.sh
test:  ##
	${DOCKER_RUN_LOCAL} pytest
shell:  ##
	${DOCKER_RUN_LOCAL} /bin/bash


# Config -----------------------------------------------------------------------

config.json:
	cp config.json.dist config.json

logging.json:
	cp logging.json.dist logging.json

# Run --------------------------------------------------------------------------
.PHONY: scan encode import_media cleanup run

scan:
	python3 scan_media.py
encode:
	python3 encode_media.py --process_order_function random
import_media:
	python3 import_media.py --force
cleanup:
	python3 cleanup_media.py
run: scan encode import_media


# Test -------------------------------------------------------------------------
.PHONY: test
test:	##
	pytest processmedia_libs tests --doctest-modules

.PHONY: cloc
cloc: ##
	cloc --vcs=git

# Clean ------------------------------------------------------------------------

.PHONY: clean
clean:	##
	rm -rf .cache .pytest_cache __pycache__ config.json logging.json mtimes.json


# Dev

# rsync -e ssh --no-perms --no-owner --no-group --verbose --stats --progress --human-readable --recursive violet:/data/sync/kk-meta/ ./kk-meta/
# rsync -e ssh --no-perms --no-owner --no-group --verbose --stats --progress --human-readable --recursive --include='*.srt' --include='*/' --exclude='*' violet:/data/sync/kk-source/ ./kk-source/