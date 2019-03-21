.PHONY: help
help:
	# Usage: make <target>, where target is
	# install        -- just install python virtualenv
	# install_os     -- Install os dependencies and setup python virtualenv
	# run            -- Alias for 'install + scan + encode + import_media'
	#
	# scan           -- Scan source media folder + create metadata cache
	# encode         -- Perform video encoding on required items
	# import_media   -- Import processed media into currently active website
	# cleanup        -- Remove unassociated processed files
	#
	# upgrade        -- Upgrade os + python dependencys
	# test           -- Run integration tests
	# clean          -- Reset to clean checkout


# Variables --------------------------------------------------------------------

OS:=$(shell uname -s)
LINUX_DISTRO:=$(shell lsb_release -a 2> /dev/null | grep "Distributor ID:" | sed 's|.*:.\(.*\)|\1|')

PYTHON_VERSION:=3.7
DEPENDENCIES_PYTHON:=docker/processmedia2.pip
DEPENDENCIES_APT:=dependencies.apt.txt
DEPENDENCIES_BREW:=dependencies.brew.txt

WRITE_PATH=data

CONFIG_PATH=$(WRITE_PATH)/config
LOG_PATH=$(WRITE_PATH)/logs
ENV=$(WRITE_PATH)/_env
PYTHONPATH_ENV=PYTHONPATH="./:$(WRITE_PATH)" $(ENV)
PYTHON=$(PYTHONPATH_ENV)/bin/python$(PYTHON_VERSION)
PIP=$(ENV)/bin/pip$(PYTHON_VERSION)
PYTEST=$(PYTHONPATH_ENV)/bin/py.test



# Installation -----------------------------------------------------------------
.PHONY: install install_os
install_os: install_$(OS) install
install: $(ENV) config.json logging.json logs

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
.PRECIOUS: $(ENV)
$(ENV):
	virtualenv --no-site-packages -p python$(PYTHON_VERSION) $(ENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r $(DEPENDENCIES_PYTHON)
.PHONY: upgrade
upgrade:
	$(PIP) install -r $(DEPENDENCIES_PYTHON) --upgrade


# Config -----------------------------------------------------------------------

config.json:
	cp config.json.dist config.json

logging.json:
	cp logging.json.dist logging.json

logs:
	mkdir -p logs


# Run --------------------------------------------------------------------------
.PHONY: scan encode import_media cleanup run

scan:
	$(PYTHON) scan_media.py
encode:
	$(PYTHON) encode_media.py --process_order_function random
import_media:
	$(PYTHON) import_media.py --force
cleanup:
	$(PYTHON) cleanup_media.py
run: install_env scan encode import_media

# temp addition to document event import step
import_media_production_api:
	$(PYTHON) import_media.py --force --api_host int.karakara.org.uk

# Test -------------------------------------------------------------------------
.PHONY: test
test:
	#$(MAKE) all --directory tests/source
	$(PYTEST) processmedia_libs tests --doctest-modules

.PHONY: cloc
cloc:
	cloc --exclude-dir=$(ENV) ./

# Clean ------------------------------------------------------------------------

.PHONY: clean
clean:
	rm -rf .cache .pytest_cache __pycache__ $(ENV) config.json logging.json logs mtimes.json
	#$(MAKE) clean --directory tests/source
