OS = $(shell uname -s)

PROJECT=karakara
PYTHON_VERSION:=3.6

CONFIG_SOURCE_PATH=config

WRITE_PATH=data
CONFIG_PATH=$(WRITE_PATH)/config
LOG_PATH=$(WRITE_PATH)/logs
EXTERNAL_PATH=$(WRITE_PATH)/externals
UPLOAD_PATH=$(WRITE_PATH)/upload
LOCALE_PATH=$(WRITE_PATH)/locale
DATABASE_PATH=$(WRITE_PATH)/database
DEPENDENCY_FETCHER=$(EXTERNAL_PATH)/dependency_fetcher.py
ENV=$(WRITE_PATH)/_env
PYTHONPATH_ENV=PYTHONPATH="./:$(WRITE_PATH)" $(ENV)
PYTHON=$(PYTHONPATH_ENV)/bin/python$(PYTHON_VERSION)
PIP=$(ENV)/bin/pip$(PYTHON_VERSION)
PSERVE=$(PYTHONPATH_ENV)/bin/pserve
PSHELL=$(PYTHONPATH_ENV)/bin/pshell
PYTEST=$(PYTHONPATH_ENV)/bin/py.test

INI_DEV  = $(CONFIG_PATH)/development.ini
INI_TEST = $(CONFIG_PATH)/test.ini
INI_PROD = $(CONFIG_PATH)/production.ini
STATIC_FILE_PATH = ../mediaserver/www/files

# this must match development.ini path
DATABASE_DEV=$(DATABASE_PATH)/test.db

PATH_LOCAL_LIBS:=../../libs/python3
PATH_REMOTE_LIBS:=https://raw.githubusercontent.com/calaldees/libs/master/python3

LOG_LINES=5

BADGENAME_SOURCE=minami

#APTGET_EXTRAS = 
#TTY=$(shell tty)
#ifndef TTY
#APTGET_EXTRAS+=-y
#endif


# Help -------------------------------------------------------------------------

.PHONY: help
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

.PRECIOUS: $(ENV)
$(ENV):
	pip install virtualenv
	# Reference - http://docs.pylonsproject.org/projects/pyramid/en/1.5-branch/narr/install.html
	virtualenv --no-site-packages -p python$(PYTHON_VERSION) $(ENV)
	$(ENV)/bin/easy_install pyramid

# Experiments
#env/bin/node: env
#	env/bin/pip install nodeenv
#	source env/bin/activate && nodeenv --python-virtualenv --prebuilt
#env/lib/node_modules/bower: env/bin/node
#	source env/bin/activate && npm install -g bower

.PRECIOUS: KaraKara.egg-info/PKG-INFO
KaraKara.egg-info/PKG-INFO: $(ENV)
	$(PYTHON) setup.py develop

# Force reexecution of setup.py dependenys (this must be done from the Makefile or make gets confused and repetedy runs the task)
#setup: KaraKara.egg-info
#	$(PYTHON) setup.py develop

$(EXTERNAL_PATH):
	mkdir -p $(EXTERNAL_PATH) && touch $(EXTERNAL_PATH)/__init__.py

.PRECIOUS: $(DEPENDENCY_FETCHER)
$(DEPENDENCY_FETCHER): $(EXTERNAL_PATH)
	# LinkLocal or Download depenncy_fetcher manager for getting external dependencys
	if [ ! -e $@ ] ; then \
		DEPENDENCY_FETCHER_FILE="apps/dependency_fetcher.py" ; \
		PATH_DEPENDENCY_FETCHER="$(PATH_LOCAL_LIBS)/$$DEPENDENCY_FETCHER_FILE" ; \
		if [ -e $$PATH_DEPENDENCY_FETCHER ] ; then \
			ln -s ../../$$PATH_DEPENDENCY_FETCHER $@ ; \
		else \
			curl $(PATH_REMOTE_LIBS)/$$DEPENDENCY_FETCHER_FILE --compressed -o $@ ; \
		fi ;\
	fi

.PHONY: dependency_download
dependency_download: $(EXTERNAL_PATH)/dependency_fetcher.py
	# Trigger dependency check on every startup
	$(PYTHON) $(DEPENDENCY_FETCHER) dependency_fetcher.json --tracker $(EXTERNAL_PATH) --destination_path $(EXTERNAL_PATH)

.PHONY: install
install: $(INI_DEV) $(LOG_PATH) $(CONFIG_PATH)/search_config.json $(CONFIG_PATH)/production.inidiff KaraKara.egg-info/PKG-INFO dependency_download $(LOCALE_PATH)/karakara.pot $(DATABASE_DEV) upload_paths


# Databases --------------------------------------------------------------------

$(DATABASE_DEV):
	mkdir -p $(DATABASE_PATH)
	$(PYTHON) -m$(PROJECT).model.setup --config_uri $(INI_DEV) --init_func $(PROJECT).model.init_data:init_data
	#env/bin/populate_KaraKara $(INI_DEV)

.PHONY: init_db_production
init_db_production: ini
	$(PYTHON) -m$(PROJECT).model.setup --config_uri $(INI_PROD) --init_func $(PROJECT).model.init_data:init_data
