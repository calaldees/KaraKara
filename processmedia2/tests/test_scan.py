import pytest
import os
import tempfile
import json
import shutil
import time

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
        self._temp_scan = tempfile.TemporaryDirectory()
        self._temp_meta = tempfile.TemporaryDirectory()
        self._link_source_files()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._temp_scan.cleanup()
        self._temp_meta.cleanup()

    @property
    def path_source(self):
        return self._temp_scan.name

    @property
    def path_meta(self):
        return self._temp_meta.name

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
        # Ensure source files are grouped effectivly
        meta = scan.scan_media()
        assert set(meta['test1.json']['scan'].keys()) == {'test1.avi', 'test1.srt', 'test1.txt'}
        assert set(meta['test2.json']['scan'].keys()) == {'test2.ogg'}

        # If a file is renamed - it is searched and re-associated with the original group even if it's name does not match anymore
        subtitle_hash = meta['test1.json']['scan']['test1.srt']['hash']
        os.rename(os.path.join(scan.path_source, 'test1.srt'), os.path.join(scan.path_source, 'testX.srt'))
        meta = scan.scan_media()
        assert meta['test1.json']['scan']['testX.srt']['hash'] == subtitle_hash, 'File was renamed, but he hash should be the same'

        # Modify the reassociated file - the file should have it's hash updated and not be dissassociated
        subtitle_file = os.path.join(scan.path_source, 'testX.srt')
        with open(subtitle_file, 'r') as subtitle_filehandle:
            subtitles = subtitle_filehandle.read()
        os.remove(subtitle_file)
        with open(subtitle_file, 'w') as subtitle_filehandle:
            subtitle_filehandle.write(subtitles.replace('Red', 'Red2'))
        meta = scan.scan_media()
        assert meta['test1.json']['scan']['testX.srt']['hash'] != subtitle_hash, 'File hash should have changed as the contents were modified'
