import os
import shutil
import hashlib
from collections import namedtuple, defaultdict
from libs.misc import fast_scan

ProcessedFileType = namedtuple('ProcessedFileType', ('source_hash_type', 'attachment_type', 'ext', 'salt'))


class ProcessedFilesManager(object):
    DEFAULT_NUMBER_OF_IMAGES = 4
    FILE_TYPE_LOOKUP = {
        processed_file_type.attachment_type: processed_file_type
        for processed_file_type in (
            # NOTE: These must match the attachment_types in the Track model
            ProcessedFileType('media', 'image', 'jpg', ''),
            ProcessedFileType('media', 'video', 'mp4', ''),
            ProcessedFileType('media', 'preview', 'mp4', ''),

            ProcessedFileType('data', 'srt', 'srt', ''),
            ProcessedFileType('data', 'tags', 'txt', ''),
        )
    }

    def __init__(self, path):
        self.path = path

    def _factory(self, hashs, ext):
        return ProcessedFile(self.path, hashs, ext)

    def get_processed_file(self, source_hash, file_type, *args):
        assert source_hash, 'source_hash can never be None. Investigation needed'
        file_type = self.FILE_TYPE_LOOKUP[file_type]
        return self._factory(
            (source_hash, file_type.attachment_type, file_type.salt, ''.join((str(a) for a in args))),
            file_type.ext
        )

    def get_all_processed_files_associated_with_source_hash(self, source_hash):
        if hasattr(source_hash, 'source_hash'):
            source_hash = source_hash.source_hash
        if not source_hash:
            return {}
        processed_files = defaultdict(list)
        for t in ('video', 'preview', 'srt', 'tags'):
            processed_files[t].append(self.get_processed_file(source_hash, t))
        for image_num in range(self.DEFAULT_NUMBER_OF_IMAGES):
            processed_files['image'].append(self.get_processed_file(source_hash, 'image', image_num))
        return processed_files

    @property
    def scan(self):
        return fast_scan(self.path)


class ProcessedFile(object):
    def __init__(self, path, hashs, ext):
        self.hash = gen_string_hash(hashs)
        self.ext = ext
        self.path = path

    @property
    def folder(self):
        return self.hash[0]

    @property
    def relative(self):
        return os.path.join(self.folder, '{}.{}'.format(self.hash, self.ext))

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
        hash_str = hasher.hexdigest()
    return hash_str
