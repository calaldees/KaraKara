import os
import json
import time
import re
from collections import ChainMap

from libs.misc import fast_scan, freeze, file_ext, first

from . import EXTS

import logging
log = logging.getLogger(__name__)


class MetaManager(object):

    def __init__(self, path):
        self.path = path
        self._release_cache()
        os.makedirs(os.path.abspath(path), exist_ok=True)

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
            except json.decoder.JSONDecodeError:
                log.error('Unable to load meta from %s', filepath)
        self.meta[name] = MetaFile(name, data)

    def save(self, name):
        filepath = self._filepath(name)
        metafile = self.meta[name]

        if not metafile.has_updated():
            return

        # If meta file modifyed since scan - abort
        if os.path.exists(filepath) and os.stat(filepath).st_mtime != self._meta_timestamps[name]:
            log.warn('Refusing to save changes. %s has been updated by another application', filepath)
            return

        with open(self._filepath(name), 'w') as destination:
            json.dump(metafile.data, destination)
        self._meta_timestamps[name] = os.stat(filepath).st_mtime

    def delete(self, name):
        os.remove(self._filepath(name))
        del self.meta[name]

    def load_all(self, mtime=None):
        for f in fast_scan(
            self.path,
            search_filter=lambda f: f.name.endswith('.json') and (mtime == None or f.stat().st_mtime >= mtime)
        ):
            self.load(f.file_no_ext)

    def save_all(self):
        for name in self.meta.keys():
            self.save(name)

    @property
    def meta_with_unassociated_files(self):
        """
        These are meta items that have a filecollection matched,
        but that file collection is incomplete, so we have some child files missing
        """
        return (m for m in self.meta.values() if m.unassociated_files)

    @property
    def unmatched_entrys(self):
        """
        Meta datafiles that have no accociated file collection.
        This could mean the source has been deleted, or renamed.
        A good course of action is to check for where they might have moved too
        """
        return (m for m in self.meta.values() if not m.file_collection)

    @property
    def source_hashs(self):
        return filter(None, (m.source_details.get('source_hash') for m in self.meta.values()))


class MetaFile(object):

    SOURCE_HASH_KEY = 'source_hash'

    def __init__(self, name, data):
        self.name = name
        self.data = data

        self.scan_data = self.data.setdefault('scan', {})
        self.pending_actions = self.data.setdefault('actions', [])
        self.source_details = self.data.setdefault('processed', {})
        self.data_hash = freeze(data).__hash__()

        self.file_collection = set()

    def associate_file(self, f):
        self.file_collection.add(f)
        file_data = self.scan_data.setdefault(f.file, {})
        mtime = int(f.stats.st_mtime)

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

        self.pending_actions = list(set(self.pending_actions) | {f.ext})

    def has_updated(self):
        return self.data_hash != freeze(self.data).__hash__()

    @property
    def unassociated_files(self):
        return {
            key: self.scan_data[key]
            for key in (set(self.scan_data.keys()) - {f.file for f in self.file_collection})
        }

    @property
    def source_hash(self):
        return self.source_details.get(self.SOURCE_HASH_KEY)
    @source_hash.setter
    def source_hash(self, value):
        self.source_details[self.SOURCE_HASH_KEY] = value


class FileItemWrapper(object):
    """
    A file data tracked within the dict in MetaFile needs some supporting methods
    Rather than blote the MetaFile object I opted for a separate wrapper for
    this data dict.
    Because this wrapper can alter the underlying dict in memory, there is no need
    for any complex coupling or communication between the object types.
    Some might call me crazy, but until anyone cares enough to assit with a
    code review, this is the way it will stay.
    """
    def __init__(self, source_path):
        self.source_path = source_path

    def wrap_scan_data(self, metafile):
        wrapped_scan_data = tuple(self._wrap_scan_data_item(d) for d in metafile.scan_data.values())
        return {k: self._get_file_for(k, wrapped_scan_data) for k in ('video', 'audio', 'sub', 'image', 'tag')}

    def _wrap_scan_data_item(self, data):
        if not data:
            return {}
        file_no_ext, ext = file_ext(data['relative'])
        return ChainMap(
            dict(
                absolute=os.path.abspath(os.path.join(self.source_path, data['relative'])),
                ext=ext,
                file_no_ext=file_no_ext,
            ),
            # IMPORTANT! Any modification to a chainmap is ALWAYS made to the first dict.
            # We DON'T want any changes to the underlying data from a wrapper
            data,
        )

    def _get_file_for(self, file_type, wrapped_scan_data):
        assert file_type in EXTS.keys(), 'file_type: {0} must be one of {1}'.format(file_type, EXTS.keys())
        exts = EXTS[file_type]
        files_for_type = sorted(
            (v for v in wrapped_scan_data if v['ext'] in exts),
            key=lambda v: exts.index(v['ext']),
            reverse=True
        )
        if len(files_for_type) > 1:
            log.warn('Multiple files for type %s identifyed %s. This may be a mistake. Using only first one', file_type, [f['relative'] for f in files_for_type])
        return first(files_for_type) or {}
