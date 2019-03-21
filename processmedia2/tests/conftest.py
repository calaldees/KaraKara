import pytest

import os
import tempfile
import shutil
import re
import subprocess
from functools import partial


from ._base import ProcessMediaTestManagerBase


# pytest-variables extension ---------------------------------------------------

#pytest_plugins = [
#    'variables',
#]

def pytest_addoption(parser):
    group = parser.getgroup('debugconfig')
    group.addoption(
        '--variable',
        action='append',
        default=[],
        #metavar='path',
        help='Add individual variable by commandline'
    )

@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    assert hasattr(config, '_variables'), 'pytest-variables plugin should be installed'
    config._variables.update(dict(
        re.match(r'(.*?)=(.*)', variable).groups()
        for variable in config.getoption('variable')
    ))


# Utils ------------------------------------------------------------------------

def parser_cmd_to_tuple(cmd):
    return tuple(filter(None, cmd.split(' ')))


# Fixtures ---------------------------------------------------------------------

@pytest.fixture(scope="session")
def TEST1_VIDEO_FILES():
    return {'test1.mp4', 'test1.srt', 'test1.txt'}


@pytest.fixture(scope="session")
def TEST2_AUDIO_FILES():
    return {'test2.ogg', 'test2.png', 'test2.ssa', 'test2.txt'}


@pytest.fixture(scope="session")
def path_source_in_repo():
    return 'tests/source'


@pytest.fixture(scope="session")
def path_source_reference(path_source_in_repo, variables):
    """
    Copy over media in repo to temp folder (this allows symlinking later)
    Some files are missing from the source set and need to be derived when this fixture is called
    """
    tempdir = tempfile.TemporaryDirectory()

    test_media_filenames = set(os.listdir(path_source_in_repo))
    for filename in test_media_filenames:
        shutil.copy2(os.path.join(path_source_in_repo, filename), os.path.join(tempdir.name, filename))

    # Derive other test media
    if 'test1.mp4' not in test_media_filenames:
        # TODO: use `variables` to aquire `cmd_ffmpeg`
        cmd = ('ffmpeg', '-f', 'image2', '-framerate', '0.1', '-i', os.path.join(path_source_in_repo, 'test1_%03d.png'), '-f', 'lavfi', '-i', 'anullsrc', '-shortest', '-c:a', 'aac', '-strict', 'experimental', '-r', '10', '-s', '640x480', os.path.join(tempdir.name, 'test1.mp4'))
        cmd_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
        assert os.path.isfile(os.path.join(tempdir.name, 'test1.mp4'))

    if 'test2.ogg' not in test_media_filenames:
        # TODO: use `variables` to aquire `cmd_sox`
        cmd = ('sox', '-n', '-r', '44100', '-c', '2', '-L', os.path.join(tempdir.name, 'test2.ogg'), 'trim', '0.0', '15.000')
        cmd_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
        assert os.path.isfile(os.path.join(tempdir.name, 'test2.ogg'))

    yield tempdir.name
    tempdir.cleanup()


@pytest.fixture()
def ProcessMediaTestManager(path_source_reference):
    return partial(ProcessMediaTestManagerBase, path_source_reference)


@pytest.fixture()
def external_tools():
    from processmedia_libs.external_tools import ProcessMediaFilesWithExternalTools
    return ProcessMediaFilesWithExternalTools()
