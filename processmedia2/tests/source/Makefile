all: test1.mp4 test2.ogg

test1.mp4:
	ffmpeg -f image2 -framerate 0.1 -i test1_%03d.png -f lavfi -i anullsrc -shortest -c:a aac -strict experimental -r 10 -s 640x480 $@

test2.ogg:
	ffmpeg -f lavfi -i anullsrc=r=11025:cl=mono -t 15.000 -acodec libvorbis $@
