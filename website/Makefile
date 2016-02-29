OS = $(shell uname -s)

ENV=_env
PYTHON=$(ENV)/bin/python3
PIP=$(ENV)/bin/pip3
PSERVE=$(ENV)/bin/pserve
PSHELL=$(ENV)/bin/pshell
PYTEST=$(ENV)/bin/py.test

PROJECT=karakara

INI_DEV  = development.ini
INI_TEST = test.ini
INI_PROD = production.ini
STATIC_FILE_PATH = ../mediaserver/www/files

LOG_LINES=5

BADGENAME_SOURCE=minami

#APTGET_EXTRAS = 
#TTY=$(shell tty)
#ifndef TTY
#APTGET_EXTRAS+=-y
#endif

help:
	# Usage: make <target>, where target is
	# install        -- 
	# test           -- run all nosetests
	# run            -- run the site in development mode
	# run_production -- run in production mode
	# clean          -- reset the folder to clean git checkout (removes virtual python env)
	# import_tracks_local_filesystem  -- crawl all mediaserver to import tracks data into local Db
	# import_tracks_local_mediaserver -- crawl http server for to import
	# insert_random_tracks            -- insert random named tracks for dev/testing
	#
	# Typical first use should be: setup, init_db, import_tracks_local_filesystem, run
	# Dpendencies - make python3-setuptools python3-dev python-virtualenv curl


# Installation -----------------------------------------------------------------

#python-virtualenv python3-setuptools python3-dev curl

$(ENV):
	# Reference - http://docs.pylonsproject.org/projects/pyramid/en/1.5-branch/narr/install.html
	virtualenv --no-site-packages -p python3 $(ENV)
	$(ENV)/bin/easy_install pyramid

# Experiments
#env/bin/node: env
#	env/bin/pip install nodeenv
#	source env/bin/activate && nodeenv --python-virtualenv --prebuilt
#env/lib/node_modules/bower: env/bin/node
#	source env/bin/activate && npm install -g bower

KaraKara.egg-info: $(ENV)
	$(PYTHON) setup.py develop

# Force reexecution of setup.py dependenys (this must be done from the Makefile or make gets confused and repetedy runs the task)
setup: KaraKara.egg-info
	$(PYTHON) setup.py develop

dependency_downloader.py:
	curl https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/dependency_downloader.py --compressed -O

externals:
	mkdir externals && touch externals/__init__.py

PHONY: dependency_download
dependency_download: dependency_downloader.py externals
	# Trigger dependency check on every startup
	$(PYTHON) dependency_downloader.py --destination externals
	#source env/bin/activate && bower install --config.interactive=false --config.directory=./externals/

install: development.ini production.inidiff KaraKara.egg-info dependency_download test.db upload_paths locale/karakara.pot


# Databases --------------------------------------------------------------------

test.db:
	$(PYTHON) -m$(PROJECT).model.setup --config_uri $(INI_DEV) --init_func $(PROJECT).model.init_data:init_data
	#env/bin/populate_KaraKara development.ini

init_db_production: ini
	$(PYTHON) -m$(PROJECT).model.setup --config_uri $(INI_PROD) --init_func $(PROJECT).model.init_data:init_data
#init_db_test: init_db
#	env/bin/python -m$(PROJECT).model.setup --config_uri development.ini --init_func $(PROJECT).tests.init_data:init_random_data


# Ini files --------------------------------------------------------------------

development.ini:
	cp development.ini.dist development.ini

production.inidiff:
	cp production.inidiff.dist production.inidiff

ini: clean_ini ini_test ini_production
ini_test: development.ini
	$(PYTHON) externals/lib/make_ini.py test
ini_production: production.inidiff
	$(PYTHON) externals/lib/make_ini.py production

# Upload paths -----------------------------------------------------------------

PHONY: upload_paths
upload_paths: data data/upload data/uploaded
data:
	mkdir data
data/upload:
	mkdir data/upload
data/uploaded:
	mkdir data/uploaded

# Run --------------------------------------------------------------------------

run: install
	$(PSERVE) --reload $(INI_DEV)

run_production: ini
	$(PSERVE) $(INI_PROD)

run_socket_server:
	$(PYTHON) -mexternals.lib.socket.multisocket_server

shell:
	$(PSHELL) $(INI_DEV)

shell_production: ini
	$(PSHELL) $(INI_PROD)

# Daemon -----------------------------------------------------------------------

