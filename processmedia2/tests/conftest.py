import pytest

import os
import tempfile
import shutil
import re
import subprocess
from functools import partial
from pathlib import Path


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
    return Path('tests/source')


@pytest.fixture(scope="session")
def path_source_reference(path_source_in_repo, variables):
    """
    Copy over media in repo to temp folder (this allows symlinking later)
    Some files are missing from the source set and need to be derived when this fixture is called
    """
    tempdir = tempfile.TemporaryDirectory()

    test_media_filenames = set(os.listdir(path_source_in_repo))
    for filename in test_media_filenames:
        shutil.copy2(path_source_in_repo.joinpath(filename), Path(tempdir.name, filename))

    def generate_missing_source_media(out, cmd):
        if not out.is_file():
            cmd += (out, )
            cmd_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
            assert cmd_result.returncode == 0
            assert out.is_file()
            # Attempt to cache this in the source/repo folder if possible to write to this area (this accelerate subsequent runs if possible). This generated files should be in .gitignore.
            # The largely does not work at code is always mounted at `readonly`
            # maybe A Makefile that can be run on the host could be created to mirror this?
            try:
                shutil.copy2(out, path_source_in_repo.joinpath(out.name))
            except OSError as ex:  ## TODO: catch real exception
                pass

    generate_missing_source_media(
        out=Path(tempdir.name, 'test1.mp4'),
        cmd=('ffmpeg', '-f', 'image2', '-framerate', '0.1', '-i', path_source_in_repo.joinpath('test1_%03d.png'), '-f', 'lavfi', '-i', 'anullsrc', '-shortest', '-c:a', 'aac', '-strict', 'experimental', '-r', '10', '-s', '640x480'),
    )
    generate_missing_source_media(
        out=Path(tempdir.name, 'test2.ogg'),
        cmd=('ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=r=11025:cl=mono', '-t', '15.000', '-acodec', 'libvorbis'),
    )

    yield tempdir.name
    tempdir.cleanup()


@pytest.fixture()
def ProcessMediaTestManager(path_source_reference):
    return partial(ProcessMediaTestManagerBase, path_source_reference)


@pytest.fixture()
def external_tools():
    from processmedia_libs.external_tools import ProcessMediaFilesWithExternalTools
    return ProcessMediaFilesWithExternalTools()
