import os
import tempfile
import json
from pathlib import Path

from processmedia_libs.meta_overlay import MetaManagerExtended

from scan_media import scan_media
from encode_media import encode_media, Encoder
from cleanup_media import cleanup_media


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
        self.meta_manager = MetaManagerExtended(path_meta=self.path_meta, path_source=self.path_source, path_processed=self.path_processed)
        self.processed_files_manager = self.meta_manager.processed_files_manager
        self.source_files_manager = self.meta_manager.source_files_manager

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._temp_scan.cleanup()
        self._temp_meta.cleanup()
        self._temp_processed.cleanup()
        self.meta_manager = None
        self.processed_manager = None
        self.source_files_manager = None

    @property
    def path_source(self):
        return self._temp_scan.name

    @property
    def path_meta(self):
        return self._temp_meta.name

    @property
    def path_processed(self):
        return self._temp_processed.name

    @property
    def commandline_kwargs(self):
        return dict(path_meta=self.path_meta, path_source=self.path_source, path_processed=self.path_processed, force=True)

    def scan_media(self):
        self.meta_manager._release_cache()
        scan_media(**self.commandline_kwargs)

    def encode_media(self, mock=None):
        self.meta_manager._release_cache()
        if mock:
            with MockEncodeExternalCalls():
                encode_media(**self.commandline_kwargs)
        else:
            encode_media(**self.commandline_kwargs)

    def cleanup_media(self):
        self.meta_manager._release_cache()
        cleanup_media(**self.commandline_kwargs)

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

    def update_source_hashs(self, name):
        m = self.get(name)
        m.update_source_hashs()
        self.meta_manager.save(name)

    def get(self, name):
        self.meta_manager._release_cache()
        self.meta_manager.load(name)
        return self.meta_manager.get(name)

    def mock_processed_files(self, filenames):
        for f in filenames:
            file_path, file_name = os.path.split(f)
            os.makedirs(os.path.join(self.path_processed, file_path), exist_ok=True)
            Path(os.path.join(self.path_processed, f)).touch()


from unittest.mock import patch
import processmedia_libs.external_tools
from pathlib import Path

class MockEncodeExternalCalls(object):

    def __init__(self, **kwargs):
        """
        MockEncodeExternalCalls(encode_video=True, extract_image=False)
        """
        self.method_returns = dict(
            probe_media=self._mock_command_return_probe,
            encode_video=self._mock_command_return_success,
            encode_audio=self._mock_command_return_success,
            encode_preview_video=self._mock_command_return_success,
            extract_image=self._mock_command_return_success,
        )
        self.method_returns.update({
            method_name: self._mock_command_return_success if return_ok_or_fail else self._mock_command_return_fail
            for method_name, return_ok_or_fail in kwargs.items()
        })
        self.patchers = {}
        self.active_patches = {}

    def __enter__(self):
        self.patchers.clear()
        self.patchers.update({
            method_name: patch.object(
                processmedia_libs.external_tools,
                method_name,
                wraps=mock_return
            )
            for method_name, mock_return in self.method_returns.items()
        })
        self.active_patches.clear()
        self.active_patches.update({
            method_name: patcher.start()
            for method_name, patcher in self.patchers.items()
        })
        return self.active_patches

    def __exit__(self, exc_type, exc_value, traceback):
        for patcher in self.patchers.values():
            patcher.stop()
        self.patchers.clear()
        self.active_patches.clear()

    @staticmethod
    def _mock_command_return_probe(*args, **kwargs):
        return {'width': 1, 'height': 1, 'duration': 1}

    @staticmethod
    def _mock_command_return_success(*args, **kwargs):
        if ('destination' in kwargs):
            Path(kwargs['destination']).touch()
        return (True, 'Mock Success')

    @staticmethod
    def _mock_command_return_fail(*args, **kwargs):
        return (False, 'Mock Failure')