start_webapp_daemon: ini
	start-stop-daemon --start --pidfile webapp.pid --name $(PROJECT) --make-pidfile --background --exec /bin/bash -- -c "$(CURDIR)/env/bin/pserve $(CURDIR)/production.ini"
stop_webapp_daemon:
	start-stop-daemon --stop  --pidfile webapp.pid && rm webapp.pid


# Test -------------------------------------------------------------------------

#import_tracks_local_mediaserver: init_db
#	env/bin/python -mkarakara.scripts.import_tracks 'http://localhost/files' --config=development.ini

#import_tracks_test: init_db
#	env/bin/python -mkarakara.scripts.import_tracks 'http://calaldees.dreamhosters.com/test/' --config=development.ini

test: ini
	$(PYTEST) externals --pdb
	$(PYTEST) $(PROJECT) --pdb
	#--pdb --capture=sys

test_crawl: ini
	$(PYTEST) $(PROJECT) --runslow -k crawl -s

test_crawl_production: ini
	echo "unimplemented ... yet"
	#env/bin/py.test $(PROJECT) --runslow -k crawl_production -s

# I18N -------------------------------------------------------------------------

locale:
	$(PYTHON) setup.py extract_messages
	$(PYTHON) setup.py init_catalog -l en
	#env/bin/python3 setup.py init_catalog -l fr
	#env/bin/python3 setup.py init_catalog -l es
	#env/bin/python3 setup.py init_catalog -l it
	#env/bin/pip3 install git+git://github.com/mitsuhiko/babel.git

env/lib/python3.4/site-packages/Babel-1.3-py3.4.egg/babel/messages/frontend.py.bak: KaraKara.egg-info
	# bable is shit and needs tweaking
	# bable is throwing a bytes/str fit in python3
	#  https://github.com/mitsuhiko/babel/issues/91
	# they have updated github/bable/master but not the pip package.
	# This just perform a ultra hack critical fix on bable
	sed -i.bak "s/tmpname, 'w'/tmpname, 'wb'/g" env/lib/python3.4/site-packages/Babel-1.3-py3.4.egg/babel/messages/frontend.py

locale/karakara.pot: locale
    # removed dependecy - env/lib/python3.4/site-packages/Babel-1.3-py3.4.egg/babel/messages/frontend.py.bak
	$(PYTHON) setup.py extract_messages
	$(PYTHON) setup.py update_catalog
	$(PYTHON) setup.py compile_catalog

i18n:
	$(PYTHON) setup.py extract_messages
	$(PYTHON) setup.py update_catalog
	#Looks like msgmerge from the gettext lib works can work in place of update_catalog.
	#cd karakara/locale && msgmerge --update en/LC_MESSAGES/KaraKara.po KaraKara.pot
	$(PYTHON) setup.py compile_catalog

# Data -------------------------------------------------------------------------

insert_random_tracks:
	$(PYTHON) -m$(PROJECT).scripts.insert_random_tracks 800 --config=$(INI_DEV)

insert_band_tracks:
	$(PYTHON) -m$(PROJECT).scripts.insert_band_tracks --config=$(INI_DEV)

import_tracks_dev: test.db
	$(PYTHON) -m$(PROJECT).scripts.import_tracks '$(STATIC_FILE_PATH)' --config=$(INI_DEV)

import_tracks_production: ini  #init_db_production
	$(PYTHON) -m$(PROJECT).scripts.import_tracks '$(STATIC_FILE_PATH)' --config=$(INI_PROD)

badgenames.txt:
	$(PYTHON) -mkarakara.scripts.badge_name_importer --source $(BADGENAME_SOURCE) > badgenames.txt

# Logs -------------------------------------------------------------------------

log_production:
	tail -n$(LOG_LINES) production.log
	tail -n$(LOG_LINES) ../mediaserver/log/access.log
	tail -n$(LOG_LINES) ../mediaserver/log/error.log


# Cleanup ----------------------------------------------------------------------

clean_ini:
	rm -f $(INI_DEV)
	rm -f $(INI_TEST)
	rm -f $(INI_PROD)

clean: clean_ini
	rm -rf $(ENV)
	rm -rf data
	rm -rf *.egg-info
	rm -f *.db
	rm -f *.log
	rm -rf externals
	rm -rf dependency_downloader.py
	rm -rf dependencys_installed.json
	rm -rf .installed_*
	rm -rf badgenames.*
	find ./locale -iname *.mo -delete
	find ./locale -iname *.pot -delete
