import os.path
import shutil
import hashlib


class ProcessedFilesManager(object):

    def __init__(self, path):
        self.path = path

    def _factory(self, hashs, ext):
        return ProcessedFile(self.path, hashs, ext)

    def get_image_file(self, source_hash, index):
        return self._factory((source_hash, 'image', str(index)), 'jpg')

    def get_video_file(self, source_hash):
        return self._factory(source_hash, 'mp4')

    def get_preview_file(self, source_hash):
        return self._factory((source_hash, 'preview'), 'mp4')

    def prune_unnneded_files(self, hashset):
        pass


class ProcessedFile(object):
    def __init__(self, path, hashs, ext):
        self.hash = self.gen_string_hash(hashs)
        self.absolute = os.path.abspath(os.path.join(path, '{}.{}'.format(self.hash, ext)))

    def move(self, source_file):
        # m.processed_data[file_type]['hash'] = hashfile()
        # m.processed_data[file_type]['mtime'] = stats().mtime
        # mv filepath -> PATH_PROCESSED/hash.original_ext
        shutil.move(source_file, self.absolute)

    @property
    def exists(self):
        return os.path.exists(self.absolute)

    def gen_string_hash(self, hashs):
        if isinstance(hashs, str):
            hash_str = hashs
        else:
            hasher = hashlib.sha256()
            hasher.update(''.join(sorted(hashs)).encode('utf-8'))
            hash_str = hasher.hexdigest()
        return hash_str
