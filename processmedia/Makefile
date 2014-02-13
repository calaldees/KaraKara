# Tools Required:
#    libav (with x264 support)
#    qt-faststart (found in the tools/ directory of libav sources)
#    mencoder (with x264, freetype2, and ass subtitle support)
#    sox
#
# Guides:
# http://sub.wordnerd.de/linux-subs.html


help:
	# processmedia
	#    install
	#    

install: 
	if dpkg -s libav-tools ; then \
		echo libav already installed; \
	else \
		echo installing libav; \
		sudo add-apt-repository ppa:motumedia/libav-daily
		sudo apt-get update
		sudo apt-get install -y libav-tools libavcodec-extra-53 sox mencoder ; \
	fi
