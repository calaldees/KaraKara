import os
import shutil
import hashlib
import base64
import re
from collections import namedtuple, defaultdict
from calaldees.files.scan import fast_scan

ProcessedFileType = namedtuple('ProcessedFileType', ('source_hash_group', 'dict_key', 'attachment_type', 'ext', 'mime','salt'))


class ProcessedFilesManager(object):
    FILE_TYPES = (
        ProcessedFileType('media', 'image1_avif', 'image', 'avif', 'image/avif', ''),
        ProcessedFileType('media', 'image2_avif', 'image', 'avif', 'image/avif', ''),
        ProcessedFileType('media', 'image3_avif', 'image', 'avif', 'image/avif', ''),
        ProcessedFileType('media', 'image4_avif', 'image', 'avif', 'image/avif', ''),
        ProcessedFileType('media', 'image1_webp', 'image', 'webp', 'image/webp', ''),
        ProcessedFileType('media', 'image2_webp', 'image', 'webp', 'image/webp', ''),
        ProcessedFileType('media', 'image3_webp', 'image', 'webp', 'image/webp', ''),
        ProcessedFileType('media', 'image4_webp', 'image', 'webp', 'image/webp', ''),

        ProcessedFileType('media', 'video', 'video', 'webm', 'video/webm; codecs=av01.0.05M.08,opus', ''),
        ProcessedFileType('media', 'preview', 'preview', 'webm', 'video/webm; codecs=av01.0.05M.08,opus', ''), #'video/mp4; codecs=avc1.4D401E,mp4a.40.2'

        ProcessedFileType('data', 'srt', 'srt', 'srt', 'text/plain', ''),
        ProcessedFileType('data', 'tags', 'tags', 'txt', 'text/plain', ''),
    )
    FILE_TYPE_LOOKUP = {
        processed_file_type.attachment_type: processed_file_type
        for processed_file_type in FILE_TYPES
    }

    def __init__(self, path):
        self.path = path

    def get_processed_files(self, hash_dict):
        if not hash_dict:
            return {}
        return {
            file_type.dict_key: ProcessedFile(
                self.path,
                (hash_dict[file_type.source_hash_group], file_type.dict_key, file_type.salt),
                file_type
            )
            for file_type in self.FILE_TYPES
        }

    @property
    def scan(self):
        return fast_scan(self.path)


class ProcessedFile(object):
    def __init__(self, path, hashs, processed_file_type):
        self.hash = gen_string_hash(hashs)
        self.processed_file_type = processed_file_type
        self.path = path

    @property
    def ext(self):
        return self.processed_file_type.ext

    @property
    def mime(self):
        return self.processed_file_type.mime

    @property
    def attachment_type(self):
        return self.processed_file_type.attachment_type

    @property
    def folder(self):
        return self.hash[0]

    @property
    def relative(self):
        return os.path.join(self.folder, f'{self.hash}.{self.ext}')

    @property
    def absolute(self):
        return os.path.abspath(os.path.join(self.path, self.relative))

    def _create_folders_if_needed(self):
        os.makedirs(os.path.join(self.path, self.folder), exist_ok=True)

    def move(self, source_file):
        """
        It is important that 'move' is used rather than opening a stream to the
        absolute path directly.
        The remote destination could be 'scp' or another remote service.
        Always using move allows for this abstraction at a later date
        """
        self._create_folders_if_needed()
        shutil.move(source_file, self.absolute)

    def copy(self, source_file):
        self._create_folders_if_needed()
        shutil.copy2(source_file, self.absolute)

    @property
    def exists(self):
        return os.path.exists(self.absolute)


def gen_string_hash(hashs):
    if isinstance(hashs, str):
        hash_str = hashs
    else:
        hasher = hashlib.sha256()
        hasher.update(''.join(sorted(hashs)).encode('utf-8'))
        #hash_str = hasher.hexdigest()

        # Use base62 string rather than hex
        # re.sub('[+/=]','_', base64.b64encode(hashlib.sha256().digest()).decode('utf8'))[:11]
        # This is filesystem safe, but not bi-directional as some data is lost
        # pow(62, 11) == 52036560683837093888  # this is 4 times more-ish than int64 pow(2,64)
        # pow(62, 10) ==   839299365868340224
        hash_str = re.sub('[+/=]','_', base64.b64encode(hasher.digest()).decode('utf8'))[:11]
    return hash_str
