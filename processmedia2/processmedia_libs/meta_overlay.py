from functools import lru_cache

from .meta_manager import MetaManager, MetaFile
from .source_files_manager import SourceFilesManager
from .processed_files_manager import gen_string_hash


class MetaManagerExtended(MetaManager):
    """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(kwargs['path_meta'])
        self.source_files_manager = SourceFilesManager(kwargs['path_source'])

    def get(self, name):
        return self.MetaFileWithSourceFiles(super().get(name), self.source_files_manager)

    class MetaFileWithSourceFiles(MetaFile):
        def __init__(self, metafile, source_files_manager):
            self.__dict__ = metafile.__dict__
            self.source_files_manager = source_files_manager

        @property
        @lru_cache(maxsize=1)
        def source_files(self):
            return self.source_files_manager.get_source_files(self)

        @property
        @lru_cache(maxsize=1)
        def source_media_files(self):
            return self.source_files_manager.get_source_media_files(self)

        @property
        @lru_cache(maxsize=1)
        def source_data_files(self):
            return self.source_files_manager.get_source_data_files(self)

        def update_source_hash(self):
            def gen_hash(source_files):
                return gen_string_hash(f['hash'] for f in source_files.values() if f)  # Derive the source hash from the child component hashs
            self.source_hash = gen_hash(self.source_files)
            self.source_media_hash = gen_hash(self.source_media_files)
            self.source_data_hash = gen_hash(self.source_data_files)
            return all((self.source_hash, self.source_media_hash, self.source_data_hash))
