import os
import json

from libs.misc import fast_scan

MTIME_STORE_FILENAME = 'mtimes.json'


class FilesetChangeMonitor(object):

    def __init__(self, path, name):
        self.path = path
        self.name = name

    @property
    def files(self):
        return fast_scan(self.path)

    @property
    def mtime(self):
        try:
            return max((f.stats.st_mtime for f in self.files))
        except ValueError:
            return 0

    @property
    def mtime_store_path(self):
        return MTIME_STORE_FILENAME  # os.path.join(self.path, MTIME_STORE_FILENAME)

    @property
    def mtime_store(self):
        if not os.path.exists(self.mtime_store_path):
            return dict()
        with open(self.mtime_store_path, 'rt') as mtime_store_filehandle:
            return json.load(mtime_store_filehandle)
    @mtime_store.setter
    def mtime_store(self, mtime_store):
        with open(self.mtime_store_path, 'wt') as mtime_store_filehandle:
            json.dump(mtime_store, mtime_store_filehandle)

    @property
    def has_changed(self):
        return self.mtime > self.mtime_store.get(self.name, 0)
    @has_changed.setter
    def has_changed(self, changed):
        if changed:
            mtime_store = self.mtime_store
            mtime_store[self.name] = self.mtime
            self.mtime_store = mtime_store