#init_db_test: init_db
#	env/bin/python -m$(PROJECT).model.setup --config_uri development.ini --init_func $(PROJECT).tests.init_data:init_random_data


# Ini files --------------------------------------------------------------------
$(LOG_PATH):
	mkdir -p $@
$(CONFIG_PATH):
	mkdir -p $@
$(INI_DEV): $(CONFIG_PATH)
	cp $(CONFIG_SOURCE_PATH)/development.ini.dist $@
$(CONFIG_PATH)/test.inidiff:
	cp $(CONFIG_SOURCE_PATH)/test.inidiff.dist $@
$(CONFIG_PATH)/production.inidiff:
	cp $(CONFIG_SOURCE_PATH)/production.inidiff.dist $@
.PHONY: ini ini_test ini_production
ini: clean_ini ini_test ini_production
ini_test: $(INI_DEV) $(CONFIG_PATH)/test.inidiff $(CONFIG_PATH)/production.inidiff
	$(PYTHON) $(EXTERNAL_PATH)/lib/make_ini.py $(INI_DEV) $(CONFIG_PATH)/test.inidiff $(INI_TEST)
ini_production: $(INI_DEV) $(CONFIG_PATH)/production.inidiff
	$(PYTHON) $(EXTERNAL_PATH)/lib/make_ini.py $(INI_DEV) $(CONFIG_PATH)/production.inidiff $(INI_PROD)

$(CONFIG_PATH)/search_config.json:
	cp config/search_config.json.dist $@

# Upload paths -----------------------------------------------------------------

.PHONY: upload_paths
upload_paths: $(WRITE_PATH) $(UPLOAD_PATH) $(WRITE_PATH)/uploaded
$(UPLOAD_PATH): $(WRITE_PATH)
	mkdir -p $@
$(WRITE_PATH)/uploaded:
	mkdir -p $@

# Run --------------------------------------------------------------------------
.PHONY: run run_production run_socket_server shell shell_production

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
.PHONY: start_webapp_daemon stop_webapp_daemon

start_webapp_daemon: ini
	start-stop-daemon --start --pidfile webapp.pid --name $(PROJECT) --make-pidfile --background --exec /bin/bash -- -c "$(CURDIR)/env/bin/pserve $(CURDIR)/production.ini"
stop_webapp_daemon:
	start-stop-daemon --stop  --pidfile webapp.pid && rm webapp.pid


# Test -------------------------------------------------------------------------
.PHONY: test test_crawl

test: ini
	$(PYTEST) $(PROJECT) --ini_file=$(INI_TEST) -x --pdb -k test_tracks
	# --capture=sys

test_crawl: ini
	$(PYTEST) $(PROJECT) --runslow -k crawl -s

test_crawl_production: ini
	echo "unimplemented ... yet"
	#env/bin/py.test $(PROJECT) --runslow -k crawl_production -s

# I18N -------------------------------------------------------------------------

$(LOCALE_PATH)/en/LC_MESSAGES/karakara.po:
	mkdir -p $$(dirname "$@")
	ln -s ../../../../locale/en/LC_MESSAGES/karakara.po $@

.PRECIOUS: $(LOCALE_PATH)/karakara.pot
$(LOCALE_PATH)/karakara.pot: $(LOCALE_PATH)/en/LC_MESSAGES/karakara.po
	$(PYTHON) setup.py extract_messages
	$(PYTHON) setup.py update_catalog
	$(PYTHON) setup.py compile_catalog

.PHONY: i18n
i18n:
	$(PYTHON) setup.py extract_messages
	$(PYTHON) setup.py update_catalog
	$(PYTHON) setup.py compile_catalog

# Data -------------------------------------------------------------------------
.PHONY: insert_random_tracks insert_band_tracks

insert_random_tracks:
	$(PYTHON) -m$(PROJECT).scripts.insert_random_tracks 800 --config=$(INI_DEV)

insert_band_tracks:
	$(PYTHON) -m$(PROJECT).scripts.insert_band_tracks --config=$(INI_DEV)

$(WRITE_PATH)/badgenames.txt:
	#$(PYTHON) -mkarakara.scripts.badge_name_importer --source $(BADGENAME_SOURCE) --cache_filename $@.cache > $@
	$(PYTHON) -mkarakara.scripts.badge_name_importer_minami_api > $@

# Logs -------------------------------------------------------------------------

.PHONY: log_production
log_production:
	tail -n$(LOG_LINES) $(LOG_PATH)/production.log
	tail -n$(LOG_LINES) ../mediaserver/log/access.log
	tail -n$(LOG_LINES) ../mediaserver/log/error.log


# Cleanup ----------------------------------------------------------------------
.PHONY: clean_ini
clean_ini:
	rm -f $(INI_DEV)
	rm -f $(INI_TEST)
	rm -f $(INI_PROD)

.PHONY: clean_cache
clean_cache:
	find . -iname *.pyc -delete
	find . -iname __pycache__ -delete
	find . -iname .cache -delete

.PHONY: clean
clean: clean_cache
	rm -rf $(WRITE_PATH)/*
	rm -rf *.egg-info/*
