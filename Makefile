-include .env

SHELL := $(SHELL) -e

.PHONY: help
.DEFAULT_GOAL:=help
help:	## display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-8s\033[0m %s\n", $$1, $$2 } END{print ""}' $(MAKEFILE_LIST)

# Required Files --------------------------------------------------------------

.env:
	cp .env.example .env
data/: data/mqtt data/logs data/queues
data/mqtt:
	mkdir -p $@
data/logs:
	mkdir -p $@
data/queues:
	mkdir -p $@


# Docker ----------------------------------------------------------------------

_DOCKER_COMPOSE:=USER=$(shell id -u):$(shell id -g) docker-compose
DOCKER_COMPOSE:=${_DOCKER_COMPOSE}

up: .env data/  ## run whole stack in docker compose
	docker compose up --build

deploy:  ##
	git pull && docker compose down && docker compose up --build --detach


# Example Data ----------------------------------------------------------------

get_example_media:  ##
	python3 processmedia3/get_example_media.py


# Cloc ------------------------------------------------------------------------

.PHONY: cloc
cloc:  ## count lines of code
	cloc --vcs=git
