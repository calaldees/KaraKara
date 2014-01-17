PROJECT=karakara

PATH_EXTERNALS=externals/

INI_DEV  = development.ini
INI_TEST = test.ini
INI_PROD = production.ini
STATIC_FILE_PATH = ../mediaserver/www/files

#APTGET_EXTRAS = 
#TTY=$(shell tty)
#ifndef TTY
#APTGET_EXTRAS+=-y
#endif


help:
	# Usage: make <target>, where target is
	# setup          -- setup python egg & install dependencys/env if needed
	# test           -- run all nosetests
	# init_db        -- create a blank database
	# init_db_test   -- create test db
	# run            -- run the site in development mode
	# run_production -- run in production mode
	# clean          -- reset the folder to clean git checkout (removes virtual python env)
	# import_tracks_local_filesystem  -- crawl all mediaserver to import tracks data into local Db
	# import_tracks_local_mediaserver -- crawl http server for to import
	# insert_random_tracks            -- insert random named tracks for dev/testing
	#
	# Typical first use should be: setup, init_db, import_tracks_local_filesystem, run

env_activate:
	source env/bin/activate
env_deactivate:
	deactivate

env:
	if dpkg -s python-virtualenv ; then \
		echo virtualenv already installed; \
	else \
		echo installing virtualenv; \
		sudo apt-get install python-virtualenv -y ; \
	fi
	if dpkg -s python3-setuptools ; then \
		echo python 3 already installed; \
	else \
		echo installing python 3; \
		sudo apt-get install python3-setuptools -y ; \
	fi
	# Reference - http://docs.pylonsproject.org/projects/pyramid/en/1.3-branch/narr/install.html
	virtualenv --no-site-packages -p python3 env
	env/bin/easy_install pyramid

setup: env
	env/bin/python setup.py develop

dependency_downloader.py:
	curl https://raw.github.com/calaldees/libs/master/python3/lib/dependency_downloader.py --compressed -O

externals:
	env/bin/python $(PROJECT)/scripts/dependency_downloader.py --destination $(PATH_EXTERNALS)

test.db:
	env/bin/python -m$(PROJECT).model.setup --config_uri $(INI_DEV) --init_func $(PROJECT).model.init_data:init_data
	#env/bin/populate_KaraKara development.ini

install: env setup dependency_downloader.py externals test.db test

#init_db_test: init_db
#	env/bin/python -m$(PROJECT).model.setup --config_uri development.ini --init_func $(PROJECT).tests.init_data:init_random_data

run: externals
	#$(MAKE) env_activate
	env/bin/pserve --reload $(INI_DEV)
	#$(MAKE) env_deactivate

run_production: ini_production
	env/bin/pserve $(INI_PROD)

run_socket_server:
	env/bin/python3 -m$(PROJECT).lib.socket_server

shell:
	env/bin/pshell $(INI_DEV)

clean:
	rm -rf env
	rm -rf data
	rm -rf *.egg-info
	rm -f *.db
	rm -f $(INI_TEST)
	rm -f $(INI_PROD)
	rm -rf $(PATH_EXTERNALS)
	rm -rf dependencys_installed.json

insert_random_tracks:
	env/bin/python -m$(PROJECT).scripts.insert_random_tracks 800 --config=$(INI_DEV)

import_tracks_dev: init_db
	env/bin/python -m$(PROJECT).scripts.import_tracks '$(STATIC_FILE_PATH)' --config=$(INI_DEV)

import_tracks_production: ini_production
	env/bin/python -m$(PROJECT).model.setup --config_uri $(INI_PROD) --init_func $(PROJECT).model.init_data:init_data
	env/bin/python -m$(PROJECT).scripts.import_tracks '$(STATIC_FILE_PATH)' --config=$(INI_PROD)

#import_tracks_local_mediaserver: init_db
#	env/bin/python -mkarakara.scripts.import_tracks 'http://localhost/files' --config=development.ini

#import_tracks_test: init_db
#	env/bin/python -mkarakara.scripts.import_tracks 'http://calaldees.dreamhosters.com/test/' --config=development.ini

test: ini_test
	env/bin/py.test $(PROJECT) -q --pdb
	#--pdb --capture=sys

test_crawl: ini_test
	env/bin/py.test $(PROJECT) --runslow -k crawl -s

ini_test:
	env/bin/python3 $(PROJECT)/scripts/make_ini.py test
ini_production:
	env/bin/python3 $(PROJECT)/scripts/make_ini.py production

start_webapp_daemon: ini_production
	start-stop-daemon --start --pidfile webapp.pid --name $(PROJECT) --make-pidfile --background --exec /bin/bash -- -c "$(CURDIR)/env/bin/pserve $(CURDIR)/production.ini"
stop_webapp_daemon:
	start-stop-daemon --stop  --pidfile webapp.pid && rm webapp.pid
