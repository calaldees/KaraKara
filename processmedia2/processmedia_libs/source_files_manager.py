from pathlib import Path
from typing import NamedTuple
from types import MappingProxyType


from . import EXT_TO_TYPE

import logging
log = logging.getLogger(__name__)


class SourceFile(NamedTuple):
    root: Path
    file: Path
    hash: str
    mtime: float
    @classmethod
    def new(cls, root, relative=None, hash=None, mtime=None):
        file = root.joinpath(relative)
        #assert file.is_file()
        return cls(root, file, hash, mtime)
    @property
    def relative(self) -> Path:
        return self.file.relative_to(self.root)
    @property
    def ext(self) -> str:
        return self.file.suffix.replace('.','')
    @property
    def type(self) -> str:
        return EXT_TO_TYPE[self.ext]


class SourceFilesManager(object):
    """
    A file data tracked within the dict in MetaFile needs some supporting methods
    Rather than blote the MetaFile object I opted for a separate wrapper for
    this data dict.
    Because this wrapper can alter the underlying dict in memory, there is no need
    for any complex coupling or communication between the object types.
    How about we create a Mixin of MetaDataManager that can inited with a source path and have @property source_files
    """
    def __init__(self, path):
        self.path = Path(path)
        assert self.path.is_dir()

    def get_source_files(self, metafile) -> MappingProxyType[str, SourceFile]:
        """
        >>> from unittest.mock import Mock
        >>> metafile = Mock()
        >>> metafile.scan_data.values = Mock(return_value=(
        ...     {'relative': 'test.mp4', 'mtime': 101.00, 'hash': '123'},
        ...     {'relative': 'test.srt', 'mtime': 102.00, 'hash': '456'},
        ...     {'relative': 'test.txt', 'mtime': 103.00, 'hash': '789'},
        ... ))
        >>> source_files_manager = SourceFilesManager('/tmp')
        >>> source_files_manager.get_source_files(metafile)
        mappingproxy({'video': SourceFile(root=PosixPath('/tmp'), file=PosixPath('/tmp/test.mp4'), hash='123', mtime=101.0), 'sub': SourceFile(root=PosixPath('/tmp'), file=PosixPath('/tmp/test.srt'), hash='456', mtime=102.0), 'tag': SourceFile(root=PosixPath('/tmp'), file=PosixPath('/tmp/test.txt'), hash='789', mtime=103.0)})
        """
        return MappingProxyType({
            source_file.type: source_file
            for source_file in (
                SourceFile.new(self.path, **scan_file) for scan_file in metafile.scan_data.values()
            )
        })
