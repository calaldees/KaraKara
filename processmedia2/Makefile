OS = $(shell uname -s)
LINUX_DISTRO=$(shell lsb_release -a 2> /dev/null | grep "Distributor ID:" | sed 's|.*:.\(.*\)|\1|')

ENV=_env
PYTHON=$(ENV)/bin/python3
PIP=$(ENV)/bin/pip3
PYTEST=$(ENV)/bin/py.test


.PHONY: help
help:
	# Help

# Installation -----------------------------------------------------------------
.PHONY: install
install: $(OS) $(ENV) libs

# OSX installation
.PHONY: Darwin has-brew
has-brew:
	# Fails if homebrew is not installed
	which brew
Darwin: has-brew
	brew update
	brew install python3
	brew install mplayer \
		--with-libcaca
	brew install sox \
		--with-flac \
		--with-lame \
		--with-libao \
		--with-libsndfile \
		--with-libvorbis \
		--with-opencore-amr \
		--with-opusfile
	brew install ffmpeg \
		--with-dcadec \
		--with-faac \
		--with-fdk-aac \
		--with-ffplay \
		--with-fontconfig \
		--with-freetype \
		--with-frei0r \
		--with-libass \
		--with-libbluray \
		--with-libbs2b \
		--with-libcaca \
		--with-libquvi \
		--with-libsoxr \
		--with-libssh \
		--with-libvidstab \
		--with-libvorbis \
		--with-libvpx \
		--with-opencore-amr \
		--with-openjpeg \
		--with-openssl \
		--with-opus \
		--with-rtmpdump \
		--with-schroedinger \
		--with-snappy \
		--with-speex \
		--with-theora \
		--with-tools \
		--with-webp \
		--with-x265 \
		--with-zeromq
	brew install libav \
		--with-fdk-aac \
		--with-fontconfig \
		--with-freetype \
		--with-frei0r \
		--with-gnutls \
		--with-libvo-aacenc \
		--with-libvorbis \
		--with-libvpx \
		--with-opencore-amr \
		--with-openjpeg \
		--with-openssl \
		--with-opus \
		--with-rtmpdump \
		--with-schroedinger \
		--with-sdl \
		--with-speex \
		--with-theora


# Linux installation
.PHONY: Linux Debian Ubuntu apt-installation
Linux: $(LINUX_DISTRO)
Debian: apt-installation
Ubuntu: apt-installation
apt-installation:
	sudo apt-get install -y python3 python3-dev python3-pip
	if dpkg -s libav-tools ; then \
		echo libav already installed; \
	else \
		echo installing libav; \
		sudo add-apt-repository ppa:motumedia/libav-daily; \
		sudo apt-get update; \
		sudo apt-get install -y libav-tools libavcodec-extra-53 sox mencoder ; \
	fi


.PHONY: has-python3
has-python3:
	# Fail if python3 is not installed
	which python3
	# Fail if virtualenv is not installed
	which virtualenv
$(ENV):
	virtualenv --no-site-packages -p python3 $(ENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r pip-requirements.txt

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
	

# Run --------------------------------------------------------------------------
.PHONY: scan encode import migrate

scan:
	$(PYTHON) scan_media.py

encode:
	$(PYTHON) encode_media.py

import:
	PYTHONPATH=../website/karakara ../website/env/bin/python3 import_media.py --config_uri ../website/development.ini

cleanup:
	$(PYTHON) cleanup_media.py
	
migrate:
	$(PYTHON) migrate_media.py

# Test -------------------------------------------------------------------------
.PHONY: test

test:
	PYTHONPATH=./ $(PYTEST) tests processmedia_libs --doctest-modules --pdb --maxfail=3

# Clean ------------------------------------------------------------------------
.PHONY: clean

clean:
	rm -rf $(ENV)
	rm -rf libs
	cd tests/source && make clean
