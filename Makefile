-include .env

SHELL := $(SHELL) -e
ENV:=_env
PROJECTS = processmedia2 website admindashboard


.PHONY: help
.DEFAULT_GOAL:=help
help:	## display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-8s\033[0m %s\n", $$1, $$2 } END{print ""}' $(MAKEFILE_LIST)

.env:
	cp .env.example .env


# Docker ----------------------------------------------------------------------

_DOCKER_COMPOSE:=USER=$(shell id -u):$(shell id -g) docker-compose
DOCKER_COMPOSE:=${_DOCKER_COMPOSE} --file docker-compose.yml


docker_build: .env
	docker-compose build
docker_shell_website:  ## start + shell into website only
	docker-compose run --rm --service-ports website /bin/bash
	# Import community user notes
	#docker-compose run -v ~/karakara_users.sql:/data/karakara_users.sql:ro postgres /bin/bash
	#  psql -h postgres -U karakara karakara -f /data/karakara_users.sql
docker_exec_website:  ## website shell (currently running container)
	docker-compose exec website /bin/bash
docker_exec_psql:  ## psql shell (currently running container)
	docker-compose exec postgres psql karakara --user karakara
docker_up:
	docker-compose up
docker_stop:
	docker-compose stop
pull:  # pull + rebuild + run
	git pull && docker-compose stop && docker-compose up --build -d


test_cypress_run:  ## cypress browser tests
	${_DOCKER_COMPOSE} --file docker-compose.test.yml run --rm test_cypress
#test_cypress_cmd:
#	${_DOCKER_COMPOSE} --file docker-compose.cypress.yml \
#		run --rm client_test \
#			${CYPRESS_CMD}
#test_cypress_gui:  ## Launch local cypress from container (requires an XServer and DISPLAY env)
#	${DOCKER_COMPOSE_TEST} run --rm --env DISPLAY test_cypress open --project .
#	${DOCKER_COMPOSE_TEST} down



# Cloc ------------------------------------------------------------------------

.PHONY: cloc
cloc:
	cloc --vcs=git
