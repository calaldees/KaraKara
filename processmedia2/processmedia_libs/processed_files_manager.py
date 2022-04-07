import shutil
import hashlib
import base64
import re
from itertools import chain
from pathlib import Path
from typing import NamedTuple
from types import MappingProxyType

from calaldees.files.scan import fast_scan


class ProcessedFileType(NamedTuple):
    key: str
    attachment_type: str
    ext: str
    mime:str
    encode_args: dict

    @property
    def salt(self):
        return str(self.encode_args)

BYPASS="scale=w='128:h=floor((128*(1/a))/2)*2'"

class ProcessedFilesManager(object):
    FILE_TYPES = MappingProxyType({processed_file_type.key: processed_file_type for processed_file_type in (
        ProcessedFileType('video', 'video', 'webm', 'video/webm; codecs=av01.0.05M.08,opus', dict(
            vcodec='libsvtav1',
            preset=4,
            qp=50,
            sc_detection='true',
            pix_fmt='yuv420p10le',
            g=240,
            acodec='libopus',
            #vf=BYPASS,
        )),
        ProcessedFileType('preview_av1', 'preview', 'webm', 'video/webm; codecs=av01.0.05M.08,opus', dict(
            vcodec='libsvtav1',
            preset=4,
            qp=60,
            sc_detection='true',
            pix_fmt='yuv420p10le',
            g=240,
            acodec='libopus',
            ab='24k',
            #vf=BYPASS,
        )), 
        ProcessedFileType('preview_h265', 'preview', 'mp4', 'video/mp4; codecs=avc1.4D401E,mp4a.40.2', dict(
            vcodec='libx265',
            #crf=50,  # SHITE
            crf=39,
            preset='slow',
            acodec='libfdk_aac',  # https://trac.ffmpeg.org/wiki/Encode/AAC#HE-AACversion2
            ab='24k',
            #vf=BYPASS,
        )),
        ProcessedFileType('image1_avif', 'image', 'avif', 'image/avif', None),
        ProcessedFileType('image2_avif', 'image', 'avif', 'image/avif', None),
        ProcessedFileType('image3_avif', 'image', 'avif', 'image/avif', None),
        ProcessedFileType('image4_avif', 'image', 'avif', 'image/avif', None),
        ProcessedFileType('image1_webp', 'image', 'webp', 'image/webp', None),
        ProcessedFileType('image2_webp', 'image', 'webp', 'image/webp', None),
        ProcessedFileType('image3_webp', 'image', 'webp', 'image/webp', None),
        ProcessedFileType('image4_webp', 'image', 'webp', 'image/webp', None),
    )})

    def __init__(self, path):
        self.path = Path(path)
        assert self.path.is_dir()

    def get_processed_files(self, source_media_hashs) -> MappingProxyType:
        """
        >>> processed_files_manager = ProcessedFilesManager('/tmp')
        >>> processed_files = processed_files_manager.get_processed_files(('1', '2', '3'))
        >>> processed_file = processed_files['image1_avif']
        >>> processed_file
        ProcessedFile(root=PosixPath('/tmp'), type=ProcessedFileType(key='image1_avif', attachment_type='image', ext='avif', mime='image/avif', encode_args=None), hash='gUIpHii00zG')
        >>> processed_file.relative
        PosixPath('g/gUIpHii00zG.avif')

        >>> processed_files2 = processed_files_manager.get_processed_files(('4', '5', '6'))
        >>> processed_file2 = processed_files2['image1_avif']
        >>> processed_file2.hash != processed_file.hash
        True
        """
        source_media_hashs = tuple(source_media_hashs)
        return MappingProxyType({
            file_type.key: ProcessedFile.new(
                self.path,
                file_type,
                chain.from_iterable((source_media_hashs, (file_type.key, file_type.salt))),
            )
            for file_type in self.FILE_TYPES.values()
        })

    @property
    def scan(self):
        return fast_scan(str(self.path))


class ProcessedFile(NamedTuple):
    root: Path
    type: ProcessedFileType
    hash: str

    @classmethod
    def new(cls, root, type, hashs):
        return cls(root, type, gen_string_hash(hashs))

    @property
    def file(self) -> Path: 
        return self.root.joinpath(self.hash[0], f'{self.hash}.{self.type.ext}')

    @property
    def relative(self) -> Path:
        return self.file.relative_to(self.root)

    def move(self, source_file):
        """
        It is important that 'move' is used rather than opening a stream to the
        absolute path directly.
        The remote destination could be 'scp' or another remote service.
        Always using move allows for this abstraction at a later date
        """
        self.file.parent.mkdir(exist_ok=True)
        shutil.move(source_file, self.file.resolve())

    def copy(self, source_file):
        self.file.parent.mkdir(exist_ok=True)
        shutil.copy2(source_file, self.file.resolve())


def gen_string_hash(hashs):
    """
    >>> gen_string_hash(('1', '2', '3'))
    'pmWkWSBCL51'
    """
    if isinstance(hashs, str):
        return hashs

    hasher = hashlib.sha256()
    hasher.update(''.join(sorted(hashs)).encode('utf-8'))
    #hash_str = hasher.hexdigest()

    # Use base62 string rather than hex
    # re.sub('[+/=]','_', base64.b64encode(hashlib.sha256().digest()).decode('utf8'))[:11]
    # This is filesystem safe, but not bi-directional as some data is lost
    # pow(62, 11) == 52036560683837093888  # this is 4 times more-ish than int64 pow(2,64)
    # pow(62, 10) ==   839299365868340224
    return re.sub('[+/=]','_', base64.b64encode(hasher.digest()).decode('utf8'))[:11]
