import re
from libs.misc import file_scan, file_extension_regex


AUDIO_EXTS = ('mp2', 'ogg', 'mp3', 'flac')
VIDEO_EXTS = ('avi', 'mpg', 'mkv', 'rm', 'ogm', 'mp4')
DATA_EXTS = ('yml', 'yaml')

RANKED_EXTS = AUDIO_EXTS + VIDEO_EXTS + DATA_EXTS  # Higher the index of the extension, the higher the file is ranked for processing. The highest ranked file of a set of names in processed
DEFAULT_PRIMARY_FILE_REGEX = file_extension_regex(RANKED_EXTS)
DEFAULT_IGNORE_FILE_REGEX = re.compile(r'0\.mp4|0_generic\.mp4')  # Protection for legacy processed files  (could be removed in once data fully migriated)


def locate_primary_files(path):
    """
    locate stuff
    """
    file_dict = {}

    for f in file_scan(path, file_regex=DEFAULT_PRIMARY_FILE_REGEX, ignore_regex=DEFAULT_IGNORE_FILE_REGEX, stats=True):
        existing = file_dict.get(f.file_no_ext)
        if RANKED_EXTS.index(f.ext) > (RANKED_EXTS.index(existing.ext) if existing else 0):
            file_dict[f.file_no_ext] = f

    return file_dict.values()


def location_file_collections(files):
    for f in files:
        pass
