import os
import json
import time
import re

from libs.misc import fast_scan, freeze

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

    def load(self, name):
        assert name
        filepath = self._filepath(name)

        if os.path.exists(filepath):
            with open(filepath, 'r') as source:
                data = json.load(source)
        else:
            data = {}
        self.meta[name] = MetaFile(name, data)

    def save(self, name):
        filepath = self._filepath(name)
        metafile = self.meta[name]

        # If meta file modifyed since scan - abort
        if os.path.exists(filepath) and os.stat(filepath).mtime > self.timestamp:
            log.warn('Refusing to save changes. %s has been updated by another application', filepath)
            return

        if metafile.has_updated():
            with open(self._filepath(name), 'w') as destination:
                json.dump(metafile.data, destination)

    def get_unmatched_files(self):
        for f in fast_scan(self.path, file_regex=re.compile(r'.*\.json$')):
            if f.file_no_ext not in self.meta:
                yield f


class MetaFile(object):

    def __init__(self, name, data):
        self.name = name
        self.data = data

        self.scan_data = self.data.setdefault('scan', {})
        self.pending_actions = self.data.setdefault('actions', {})
        self.data_hash = freeze(data).__hash__()

    def associate_file_collection(self, file_collection):
        pass

    def has_updated(self):
        return self.data_hash != freeze(self.data).__hash__()
