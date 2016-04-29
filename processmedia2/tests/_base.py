import os
import tempfile
import json
from pathlib import Path

from scan_media import scan_media
from encode_media import encode_media
from processmedia_libs.meta_manager import MetaManager
from processmedia_libs.processed_files_manager import ProcessedFilesManager

SOURCE_PATH = 'tests/source/'

TEST1_VIDEO_FILES = set(('test1.mp4', 'test1.srt', 'test1.txt'))
TEST2_AUDIO_FILES = set(('test2.ogg', 'test2.png', 'test2.ssa', 'test2.txt'))


# Utils ------------------------------------------------------------------------

class ProcessMediaTestManager(object):

    def __init__(self, source_files=set()):
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
        Dump of all the generated raw meta json files into python data structure
        """
        meta = {}
        for filename in os.listdir(self.path_meta):
            with open(os.path.join(self.path_meta, filename), 'r') as meta_filehandle:
                meta[filename] = json.load(meta_filehandle)
        return meta
    @meta.setter
    def meta(self, data):
        self.meta_manager._release_cache()
        for f in os.listdir(self.path_meta):
            os.remove(os.path.join(self.path_meta, f))
        for filename, meta_data in data.items():
            with open(os.path.join(self.path_meta, filename), 'w') as meta_filehandle:
                json.dump(meta_data, meta_filehandle)
        self.meta_manager.load_all()

    def get_source_hash(self, name):
        self.meta_manager._release_cache()
        self.meta_manager.load(name)
        return self.meta_manager.get(name).source_hash

    def get_all_processed_files_associated_with_source_hash(self, source_hash):
        return self.processed_manager.get_all_processed_files_associated_with_source_hash(source_hash)

    def processed_files(self, name):
        return self.get_all_processed_files_associated_with_source_hash(self.get_source_hash(name))

    def mock_processed_files(self, filenames):
        for f in filenames:
            file_path, file_name = os.path.split(f)
            os.makedirs(os.path.join(self.path_processed, file_path), exist_ok=True)
            Path(os.path.join(self.path_processed, f)).touch()
