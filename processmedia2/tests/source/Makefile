
all: test1.avi test2.ogg

test1.avi:
	# Generate 30second test video of 10sec red, 10sec, green, 10sec blue
	ffmpeg -f image2 -framerate 0.1 -i test1_%03d.png test1.avi

test2.ogg:
	# Generate test audio of 10 seconds scilence
	# -b 16
	sox -n -r 44100 -c 2 -L test2.ogg trim 0.0 10.000

clean:
	rm -rf test1.avi test2.ogg