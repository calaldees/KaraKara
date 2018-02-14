include .env._base
include .env._rsync

SHELL := $(SHELL) -e
ENV:=_env
PROJECTS = processmedia2 website player mediaserver admindashboard


.PHONY: help
help:
	# Karakara - Karaoke event system
	#  (propergate to all projects)
	#   install
	#   test
	#   clean
	#
	#  (top level)
	#   docker_build -> docker_run
	#   rsync_pull
	#   cloc


.env:
	cp $@._base $@
	cat $@._local >> $@


# Docker ----------------------------------------------------------------------

docker_build: .env
	docker-compose build
	docker-compose run --rm website $(PATH_CONTAINER_SCRIPTS)/_install.sh
docker_shell:
	docker-compose run --rm --service-ports website /bin/bash
docker_exec:
	docker exec -it karakara_website_1 /bin/bash
docker_run:
	docker-compose --file docker-compose.yml up

# Rsync -----------------------------------------------------------------------

RSYNC_ARGS:=--archive --no-perms --no-owner --no-group --verbose --stats --progress --human-readable --append-verify --exclude '.*' --exclude 'backup'
#--update --copy-links --checksum --bwlimit=100 --inplace --partial --timeout 30 --checksum
rsync_pull:
	rsync $(RSYNC_REMOTE) $(RSYNC_LOCAL) -e ssh $(RSYNC_ARGS) --delete-after
rsync_push:
	rsync $(RSYNC_LOCAL) $(RSYNC_REMOTE) -e ssh $(RSYNC_ARGS) --dry-run
rsync_local_push:
	rsync $(RSYNC_LOCAL)/meta/ $(RSYNC_LOCAL_TARGET)/meta/ $(RSYNC_ARGS) --delete-after
	rsync $(RSYNC_LOCAL)/processed/ $(RSYNC_LOCAL_TARGET)/processed/ $(RSYNC_ARGS) --delete-after

# Install ---------------------------------------------------------------------

.PHONY: install
install: .env
	for project in $(PROJECTS); do \
		$(MAKE) install --no-keep-going --directory $$project ; \
	done

# Test ------------------------------------------------------------------------

.PHONY: test
test:
	for project in $(PROJECTS); do \
		$(MAKE) test --no-keep-going --directory $$project ; \
	done

# Cloc ------------------------------------------------------------------------

.PHONY: cloc
cloc:
	cloc --exclude-dir=$(ENV),libs ./

# Clean ------------------------------------------------------------------------

.PHONY: clean_osx_cancer
clean_osx_cancer:
	find ./ -iname \.DS_Store -delete

.PHONY: clean
clean: clean_osx_cancer
	rm -rf .cache .vagrant .env
	for project in $(PROJECTS); do \
		$(MAKE) clean --directory $$project ; \
	done

