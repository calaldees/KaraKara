.PHONY: help
help:
	# Usage: make <target>, where target is
	# install        -- Install os dependencys and setup python virtualenv
	# install_env    --   just install python virtualenv
	# run            -- Alias for 'scan + encode + import_develop'
	# run_production -- Alias for 'scan + encode + import_production'
	#
	# scan           -- Scan source media folder + create metadata cache
	# encode         -- Perform video encoding on required items
	# import         -- Import processed media into website db
	# cleanup        -- Remove unassociated processed files
	#
	# upgrade        -- Upgrade os + python dependencys
	# test           -- Run integration tests
	# clean          -- Reset to clean checkout


# Variables --------------------------------------------------------------------

OS:=$(shell uname -s)
LINUX_DISTRO:=$(shell lsb_release -a 2> /dev/null | grep "Distributor ID:" | sed 's|.*:.\(.*\)|\1|')

DEPENDENCIES_PYTHON:=dependencies.python.txt
DEPENDENCIES_APT:=dependencies.apt.txt
DEPENDENCIES_BREW:=dependencies.brew.txt

ENV:=_env
PYTHON:=$(ENV)/bin/python3
PIP:=$(ENV)/bin/pip3
PYTEST:=$(ENV)/bin/py.test

WEB_PATH:=../website
WEB_WORKING:=$(WEB_PATH)/karakara
WEB_PYTHON:=$(WEB_PATH)/$(PYTHON)
WEB_PYTEST:=$(WEB_PATH)/$(PYTEST)
WEB_PYTHONPATH:=$(WEB_WORKING):./:$(ENV)/lib/python3.5/site-packages/

# Installation -----------------------------------------------------------------
.PHONY: install install_env
install: install_$(OS) install_env
install_env: $(ENV) libs config.json logging.json logs

# OSX ----
.PHONY: has-brew install_Darwin upgrade_Darwin
has-brew:
	which brew
install_Darwin: has-brew
	brew update
	cat $(DEPENDENCIES_BREW) |xargs  brew install 
upgrade_Darwin: has-brew
	cat $(DEPENDENCIES_BREW) |xargs  brew upgrade

# Linux ----
.PHONY: install_Linux install_Debian install_Ubuntu apt-installation upgrade_Linux upgrade_Debian upgrade_Ubuntu apt-upgrade
install_Linux: install_$(LINUX_DISTRO)
install_Debian: apt-installation
install_Ubuntu: apt-installation
apt-installation:
	cat $(DEPENDENCIES_APT) |xargs  sudo apt-get install -y
upgrade_Linux: upgrade_$(LINUX_DISTRO)
upgrade_Debian: apt-upgrade
upgrade_Ubuntu: apt-upgrade
apt-upgrade:
	sudo apt-get update
	# TODO: install upgraded apt versions

# Python/Virtualenv ----
.PHONY: has-python3
has-python3:
	which python3
	which virtualenv
.PRECIOUS: $(ENV)
$(ENV):
	virtualenv --no-site-packages -p python3 $(ENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r $(DEPENDENCIES_PYTHON)
.PHONY: upgrade
upgrade: upgrade_$(OS)
	$(PIP) install -r $(DEPENDENCIES_PYTHON) --upgrade

# Link local libs ----
libs:
	mkdir -p libs
	touch libs/__init__.py
	cd libs && \
	if [ -d ../../../libs/ ] ; then \
		ln -s ../../../libs/python3/lib/misc.py                            misc.py                  ;\
		ln -s ../../../libs/python3/lib/file.py                            file.py                  ;\
	else \
		wget -cq https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/misc.py        ;\
		wget -cq https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/file.py        ;\
	fi


# Config -----------------------------------------------------------------------

config.json:
	cp config.json.dist config.json

logging.json:
	cp logging.json.dist logging.json

logs:
	mkdir -p logs


# Run --------------------------------------------------------------------------
.PHONY: scan encode import_development import_production cleanup run run_production

scan:
	$(PYTHON) scan_media.py

encode:
	$(PYTHON) encode_media.py --process_order_function random

import_%:
	PYTHONPATH="$(WEB_PYTHONPATH)" $(WEB_PYTHON) import_media.py --config_uri $(WEB_PATH)/$*.ini

cleanup:
	$(PYTHON) cleanup_media.py

run: install_env scan encode import_development
run_production: install_env scan encode import_production


# Test -------------------------------------------------------------------------
.PHONY: test
test:
	$(MAKE) all --directory tests/source
	PYTHONPATH=./ $(PYTEST) processmedia_libs libs tests --doctest-modules --pdb --ignore=tests/test_import.py
	$(MAKE) ini --directory $(WEB_PATH)
	PYTHONPATH="$(WEB_PYTHONPATH)" $(WEB_PYTEST) tests/test_import.py --pdb

.PHONY: cloc
cloc:
	cloc --exclude-dir=$(ENV),libs ./

# Clean ------------------------------------------------------------------------

.PHONY: clean
clean:
	rm -rf .cache __pycache__ $(ENV) libs config.json logging.json logs mtimes.json
	$(MAKE) clean --directory tests/source
