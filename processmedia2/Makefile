OS = $(shell uname -s)
LINUX_DISTRO=$(shell lsb_release -a 2> /dev/null | grep "Distributor ID:" | sed 's|.*:.\(.*\)|\1|')

.PHONY: help
help:
	# Help

# Installation -----------------------------------------------------------------
.PHONY: install
install: $(OS) env

# OSX installation
.PHONY: Darwin has-brew
has-brew:
	# Fails if homebrew is not installed
	which brew
Darwin: has-brew
	brew install python3

# Linux installation
.PHONY: Linux Debian Ubuntu apt-installation
Linux: $(LINUX_DISTRO)
Debian: apt-installation
Ubuntu: apt-installation
apt-installation:
	sudo apt-get install -y python3 python3-dev python3-pip


.PHONY: has-python3
has-python3:
	# Fail if python3 is not installed
	which python3
	# Fail if virtualenv is not installed
	which virtualenv
env: has-python3
	virtualenv --no-site-packages -p python3 env

# Run --------------------------------------------------------------------------
.PHONY: run run_production

run:

run_production:

# Test -------------------------------------------------------------------------
.PHONY: test

test:

# Clean ------------------------------------------------------------------------
.PHONY: clean

clean:
	rm -rf env
