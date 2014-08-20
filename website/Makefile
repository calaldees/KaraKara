OS = $(shell uname -s)

PROJECT=karakara

INI_DEV  = development.ini
INI_TEST = test.ini
INI_PROD = production.ini
STATIC_FILE_PATH = ../mediaserver/www/files

LOG_LINES=5

#APTGET_EXTRAS = 
#TTY=$(shell tty)
#ifndef TTY
#APTGET_EXTRAS+=-y
#endif


help:
	# Usage: make <target>, where target is
	# install        -- run after clean checkout to pull dependecys and setup
	# test           -- run all nosetests
	# run            -- run the site in development mode
	# run_production -- run in production mode
	# clean          -- reset the folder to clean git checkout (removes virtual python env)
	# import_tracks_local_filesystem  -- crawl all mediaserver to import tracks data into local Db
	# import_tracks_local_mediaserver -- crawl http server for to import
	# insert_random_tracks            -- insert random named tracks for dev/testing
	#
	# Typical first use should be: setup, init_db, import_tracks_local_filesystem, run


# Installation -----------------------------------------------------------------

.installed_python: .installed_python_$(OS)
	touch .installed_python

# OSX installation
.installed_python_Darwin:
	brew install python3
	# python virtualenv?
	touch .installed_python_Darwin

# Linux installation
.installed_python_Linux:
	if dpkg -s python-virtualenv ; then \
		echo virtualenv already installed; \
	else \
		echo installing virtualenv; \
		sudo apt-get install -y python-virtualenv curl ; \
	fi
	if dpkg -s python3-setuptools ; then \
		echo python 3 already installed; \
	else \
		echo installing python 3; \
		sudo apt-get install -y python3-setuptools python3-dev curl ; \
	fi
	touch .installed_python_Linux

env: .installed_python
	# Reference - http://docs.pylonsproject.org/projects/pyramid/en/1.5-branch/narr/install.html
	virtualenv --no-site-packages -p python3 env
	env/bin/easy_install pyramid

KaraKara.egg-info: env
	env/bin/python setup.py develop

dependency_downloader.py:
	curl https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/dependency_downloader.py --compressed -O

externals:
	mkdir externals && touch externals/__init__.py

dependency_download: dependency_downloader.py externals
	# Trigger dependency check on every startup
	env/bin/python dependency_downloader.py --destination externals

install: development.ini production.inidiff KaraKara.egg-info dependency_download test.db upload_paths


# Databases --------------------------------------------------------------------

test.db:
	env/bin/python -m$(PROJECT).model.setup --config_uri $(INI_DEV) --init_func $(PROJECT).model.init_data:init_data
	#env/bin/populate_KaraKara development.ini

init_db_production: ini_production
	env/bin/python -m$(PROJECT).model.setup --config_uri $(INI_PROD) --init_func $(PROJECT).model.init_data:init_data
#init_db_test: init_db
#	env/bin/python -m$(PROJECT).model.setup --config_uri development.ini --init_func $(PROJECT).tests.init_data:init_random_data


# Ini files --------------------------------------------------------------------

development.ini:
	cp development.ini.dist development.ini

production.inidiff:
	cp production.inidiff.dist production.inidiff

ini_test: development.ini
	env/bin/python3 externals/lib/make_ini.py test
ini_production: production.inidiff
	env/bin/python3 externals/lib/make_ini.py production

# Upload paths -----------------------------------------------------------------

upload_paths: data data/upload data/uploaded
data:
	mkdir data
data/upload:
	mkdir data/upload
data/uploaded:
	mkdir data/uploaded

# Run --------------------------------------------------------------------------

run:
	env/bin/pserve --reload $(INI_DEV)

run_production: ini_production
	env/bin/pserve $(INI_PROD)

run_socket_server:
	env/bin/python3 -mexternals.lib.socket.multisocket_server

shell:
	env/bin/pshell $(INI_DEV)

shell_production: ini_production
	env/bin/pshell $(INI_PROD)

# Daemon -----------------------------------------------------------------------

start_webapp_daemon: ini_production
	start-stop-daemon --start --pidfile webapp.pid --name $(PROJECT) --make-pidfile --background --exec /bin/bash -- -c "$(CURDIR)/env/bin/pserve $(CURDIR)/production.ini"
stop_webapp_daemon:
	start-stop-daemon --stop  --pidfile webapp.pid && rm webapp.pid


# Test -------------------------------------------------------------------------

#import_tracks_local_mediaserver: init_db
#	env/bin/python -mkarakara.scripts.import_tracks 'http://localhost/files' --config=development.ini

#import_tracks_test: init_db
#	env/bin/python -mkarakara.scripts.import_tracks 'http://calaldees.dreamhosters.com/test/' --config=development.ini

test: ini_test
	env/bin/py.test externals -q --pdb
	env/bin/py.test $(PROJECT) -q --pdb
	#--pdb --capture=sys

test_crawl: ini_test
	env/bin/py.test $(PROJECT) --runslow -k crawl -s

test_crawl_production: init_test ini_production
	echo "unimplemented ... yet"
	#env/bin/py.test $(PROJECT) --runslow -k crawl_production -s


# Data -------------------------------------------------------------------------

insert_random_tracks:
	env/bin/python -m$(PROJECT).scripts.insert_random_tracks 800 --config=$(INI_DEV)

import_tracks_dev: test.db
	env/bin/python -m$(PROJECT).scripts.import_tracks '$(STATIC_FILE_PATH)' --config=$(INI_DEV)

import_tracks_production: ini_production  #init_db_production
	env/bin/python -m$(PROJECT).scripts.import_tracks '$(STATIC_FILE_PATH)' --config=$(INI_PROD)


# Logs -------------------------------------------------------------------------

log_production:
	tail -n$(LOG_LINES) production.log
	tail -n$(LOG_LINES) ../mediaserver/log/access.log
	tail -n$(LOG_LINES) ../mediaserver/log/error.log


# Cleanup ----------------------------------------------------------------------

clean:
	rm -rf env
	rm -rf data
	rm -rf *.egg-info
	rm -f *.db
	rm -f *.log
	rm -f $(INI_TEST)
	rm -f $(INI_PROD)
	rm -rf externals
	rm -rf dependency_downloader.py
	rm -rf dependencys_installed.json
	rm -rf .installed_*
