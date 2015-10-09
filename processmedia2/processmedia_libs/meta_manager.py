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
        os.makedirs(os.path.abspath(path), exist_ok=True)

    def get(self, name):
        return self.meta.get(name)

    def _filepath(self, name):
        return os.path.join(self.path, '{0}.json'.format(name))

    def load(self, name):
        assert name
        filepath = self._filepath(name)

        data = {}
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as source:
                    data = json.load(source)
            except json.decoder.JSONDecodeError:
                log.error('Unable to load meta from %s', filepath)
        self.meta[name] = MetaFile(name, data)

    def save(self, name):
        filepath = self._filepath(name)
        metafile = self.meta[name]

        if not metafile.has_updated():
            return

        # If meta file modifyed since scan - abort
        if os.path.exists(filepath) and os.stat(filepath).st_mtime > self.timestamp:
            log.warn('Refusing to save changes. %s has been updated by another application', filepath)
            return

        with open(self._filepath(name), 'w') as destination:
            json.dump(metafile.data, destination)

    def load_all(self):
        for f in fast_scan(self.path, file_regex=re.compile(r'.*\.json$')):
            self.load(f.file_no_ext)

    def save_all(self):
        for name in self.meta.keys():
            self.save(name)

    @property
    def unmatched(self):
        return {k: m for k, m in self.meta.items() if not m.file_collection}

    @property
    def unaccounted(self):
        return {k: m.unacounted for k, m in self.meta.items()}


class MetaFile(object):

    def __init__(self, name, data):
        self.name = name
        self.data = data

        self.scan_data = self.data.setdefault('scan', {})
        self.pending_actions = self.data.setdefault('actions', [])
        self.data_hash = freeze(data).__hash__()

        self.file_collection = ()

    def associate_file_collection(self, file_collection):
        self.file_collection = file_collection
        for f in file_collection:
            current = self.scan_data.setdefault(f.file, {})
            mtime = int(f.stats.st_mtime)
            if current.get('mtime') == mtime:
                continue
            current['mtime'] = mtime
            filehash = str(f.hash)
            if current.get('hash') == filehash:
                continue
            current['hash'] = filehash
            self.pending_actions.append(f.ext)

    def has_updated(self):
        return self.data_hash != freeze(self.data).__hash__()

    @property
    def unacounted(self):
        return {
            key: self.scan_data[key]
            for key in (set(self.scan_data.keys()) - {f.file for f in self.file_collection})
        }
