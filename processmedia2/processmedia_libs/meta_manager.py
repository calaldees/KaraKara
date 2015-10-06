import os
import json
import time
import re

from libs.misc import fast_scan

import logging
log = logging.getLogger(__name__)


class MetaManager(object):

    def __init__(self, path):
        self.path = path
        self.meta = {}
        self.timestamp = time.time()

    def get(self, name):
        return self.meta.get(name)

    def _filepath(self, name):
        return os.path.join(self.path, '{0}.json'.format(name))

    def load(self, name, file_collection):
        assert name
        assert file_collection
        filepath = self._filepath(name)

        if os.path.exists(filepath):
            with open(filepath, 'r') as source:
                data = json.load(source)
        else:
            data = {}
        self.meta[name] = MetaFile(name, data, file_collection)

    def save(self, name):
        filepath = self._filepath(name)
        metafile = self.meta[name]
        if os.stat(filepath).mtime > self.timestamp:
            log.warn('Refusing to save changes. %s has been updated by another application', filepath)
            return
        if metafile.has_updated():
            with open(self._filepath(name), 'w') as destination:
                json.dump(metafile.data, destination)

    def get_unmatched_files(self):
        for f in fast_scan(self.path, file_regex=re.compile(r'.*\.json$')):
            if f.file_no_ext not in self.meta:\
                yield f


class MetaFile(object):

    def __init__(self, name, data, file_collection=None):
        self.name = name
        self.data = data
        self.file_collection = file_collection

    def has_updated(self):
        return False
