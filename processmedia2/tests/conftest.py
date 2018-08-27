import pytest


#test1.mp4:
#	ffmpeg -f image2 -framerate 0.1 -i test1_%03d.png -f lavfi -i anullsrc -shortest -c:a aac -strict experimental -r 10 -s 640x480 test1.mp4

#test2.ogg:
	# Generate test audio of 10 seconds scilence
	# -b 16
#	sox -n -r 44100 -c 2 -L test2.ogg trim 0.0 15.000


@pytest.fixture(scope="session")
def TEST1_VIDEO_FILES():
    return set(('test1.mp4', 'test1.srt', 'test1.txt'))


@pytest.fixture(scope="session")
def TEST1_VIDEO_FILES():
    return set(('test2.ogg', 'test2.png', 'test2.ssa', 'test2.txt'))
