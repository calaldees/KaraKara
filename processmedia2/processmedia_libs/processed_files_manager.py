import shutil
from itertools import chain
from pathlib import Path
from typing import NamedTuple
from collections.abc import MappingView, Sequence
from types import MappingProxyType

from calaldees.files.scan import fast_scan

from .hash import gen_string_hash


# ffmpeg reuseable args
VF_SCALE_TEMPLATE = "scale=w='{0}:h=floor(({0}*(1/a))/2)*2'"
SCALE_IMAGE=dict(
    vf=VF_SCALE_TEMPLATE.format(512),
)
SCALE_EVEN=dict(
    vf='scale=w=floor(iw/2)*2:h=floor(ih/2)*2',  # 264 codec can only handle dimension a multiple of 2. Some input does not adhere to this and need correction.
)
PREVIEW=dict(
    ab='24k',
    ac=1,
    vf=VF_SCALE_TEMPLATE.format(320),
)
NORMALIZE_AUDIO=dict(
    #ar=48000,
    af='loudnorm=I=-23:LRA=1:dual_mono=true:tp=-1',
    # GoogleGroups - crazy audio guys conversation
    # https://groups.google.com/a/opencast.org/g/users/c/R40ZE3l_ay8/m/2IUpQTcQCAAJ
    # Another idea:
    # highpass=f=120,acompressor=threshold=0.3:makeup=3:release=50:attack=5:knee=4:ratio=10:detection=peak,alimiter=limit=0.95
)
# 'scale_even': 'scale=w=floor(iw/2)*2:h=floor(ih/2)*2',  # h264 codec can only handle dimension a multiple of 2. Some input does not adhere to this and need correction.


class ProcessedFileType(NamedTuple):
    key: str
    attachment_type: str
    ext: str
    mime:str
    encode_args: dict

    @property
    def salt(self):
        return str(self.encode_args)


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
            ac=2,
            **SCALE_EVEN,
            **NORMALIZE_AUDIO,
        )),
        ProcessedFileType('preview_av1', 'preview', 'webm', 'video/webm; codecs=av01.0.05M.08,opus', dict(
            vcodec='libsvtav1',
            preset=4,
            qp=60,
            sc_detection='true',
            pix_fmt='yuv420p10le',
            g=240,
            acodec='libopus',
            **PREVIEW,
            **NORMALIZE_AUDIO,
        )), 
        ProcessedFileType('preview_h265', 'preview', 'mp4', 'video/mp4; codecs=avc1.4D401E,mp4a.40.2', dict(
            vcodec='libx265',
            #crf=50,  # Minimum
            crf=39,
            preset='slow',
            acodec='libfdk_aac',  # https://trac.ffmpeg.org/wiki/Encode/AAC#HE-AACversion2
            **PREVIEW,
            **NORMALIZE_AUDIO,
        )),
        ProcessedFileType('image1_avif', 'image', 'avif', 'image/avif', SCALE_IMAGE),
        ProcessedFileType('image2_avif', 'image', 'avif', 'image/avif', SCALE_IMAGE),
        ProcessedFileType('image3_avif', 'image', 'avif', 'image/avif', SCALE_IMAGE),
        ProcessedFileType('image4_avif', 'image', 'avif', 'image/avif', SCALE_IMAGE),
        ProcessedFileType('image1_webp', 'image', 'webp', 'image/webp', SCALE_IMAGE),
        ProcessedFileType('image2_webp', 'image', 'webp', 'image/webp', SCALE_IMAGE),
        ProcessedFileType('image3_webp', 'image', 'webp', 'image/webp', SCALE_IMAGE),
        ProcessedFileType('image4_webp', 'image', 'webp', 'image/webp', SCALE_IMAGE),
        ProcessedFileType('subtitle', 'subtitle', 'vtt', 'text/vtt', dict()),
    )})

    def __init__(self, path):
        self.path = Path(path)
        assert self.path.is_dir()

    def get_processed_files(self, source_media_hashs: Sequence[str]) -> MappingProxyType[str, ProcessedFile]:
        """
        >>> processed_files_manager = ProcessedFilesManager('/tmp')
        >>> processed_files = processed_files_manager.get_processed_files(('1', '2', '3'))
        >>> processed_file = processed_files['image1_avif']
        >>> len(processed_file.hash)
        11

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
