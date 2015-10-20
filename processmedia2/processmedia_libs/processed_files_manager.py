import os.path
import shutil

class ProcessedFilesManager(object):

    def __init__(self, path):
        self.path = path

    def factory(self, hashs, ext):
        return ProcessedFile(self.path, hashs, ext)

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
        hash_str = str(frozenset(hashs).__hash__())
        if hash_str.startswith('-'):
            hash_str = hash_str.strip('-')+'x'
        return hash_str
