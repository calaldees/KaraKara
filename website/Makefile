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
	brew install python3 gettext
	# cd ~/bin/ && ln -s /usr/local/opt/gettext/bin/msgmerge
	# python virtualenv?
	touch .installed_python_Darwin

# Linux installation
.installed_python_Linux:
	if dpkg -s python-virtualenv ; then \
		echo virtualenv already installed; \
	else \
		echo installing virtualenv; \
		sudo apt-get install -y python-virtualenv curl gettext; \
	fi
	if dpkg -s python3-setuptools ; then \
		echo python 3 already installed; \
	else \
		echo installing python 3; \
		sudo apt-get install -y python3-setuptools python3-dev curl gettext; \
	fi
	touch .installed_python_Linux

env: .installed_python
	# Reference - http://docs.pylonsproject.org/projects/pyramid/en/1.5-branch/narr/install.html
	virtualenv --no-site-packages -p python3 env
	env/bin/easy_install pyramid

# Experiments
#env/bin/node: env
#	env/bin/pip install nodeenv
#	source env/bin/activate && nodeenv --python-virtualenv --prebuilt
#env/lib/node_modules/bower: env/bin/node
#	source env/bin/activate && npm install -g bower

KaraKara.egg-info: env
	env/bin/python setup.py develop

dependency_downloader.py:
	curl https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/dependency_downloader.py --compressed -O

externals:
	mkdir externals && touch externals/__init__.py

dependency_download: dependency_downloader.py externals
	# Trigger dependency check on every startup
	env/bin/python dependency_downloader.py --destination externals
	#source env/bin/activate && bower install --config.interactive=false --config.directory=./externals/

install: development.ini production.inidiff KaraKara.egg-info dependency_download test.db upload_paths i18n


# Databases --------------------------------------------------------------------

test.db:
	env/bin/python -m$(PROJECT).model.setup --config_uri $(INI_DEV) --init_func $(PROJECT).model.init_data:init_data
	#env/bin/populate_KaraKara development.ini

init_db_production: ini
	env/bin/python -m$(PROJECT).model.setup --config_uri $(INI_PROD) --init_func $(PROJECT).model.init_data:init_data
#init_db_test: init_db
#	env/bin/python -m$(PROJECT).model.setup --config_uri development.ini --init_func $(PROJECT).tests.init_data:init_random_data


# Ini files --------------------------------------------------------------------

development.ini:
	cp development.ini.dist development.ini

production.inidiff:
	cp production.inidiff.dist production.inidiff

ini: clean_ini ini_test ini_production
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

run: install
	env/bin/pserve --reload $(INI_DEV)

run_production: ini
	env/bin/pserve $(INI_PROD)

run_socket_server:
	env/bin/python3 -mexternals.lib.socket.multisocket_server

shell:
	env/bin/pshell $(INI_DEV)

shell_production: ini
	env/bin/pshell $(INI_PROD)

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
	env/bin/py.test externals --pdb
	env/bin/py.test $(PROJECT) --pdb
	#--pdb --capture=sys

test_crawl: ini
	env/bin/py.test $(PROJECT) --runslow -k crawl -s

test_crawl_production: ini
	echo "unimplemented ... yet"
	#env/bin/py.test $(PROJECT) --runslow -k crawl_production -s

# I18N -------------------------------------------------------------------------

locale:
	env/bin/python3 setup.py extract_messages
	env/bin/python3 setup.py init_catalog -l en
	#env/bin/python3 setup.py init_catalog -l fr
	#env/bin/python3 setup.py init_catalog -l es
	#env/bin/python3 setup.py init_catalog -l it
	#env/bin/pip3 install git+git://github.com/mitsuhiko/babel.git
	

env/lib/python3.4/site-packages/babel/messages/frontend.py.bak: env
	# bable is shit and needs tweaking
	# bable is throwing a bytes/str fit in python3
	#  https://github.com/mitsuhiko/babel/issues/91
	# they have updated github/bable/master but not the pip package.
	# This just perform a ultra hack critical fix on bable
	sed -i.bak "s/tmpname, 'w'/tmpname, 'wb'/g" env/lib/python3.4/site-packages/babel/messages/frontend.py

i18n: locale env/lib/python3.4/site-packages/babel/messages/frontend.py.bak
	env/bin/python3 setup.py extract_messages
	env/bin/python3 setup.py update_catalog
	#Looks like msgmerge from the gettext lib works can work in place of update_catalog.
	#cd karakara/locale && msgmerge --update en/LC_MESSAGES/KaraKara.po KaraKara.pot
	env/bin/python3 setup.py compile_catalog

# Data -------------------------------------------------------------------------

insert_random_tracks:
	env/bin/python -m$(PROJECT).scripts.insert_random_tracks 800 --config=$(INI_DEV)

import_tracks_dev: test.db
	env/bin/python -m$(PROJECT).scripts.import_tracks '$(STATIC_FILE_PATH)' --config=$(INI_DEV)

import_tracks_production: ini  #init_db_production
	env/bin/python -m$(PROJECT).scripts.import_tracks '$(STATIC_FILE_PATH)' --config=$(INI_PROD)


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
	rm -rf env
	rm -rf data
	rm -rf *.egg-info
	rm -f *.db
	rm -f *.log
	rm -rf externals
	rm -rf dependency_downloader.py
	rm -rf dependencys_installed.json
	rm -rf .installed_*
