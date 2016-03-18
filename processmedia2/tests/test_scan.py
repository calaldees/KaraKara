import pytest
import os
import tempfile
import json

from scan_media import main as scan_media


SOURCE_PATH = 'tests/source/'

TEST1_VIDEO_FILES = ('test1.avi', 'test1.srt', 'test1.txt')
TEST2_AUDIO_FILES = ('test2.ogg',)


# Utils ------------------------------------------------------------------------


class ScanManager(object):

    def __init__(self, source_files):
        self.source_files = source_files

    def _link_source_files(self):
        for f in self.source_files:
            os.link(
                os.path.join(SOURCE_PATH, f),
                os.path.join(self.path_source, f)
            )

    def __enter__(self):
        self.temp_scan = tempfile.TemporaryDirectory()
        self.temp_meta = tempfile.TemporaryDirectory()
        self._link_source_files()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.temp_scan.cleanup()
        self.temp_meta.cleanup()

    @property
    def path_source(self):
        return self.temp_scan.name

    @property
    def path_meta(self):
        return self.temp_meta.name

    def scan_media(self):
        scan_media(path_source=self.path_source, path_meta=self.path_meta)

        meta = {}
        for f in os.listdir(self.path_meta):
            with open(os.path.join(self.path_meta, f), 'r') as meta_filehandle:
                meta[f] = json.load(meta_filehandle)
        return meta


# Tests ------------------------------------------------------------------------

def test_scan_grouping():
    with ScanManager(TEST1_VIDEO_FILES + TEST2_AUDIO_FILES) as scan:
        meta = scan.scan_media()
        assert set(meta['test1.json']['scan'].keys()) == {'test1.avi', 'test1.srt', 'test1.txt'}
        assert set(meta['test2.json']['scan'].keys()) == {'test2.ogg'}
