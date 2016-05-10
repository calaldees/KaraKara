import os
from collections import ChainMap
from functools import lru_cache

from libs.misc import file_ext, first
from . import EXTS
from .meta_manager import MetaManager

import logging
log = logging.getLogger(__name__)

MEDIA_FILETYPES = {'video', 'audio', 'sub', 'image'}
DATA_FILETYPES = {'tag', }
ALL_FILETYPES = MEDIA_FILETYPES | DATA_FILETYPES


class SourceFilesManager(object):
    """
    A file data tracked within the dict in MetaFile needs some supporting methods
    Rather than blote the MetaFile object I opted for a separate wrapper for
    this data dict.
    Because this wrapper can alter the underlying dict in memory, there is no need
    for any complex coupling or communication between the object types.
    How about we create a Mixin of MetaDataManager that can inited with a source path and have @property source_files
    """
    def __init__(self, source_path):
        self.source_path = source_path

    def get_source_files(self, metafile):
        return self._wrap_scan_data(metafile, ALL_FILETYPES)

    def get_source_media_files(self, metafile):
        return self._wrap_scan_data(metafile, MEDIA_FILETYPES)

    def _wrap_scan_data(self, metafile, filetypes):
        wrapped_scan_data = tuple(self._wrap_scan_data_item(d) for d in metafile.scan_data.values())
        return {k: self._get_file_for(k, wrapped_scan_data) for k in filetypes}

    def _wrap_scan_data_item(self, data):
        """
        Wrap the stored source data dict item in a ChainMap that adds additional common derived fields
        """
        if not data:
            return {}
        file_no_ext, ext = file_ext(data['relative'])
        return ChainMap(
            dict(
                absolute=os.path.abspath(os.path.join(self.source_path, data['relative'])),
                ext=ext,
                file_no_ext=file_no_ext,
            ),
            # IMPORTANT! Any modification to a chainmap is ALWAYS made to the first dict.
            # We DON'T want any changes to the underlying data from a wrapper
            data,
        )

    def _get_file_for(self, file_type, wrapped_scan_data):
        assert file_type in EXTS.keys(), 'file_type: {0} must be one of {1}'.format(file_type, EXTS.keys())
        exts = EXTS[file_type]
        files_for_type = sorted(
            (v for v in wrapped_scan_data if v['ext'] in exts),
            key=lambda v: exts.index(v['ext']),
            reverse=True
        )
        if len(files_for_type) > 1:
            log.warn('Multiple files for type %s identifyed %s. This may be a mistake. Using only first one', file_type, [f['relative'] for f in files_for_type])
        return first(files_for_type) or {}


class MetaManagerWithSourceFiles(MetaManager):
    """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(kwargs['path_meta'])
        self.source_files_manager = SourceFilesManager(kwargs['path_source'])

    def get(self, name):
        metafile = super().get(name)
        #@property
        @lru_cache(maxsize=1)
        def get_source_files(self):
            return self.source_files_manager.get_source_files(metafile)
        #@property
        @lru_cache(maxsize=1)
        def get_source_meta_files(self):
            return self.source_files_manager.get_source_media_files(metafile)
        metafile.source_files = get_source_files(self)  # DO NOT WANT! Want lazy propery instread
        return metafile
