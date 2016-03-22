import os
import tempfile
import json

from scan_media import scan_media
from encode_media import encode_media
from processmedia_libs.meta_manager import MetaManager
from processmedia_libs.processed_files_manager import ProcessedFilesManager

SOURCE_PATH = 'tests/source/'

TEST1_VIDEO_FILES = ('test1.mp4', 'test1.srt', 'test1.txt')
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
        self._temp_processed = tempfile.TemporaryDirectory()
        self._link_source_files()
        self.meta_manager = MetaManager(self.path_meta)
        self.processed_manager = ProcessedFilesManager(self.path_processed)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._temp_scan.cleanup()
        self._temp_meta.cleanup()
        self._temp_processed.cleanup()
        self.meta_manager = None
        self.processed_manager = None

    @property
    def path_source(self):
        return self._temp_scan.name

    @property
    def path_meta(self):
        return self._temp_meta.name

    @property
    def path_processed(self):
        return self._temp_processed.name

    def scan_media(self):
        scan_media(path_source=self.path_source, path_meta=self.path_meta)

    def encode_media(self):
        encode_media(path_source=self.path_source, path_meta=self.path_meta, path_processed=self.path_processed)

    @property
    def meta(self):
        """
        Dump of all the generated raw meta json files
        """
        meta = {}
        for f in os.listdir(self.path_meta):
            with open(os.path.join(self.path_meta, f), 'r') as meta_filehandle:
                meta[f] = json.load(meta_filehandle)
        return meta

    def processed_files(self, name):
        self.meta_manager._release_cache()
        self.meta_manager.load(name)
        source_hash = self.meta_manager.get(name).source_hash
        return self.processed_manager.get_all_processed_files_associated_with_source_hash(source_hash)
