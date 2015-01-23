from collections import defaultdict

from externals.lib.misc import file_scan

import logging
log = logging.getLogger(__name__)

VERSION = "0.0"

print("Detect which tags.txt have been buggered")
help = """
Check the mtime of the latest .bak file.
If the tags.txt file is NEWER than then latest bak then we have pushed the wrong data and have lost info
"""

tag_file = {}
bak_file = defaultdict(int)

for f in file_scan('/Users/allan.callaghan/Applications/KaraKara/files/', file_regex='.*(txt|bak)$', stats=True):
    folder = f.relative.split('/')[0]
    mtime = f.stats.st_mtime
    if 'tags.txt' == f.file:
        tag_file[folder] = mtime
    if '.bak' in f.file:
        if mtime > bak_file[folder]:
            bak_file[folder] = mtime

for folder, mtime in tag_file.items():
    if mtime < bak_file[folder]:
        print(folder)

