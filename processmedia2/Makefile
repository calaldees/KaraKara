OS = $(shell uname -s)
LINUX_DISTRO=$(shell lsb_release -a 2> /dev/null | grep "Distributor ID:" | sed 's|.*:.\(.*\)|\1|')

PYTHON_DEPENDENCYS=pip-requirements.txt

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
	# Help

# Installation -----------------------------------------------------------------
.PHONY: install
install: install_$(OS) $(ENV) libs

# OSX installation
.PHONY: install_Darwin has-brew
has-brew:
	# Fails if homebrew is not installed
	which brew
install_Darwin: has-brew
	brew update
	brew install python3 jpegoptim tesseract
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
		--with-openh264 \
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
		--with-zeromq \
		--with-zimg


# Linux installation
.PHONY: install_Linux install_Debian install_Ubuntu apt-installation
install_Linux: install_$(LINUX_DISTRO)
install_Debian: apt-installation
install_Ubuntu: apt-installation
apt-installation:
	sudo apt-get install -y python3 python3-dev python3-pip sox jpegoptim tesseract-ocr tesseract-ocr-eng libjpeg-dev virtualenv ffmpeg
	#if dpkg -s ffmpeg ; then \
	#	echo ffmpeg already installed ;\
	#else \
	#	echo installing ffmpeg ;\
		#sudo add-apt-repository ppa:motumedia/libav-daily ;\
		#sudo add-apt-repository ppa:jon-severinsson/ffmpeg ;\
	#	sudo apt-get update ;\
	#	sudo apt-get install -y ffmpeg \
		#libavcodec-extra-53
	#fi


.PHONY: has-python3
has-python3:
	# Fail if python3 is not installed
	which python3
	# Fail if virtualenv is not installed
	which virtualenv
$(ENV):
	virtualenv --no-site-packages -p python3 $(ENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r $(PYTHON_DEPENDENCYS)


.PHONY: upgrade
upgrade:
	$(PIP) install -r $(PYTHON_DEPENDENCYS) --upgrade
	brew reinstall jpegoptim tesseract sox ffmpeg


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
.PHONY: scan encode import cleanup process

scan:
	$(PYTHON) scan_media.py

encode:
	$(PYTHON) encode_media.py --process_order_function random
	#--log_level 0
	#--log_level 30

import:
	PYTHONPATH="$(WEB_WORKING)" $(WEB_PYTHON) import_media.py --config_uri $(WEB_PATH)/development.ini

cleanup:
	$(PYTHON) cleanup_media.py

process: scan encode import cleanup


# Migrate --

.PHONY: migrate
migrate:
	$(PYTHON) migrate_media.py --log_level 0 --path_source ~/Applications/KaraKara/files --path_destination ~/Applications/KaraKara/migrate



# Test -------------------------------------------------------------------------
.PHONY: test cloc

test:
	$(MAKE) all --directory tests/source
	PYTHONPATH=./ $(PYTEST) processmedia_libs libs tests --doctest-modules --pdb --maxfail=3 --ignore=tests/test_import.py
	$(MAKE) ini --directory $(WEB_PATH)
	PYTHONPATH="$(WEB_WORKING):./:$(ENV)/lib/python3.5/site-packages/" $(WEB_PYTEST) tests/test_import.py --pdb

cloc:
	cloc --exclude-dir=$(ENV) ./

# Clean ------------------------------------------------------------------------
.PHONY: clean

clean:
	rm -rf .cache __pycache__ $(ENV) libs
	$(MAKE) clean --directory tests/source
