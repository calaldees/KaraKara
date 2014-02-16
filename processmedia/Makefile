# Tools Required:
#    libav (with x264 support)
#    qt-faststart (found in the tools/ directory of libav sources)
#    mencoder (with x264, freetype2, and ass subtitle support)
#    sox
#
# Guides:
# http://sub.wordnerd.de/linux-subs.html
# http://stackoverflow.com/questions/3466166/how-to-check-if-running-in-cygwin-mac-or-linux

help:
	# processmedia
	#    install
	#    install_mac
	#    install_linux

install:
	if ["$(uname)" == "Darwin"]; then \
		echo "MacOSX" ;\
	elif ["$(expr substr $(uname -s) 1 5)" == "Linux"]; then \
		echo "Linux" ;\
	elif ["$(expr substr $(uname -s) 1 10)" == "MINGW32_NT"]; then \
		echo "WindowsNT" ;\
	fi \

install_mac:
	brew install libav sox mplayer ffmpeg --devel --with-libass --with-freetype --with-fdk-aac --with-libvo-aacenc --with-ffplay --with-frei0r --with-libbluray --with-libquvi --with-libvo-aacenc --with-libvpx --with-opencore-amr --with-openjpeg --with-openssl --with-opus --with-rtmpdump --with-schroedinger --with-speex --with-theora --with-tools --with-libcaca --with-flac --with-lame --with-libao --with-libsndfile --with-libvorbis --with-opencore-amr --with-gnutls

install_linux:
	if dpkg -s libav-tools ; then \
		echo libav already installed; \
	else \
		echo installing libav; \
		sudo add-apt-repository ppa:motumedia/libav-daily; \
		sudo apt-get update; \
		sudo apt-get install -y libav-tools libavcodec-extra-53 sox mencoder ; \
	fi
