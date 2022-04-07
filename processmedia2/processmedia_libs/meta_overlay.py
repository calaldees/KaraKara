from functools import cached_property, lru_cache

from .meta_manager import MetaManager, MetaFile
from .source_files_manager import SourceFilesManager
from .processed_files_manager import ProcessedFilesManager, gen_string_hash


class MetaManagerExtended(MetaManager):
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
        def __init__(self, metafile, source_files_manager, processed_files_manager):
            self.__dict__ = metafile.__dict__
            self.source_files_manager = source_files_manager
            self.processed_files_manager = processed_files_manager

        @cached_property
        def source_files(self):
            return self.source_files_manager.get_source_files(self)

        @cached_property
        def processed_files(self):
            return self.processed_files_manager.get_processed_files((
                source_file.hash
                for source_file_type, source_file in self.source_files.items()
                if source_file_type in ('video', 'audio', 'image')  # only source media types modify the processed_file hash
            ))
