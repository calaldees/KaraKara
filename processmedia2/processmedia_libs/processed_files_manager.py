
class ProcessedFilesManager(object):

    def __init__(self, path):
        pass

    def move_to_processed(self, filepath, file_type):
        # m.processed_data[file_type]['hash'] = hashfile()
        # m.processed_data[file_type]['mtime'] = stats().mtime
        # mv filepath -> PATH_PROCESSED/hash.original_ext
        pass

    def check_file_exists(self):
        pass

    def prune_unnneded_files(self, hashset):
        pass
