include .env

SHELL := $(SHELL) -e

ENV:=_env

.PHONY: help
help:
	# KaraKara

docker_build:
	docker-compose build
	docker-compose run --rm website $(PATH_CONTAINER_SCRIPTS)/_install.sh
docker_shell:
	docker-compose run --rm --service-ports website /bin/bash

#	docker run --rm -i -t karakara /bin/bash
#	docker build -t karakara --file karakara.Dockerfile .

#run_docker:
#	docker run -v "$(pwd):/karakara" --net=host appium

#run_production:
#	cd mediaserver ; $(MAKE) start_nginx
#	cd website ; $(MAKE) run_production

#init_random_production:
#	cd website ; env/bin/python -mkarakara.model.setup --config_uri production.ini --init_func karakara.model.init_data:init_data
#	cd website ; env/bin/python -mkarakara.scripts.insert_random_tracks 1200 --config=production.ini

#vagrant:
#	if dpkg -s vagrant ; then \
#		echo vagrant already installed; \
#	else \
#		echo installing vagrant ; \
#		sudo apt-get install vagrant -y ; \
#		vagrant box add precise32 http://files.vagrantup.com/precise32.box ; \
#	fi
#	cd vagrant ; vagrant up

#del_osx_cancer:
#	find ~/Applications/KaraKara/files/ -iname \.DS_Store -delete

RSYNC_ARGS:=--archive --no-perms --no-owner --no-group --verbose --stats --progress --human-readable --update --inplace --partial --exclude '.*' --exclude 'backup'
#--partial --update --copy-links --checksum --update --bwlimit=100
RSYNC_LOCAL:=~/Applications/KaraKara/files
RSYNC_REMOTE:=calaldees@violet.shishnet.org:/data/media_upload/
rsync_pull:
	rsync $(RSYNC_REMOTE) $(RSYNC_LOCAL) -e ssh $(RSYNC_ARGS) --delete-after
rsync_push:
	rsync $(RSYNC_LOCAL) $(RSYNC_REMOTE) -e ssh $(RSYNC_ARGS)

RSYNC_LOCAL_TARGET:=/Volumes/Samsung_T1/KaraKara
rsync_local_push_samsung:
	rsync $(RSYNC_LOCAL_SOURCE)/meta/ $(RSYNC_LOCAL_TARGET)/meta/ $(RSYNC_ARGS) --delete-after
	rsync $(RSYNC_LOCAL_SOURCE)/processed/ $(RSYNC_LOCAL_TARGET)/processed/ $(RSYNC_ARGS) --delete-after

#hash_match:
#	website/env/bin/python3 website/karakara/scripts/hash_matcher.py --source_folder ~/temp/Convention\ Karaoke/ --destination_folder ~/Applications/KaraKara/files/ -v

move_mouse:
	# Problems with screensaver. Move mouse every 5min
	while true ; do echo 'loopity'; sleep 300; xte 'mousemove 1024 100' -x :0; sleep 300; xte 'mousemove 1024 760' -x :0; done


PROJECTS = processmedia2 website player mediaserver admindashboard

.PHONY: install
install:
	for project in $(PROJECTS); do \
		$(MAKE) install --no-keep-going --directory $$project ; \
	done

.PHONY: test
test:
	for project in $(PROJECTS); do \
		$(MAKE) test --no-keep-going --directory $$project ; \
	done

.PHONY: cloc
cloc:
	cloc --exclude-dir=$(ENV),libs ./


# Clean ------------------------------------------------------------------------
.PHONY: clean
clean:
	rm -rf .cache .vagrant
	for project in $(PROJECTS); do \
		$(MAKE) clean --directory $$project ; \
	done

