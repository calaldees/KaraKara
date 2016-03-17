import pytest
import os
import tempfile
import json
from contextlib import contextmanager

from scan_media import main as scan_media


SOURCE_PATH = 'tests/source/'

TEST1_VIDEO_FILES = ('test1.avi', 'test1.srt', 'test1.txt')
TEST2_AUDIO_FILES = ('test2.ogg',)


# Fixtures ---------------------------------------------------------------------

@contextmanager
def temp_source_folder(files):
    with tempfile.TemporaryDirectory() as tempdir:
        for f in files:
            os.link(
                os.path.join(SOURCE_PATH, f),
                os.path.join(tempdir, f)
            )
        yield tempdir


@contextmanager
def scan_meta(source_files):
    with tempfile.TemporaryDirectory() as path_meta:
        with temp_source_folder(source_files) as path_source:
            scan_media(
                path_source=path_source,
                path_meta=path_meta
            )
            meta = {}
            for f in os.listdir(path_meta):
                with open(os.path.join(path_meta, f), 'r') as meta_filehandle:
                    meta[f] = json.load(meta_filehandle)
            yield meta


# Tests ------------------------------------------------------------------------

def test_scan_grouping():
    with scan_meta(TEST1_VIDEO_FILES + TEST2_AUDIO_FILES) as meta:
        assert {k for k in meta['test1.json']['scan'].keys()} == {'test1.avi', 'test1.srt', 'test1.txt'}
        assert {k for k in meta['test2.json']['scan'].keys()} == {'test2.ogg'}
