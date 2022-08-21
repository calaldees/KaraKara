import os
import json

from calaldees.data import freeze
from calaldees.files.scan import fast_scan

import logging
log = logging.getLogger(__name__)


class MetaManager(object):

    def __init__(self, path_meta=None):
        assert path_meta
        self.path = path_meta
        self._release_cache()
        os.makedirs(os.path.abspath(self.path), exist_ok=True)

    def _release_cache(self):
        self.meta = {}
        self._meta_timestamps = {}

    def get(self, name):
        return self.meta.get(name)

    def _filepath(self, name):
        return os.path.join(self.path, '{0}.json'.format(name))

    def load(self, name):
        assert name
        if self.meta.get(name):
            return

        filepath = self._filepath(name)
        data = {}
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as source:
                    data = json.load(source)
                self._meta_timestamps[name] = os.stat(filepath).st_mtime
            except json.decoder.JSONDecodeError as ex:
                log.error('Unable to load meta from %s %s', filepath, ex)
        self.meta[name] = MetaFile(name, data)

    def save(self, name):
        filepath = self._filepath(name)
        metafile = self.meta[name]

        if not metafile.has_updated():
            return

        # If meta file modified since scan - abort
        _check_meta_mtime_safety = False  # TODO: this appears to not use `disable_meta_write_safety` in config? Investigate
        if _check_meta_mtime_safety and os.path.exists(filepath):
            mtime_expected = self._meta_timestamps[name]
            mtime_current = os.stat(filepath).st_mtime
            if mtime_current != mtime_expected:
                log.warning(f'Refusing to save changes. {filepath} has been updated by another application. Expected mtime of {mtime_expected} but got {mtime_current}')
                return

        #log.info(f'meta saving {name} - before mtime {os.stat(filepath).st_mtime}')
        with open(self._filepath(name), 'w') as destination:
            json.dump(metafile.data, destination)
        self._meta_timestamps[name] = os.stat(filepath).st_mtime
        log.info(f'meta saved {name} - after mtime {self._meta_timestamps[name]}')

    def delete(self, name):
        try:
            os.remove(self._filepath(name))
        except Exception:
            log.error('Unable to delete missing metafile - How did this happen? {}'.format(self._filepath(name)))
        del self.meta[name]

    def load_all(self):
        for f in self.files:
            self.load(f.file_no_ext)

    def save_all(self):
        for name in self.meta.keys():
            self.save(name)

    @property
    def files(self):
        # wha? (mtime == None or f.stat().st_mtime >= mtime)
        return fast_scan(self.path, search_filter=lambda f: f.endswith('.json'))

    @property
    def source_hashs(self):
        return (m.source_hash for m in self.meta.values())  #  if m.source_hash


class MetaFile(object):

    SOURCE_HASHS_KEY = 'hashs'
    SOURCE_HASH_FULL_KEY = 'full'

    def __init__(self, name, data):
        self.name = name
        self.data = data

        self.scan_data = self.data.setdefault('scan', {})
        self.pending_actions = self.data.setdefault('actions', [])
        self.source_details = self.data.setdefault('source_details', {})
        self.data_hash = freeze(data).__hash__()

        self.file_collection = set()

    def associate_file(self, f):
        self.file_collection.add(f)
        file_data = self.scan_data.setdefault(f.file, {})
        mtime = f.stats.st_mtime

        if file_data.get('relative') == f.relative and file_data.get('mtime') == mtime:
            return

        if file_data.get('mtime') == mtime:
            file_data['relative'] = f.relative
            return

        filehash = str(f.hash)
        if file_data.get('hash') == filehash:
            file_data['relative'] = f.relative
            file_data['mtime'] = mtime
            return

        # Remove any existing entries for this filehash in our previous scan collection
        for k in {k for k, v in self.scan_data.items() if v.get('hash') == filehash}:
            log.info('Removing entry for %s as this hash clashs with new entry %s', k, f.file)
            del self.scan_data[k]

        file_data['relative'] = f.relative
        file_data['mtime'] = mtime
        file_data['hash'] = filehash

        #self.pending_actions = list(set(self.pending_actions) | {f.ext})
        #if self.SOURCE_HASHS_KEY in self.source_details:
        #    log.debug('{} source changed, clearing source hashs'.format(self.name))
        #    del self.source_details[self.SOURCE_HASHS_KEY]

    def has_updated(self):
        return self.data_hash != freeze(self.data).__hash__()

    @property
    def unassociated_files(self):
        return {
            key: self.scan_data[key]
            for key in (set(self.scan_data.keys()) - {f.file for f in self.file_collection})
        }

    def unlink_unassociated_files(self):
        for key, file_data in self.unassociated_files.items():
            log.info('Unlinking {} {}'.format(key, file_data['relative']))
            del self.scan_data[key]
