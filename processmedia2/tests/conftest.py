import pytest

import os
import tempfile
import shutil
from functools import partial


from ._base import ProcessMediaTestManagerBase


@pytest.fixture(scope="session")
def TEST1_VIDEO_FILES():
    return set(('test1.mp4', 'test1.srt', 'test1.txt'))


@pytest.fixture(scope="session")
def TEST2_AUDIO_FILES():
    return set(('test2.ogg', 'test2.png', 'test2.ssa', 'test2.txt'))


@pytest.fixture(scope="session")
def path_source_in_repo():
    return 'tests/source'


@pytest.fixture(scope="session")
def path_source_reference(path_source_in_repo, variables):
    tempdir = tempfile.TemporaryDirectory()

    # Copy over media in repo to temp folder (this allows symlinking later)
    test_media_filenames = set(os.listdir(path_source_in_repo))
    for filename in test_media_filenames:
        shutil.copy2(os.path.join(path_source_in_repo, filename), os.path.join(tempdir.name, filename))

    # Derive other test media
    if 'test1.mp4' not in test_media_filenames:
        #ffmpeg -f image2 -framerate 0.1 -i test1_%03d.png -f lavfi -i anullsrc -shortest -c:a aac -strict experimental -r 10 -s 640x480 test1.mp4
        raise NotImplementedError()

    if 'test2.ogg' not in test_media_filenames:
        #sox -n -r 44100 -c 2 -L test2.ogg trim 0.0 15.000
        raise NotImplementedError()

    yield tempdir
    tempdir.cleanup()


@pytest.fixture()
def ProcessMediaTestManager(path_source_reference):
    return partial(ProcessMediaTestManagerBase, path_source_reference)
