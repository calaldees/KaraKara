-include .env

SHELL := $(SHELL) -e
ENV:=_env
PROJECTS = processmedia2 website admindashboard


.PHONY: help
help:
	# Karakara - Karaoke event system
	#
	# This Makefile is being reconsidered - try `docker-compose up`


.env:
	cp .env.example .env


# Docker ----------------------------------------------------------------------

docker_build: .env
	docker-compose build
docker_shell_website:
	docker-compose run --rm --service-ports website /bin/bash
	# Import community user notes
	#docker-compose run -v ~/karakara_users.sql:/data/karakara_users.sql:ro postgres /bin/bash
	#  psql -h postgres -U karakara karakara -f /data/karakara_users.sql
docker_exec_website:
	docker-compose exec website /bin/bash
docker_exec_website_generate_static_track_list:  ## Shortcut for manually prompting static regen
	docker-compose exec website curl -X PATCH http://localhost:6543/track_import?format=json
docker_exec_psql:
	docker-compose exec postgres psql karakara --user karakara
docker_up:
	docker-compose up
docker_stop:
	docker-compose stop
pull:
	git pull && docker-compose stop && docker-compose up --build -d

# Cloc ------------------------------------------------------------------------

.PHONY: cloc
cloc:
	cloc --vcs=git
