import re
import os.path

import yaml

from libs.misc import file_scan, file_extension_regex
from libs.file import FolderStructure


AUDIO_EXTS = ('mp2', 'ogg', 'mp3', 'flac')
VIDEO_EXTS = ('avi', 'mpg', 'mkv', 'rm', 'ogm', 'mp4')
DATA_EXTS = ('yml', 'yaml')

RANKED_EXTS = AUDIO_EXTS + VIDEO_EXTS + DATA_EXTS  # Higher the index of the extension, the higher the file is ranked for processing. The highest ranked file of a set of names in processed
DEFAULT_PRIMARY_FILE_REGEX = file_extension_regex(RANKED_EXTS)
DEFAULT_IGNORE_FILE_REGEX = re.compile(r'0\.mp4|0_generic\.mp4')  # Protection for legacy processed files  (could be removed in once data fully migriated)


# Utils ------------------------------------------------------------------------

def _load_yaml(filename):
    with open(filename, 'rb') as file_handle:
        return yaml.load(file_handle)


# Scan -------------------------------------------------------------------------

def scan(path):
    folder_structure = FolderStructure.factory(path)
    primary_files = locate_primary_files(folder_structure)  # This could be optimised to crawl the FolderStructure rather than doing another separate scan
    location_file_collections(folder_structure, primary_files)

# Scan sections ----------------------------------------------------------------

def locate_primary_files(folder_structure, file_regex=DEFAULT_PRIMARY_FILE_REGEX, ignore_regex=DEFAULT_IGNORE_FILE_REGEX):
    """
    locate stuff
    """
    file_dict = {}

    #for f in file_scan(path, file_regex=file_regex, ignore_regex=ignore_regex, stats=True):
    for f in folder_structure.scan(file_regex=file_regex, ignore_regex=ignore_regex):
        existing = file_dict.get(f.file_no_ext)
        if RANKED_EXTS.index(f.ext) > (RANKED_EXTS.index(existing.ext) if existing else 0):
            file_dict[f.file_no_ext] = f
    return file_dict.values()


def location_file_collections(folder_structure, primary_files):
    for f in primary_files:
        if f.ext in DATA_EXTS:
            pass
            #yield map(lambda data_filename: os.path.join(f.folder, data_filename), load_yaml(f.absolute))
        else:
            pass
