OS = $(shell uname -s)
LINUX_DISTRO=$(shell lsb_release -a 2> /dev/null | grep "Distributor ID:" | sed 's|.*:.\(.*\)|\1|')

DEPENDENCIES_PYTHON=dependencies.python.txt
DEPENDENCIES_APT=dependencies.apt.txt
DEPENDENCIES_BREW=dependencies.brew.txt

ENV=_env
PYTHON=$(ENV)/bin/python3
PIP=$(ENV)/bin/pip3
PYTEST=$(ENV)/bin/py.test

WEB_PATH=../website
WEB_WORKING=$(WEB_PATH)/karakara
WEB_PYTHON=$(WEB_PATH)/$(PYTHON)
WEB_PYTEST=$(WEB_PATH)/$(PYTEST)

.PHONY: help
help:
	# Usage: make <target>, where target is
	# install        -- Install os dependencys and setup python virtualenv
	# run            -- Alias for 'scan + encode + import'
	#
	# scan           -- Scan source media folder + create metadata cache
	# encode         -- Perform video encoding on required items
	# import         -- Import processed media into website db
	# cleanup        -- Remove unassociated processed files
	#
	# upgrade        -- Upgrade os + python dependencys
	# test           -- Run integration tests
	# migrate        -- Migrate legacy media structure from processmedia1
	# clean          -- Reset to clean checkout

# Installation -----------------------------------------------------------------
.PHONY: install
install: install_$(OS) $(ENV) libs config.json

# OSX installation ----
.PHONY: has-brew install_Darwin upgrade_Darwin
has-brew:
	# Fails if homebrew is not installed
	which brew
install_Darwin: has-brew
	brew update
	cat $(DEPENDENCIES_BREW) |xargs  brew install 
upgrade_Darwin: has-brew
	cat $(DEPENDENCIES_BREW) |xargs  brew upgrade

# Linux installation ----
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
	# TODO: install newer apt versions

# Python/Virtualenv ----
.PHONY: has-python3
has-python3:
	# Fail if python3 is not installed
	which python3
	# Fail if virtualenv is not installed
	which virtualenv
$(ENV): has-python3
	virtualenv --no-site-packages -p python3 $(ENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r $(DEPENDENCIES_PYTHON)
.PHONY: upgrade
upgrade: upgrade_$(OS)
	$(PIP) install -r $(DEPENDENCIES_PYTHON) --upgrade


libs:
	mkdir libs
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

# Run --------------------------------------------------------------------------
.PHONY: scan encode import cleanup run

scan:
	$(PYTHON) scan_media.py

encode:
	$(PYTHON) encode_media.py --process_order_function random

import:
	PYTHONPATH="$(WEB_WORKING)" $(WEB_PYTHON) import_media.py --config_uri $(WEB_PATH)/development.ini

cleanup:
	$(PYTHON) cleanup_media.py

run: scan encode import


# Migrate --

.PHONY: migrate
migrate:
	$(PYTHON) migrate_media.py --log_level 1 --path_source ~/Applications/KaraKara/files --path_destination ~/Applications/KaraKara/migrate --move_func move



# Test -------------------------------------------------------------------------
.PHONY: test cloc

test:
	$(MAKE) all --directory tests/source
	PYTHONPATH=./ $(PYTEST) processmedia_libs libs tests --doctest-modules --pdb --ignore=tests/test_import.py
	# --maxfail=3
	$(MAKE) ini --directory $(WEB_PATH)
	PYTHONPATH="$(WEB_WORKING):./:$(ENV)/lib/python3.5/site-packages/" $(WEB_PYTEST) tests/test_import.py --pdb

cloc:
	cloc --exclude-dir=$(ENV),libs ./

# Clean ------------------------------------------------------------------------
.PHONY: clean

clean:
	rm -rf .cache __pycache__ $(ENV) libs
	$(MAKE) clean --directory tests/source
	rf -rf config.json
