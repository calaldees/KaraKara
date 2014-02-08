#Notes
# http://sub.wordnerd.de/linux-subs.html
#  sudo add-apt-repository ppa:motumedia/libav-daily
# apt-get install libavcodec-extra-53 sox mencoder

help:
	# Makefile placeholder
	#   install

install: build/libav build/qt-faststart build/mencoder build/sox

build:
	mkdir build

build/libav: build
	# libav (with x264 support)

build/libav/tools/qt-faststart: build/libav
	# qt-faststart (found in the tools/ directory of libav sources)

build/mencoder: build
	# mencoder (with x264, freetype2, and ass subtitle support)

build/sox: build
	# sox
