from functools import lru_cache

from .meta_manager import MetaManager, MetaFile
from .source_files_manager import SourceFilesManager
from .processed_files_manager import ProcessedFilesManager, gen_string_hash


class MetaManagerExtended(MetaManager):
    """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(kwargs['path_meta'])
        self.source_files_manager = SourceFilesManager(kwargs['path_source'])
        self.processed_files_manager = ProcessedFilesManager(kwargs['path_processed'])

    def get(self, name):
        super_object = super().get(name)
        if super_object:
            return self.MetaFileWithSourceFiles(super_object, self.source_files_manager, self.processed_files_manager)

    @property
    def meta_items(self):
        return (self.get(name) for name in self.meta.keys())

    class MetaFileWithSourceFiles(MetaFile):
        SOURCE_TYPES = {'media', 'data'}

        def __init__(self, metafile, source_files_manager, processed_files_manager):
            self.__dict__ = metafile.__dict__
            self.source_files_manager = source_files_manager
            self.processed_files_manager = processed_files_manager

        @property
        def source_files(self):
            return self.get_source_files()

        @lru_cache(maxsize=len(SOURCE_TYPES)+1)
        def get_source_files(self, file_type=None):
            return self.source_files_manager.get_source_files(self, file_type)

        def update_source_hashs(self):
            self.source_hashs.clear()
            self.source_hashs.update({
                source_type: gen_string_hash(f['hash'] for f in self.get_source_files(source_type).values() if f)
                for source_type in self.SOURCE_TYPES
            })
            self.source_hashs[MetaFile.SOURCE_HASH_FULL_KEY] = gen_string_hash(self.source_hashs.values())
            self._processed_files.cache_clear()
            return all(self.source_hashs.values())

        @lru_cache(maxsize=1)
        def _processed_files(self):
            return self.processed_files_manager.get_processed_files(self.source_hashs)
        @property
        def processed_files(self):
            return self._processed_files()
