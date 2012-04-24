#!/bin/bash

#
# Requirements:
# - avconv (ffmpeg's new command line video converter)
# - libavcodec with patented format support (ubuntu package libavcodec-extra-53)
# - sox
# - mencoder
#
# Usage:
#  ./encode.sh Some_Song/Original_Download.flv
#
# Outputs:
# - Some_Song/thumb.jpg     (320x240 JPG)
# - Some_Song/video.mp4     (full size H264/AAC)
# - Some_Song/preview.mp4   (320x240 H264/AAC with fade out)
#
# TODO: hard code subtitles
#


PREVIEW_LENGTH=15
FADE_LENGTH=5
FPS=29
DIR="`dirname \"$1\"`"


# pick a thumbnail 4 seconds in
avconv -y -itsoffset -4 -i "$1" -vcodec mjpeg -vframes 1 -an -f rawvideo -s 320x240 $DIR/thumb.jpg


# encode full-size video into a chrome-friendly format
# mencoder is needed to bake subs into the video, avconv is needed to encode audio to AAC
mencoder "$1" -slang eng -ovc x264 -oac pcm -o $DIR/video.avi
avconv -y -i $DIR/video.avi -vcodec copy -acodec libvo_aacenc $DIR/video.mp4


# extract and fade out audio preview
avconv -y -i "$1" -t 00:00:$PREVIEW_LENGTH -vn -f aiff pipe: | \
	sox -t aiff - -t aiff - fade t 0 00:00:$PREVIEW_LENGTH $FADE_LENGTH | \
	avconv -i pipe: $DIR/preview.m4a

# extract and fade out video preview
avconv -y -i "$1" -t 00:00:$PREVIEW_LENGTH -an -s 320x240 \
	-vf fade=out:$(($FPS*$PREVIEW_LENGTH-$FPS*$FADE_LENGTH)):$(($FPS*$FADE_LENGTH)) \
	-vcodec libx264 $DIR/preview.m4v

# merge previews
avconv -y -i $DIR/preview.m4a -i $DIR/preview.m4v -acodec copy -vcodec copy $DIR/preview.mp4

# tidy up
rm -f $DIR/preview.m4a $DIR/preview.m4v $DIR/video.avi
