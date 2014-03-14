'processmedia' component normalises mixed video/audio/subtitle input in to
consistent output directory structure with metadata in JSON files.

See Spec.txt for full processing and output specification.

Tool requirements:
  * libav (with x264 support)
  * qt-faststart (found in the tools/ directory of libav sources)
  * mencoder (with x264, freetype2, and ass subtitle support)
  * sox

You should be prepared to build these from sources as most binary
distributions are incomplete or broken.
