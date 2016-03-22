
all: test1.mp4 test2.ogg

test1.mp4:
	ffmpeg -f image2 -framerate 0.1 -i test1_%03d.png -f lavfi -i anullsrc -shortest -c:a aac -strict experimental -r 30 -s 1024x768 test1.mp4

test2.ogg:
	# Generate test audio of 10 seconds scilence
	# -b 16
	sox -n -r 44100 -c 2 -L test2.ogg trim 0.0 10.000

clean:
	rm -rf test1.mp4 test2.ogg