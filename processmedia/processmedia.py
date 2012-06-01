#!/usr/bin/python

import os, re, string, sys
import subprocess, urllib
import json

logs = [sys.stdout]

def log(*s):
	for f in logs:
		try:
			print >>f, "".join(map(unicode, s))
		except:
			pass # out of space, etc

def warn(*s):
	print >>sys.stderr, "processmedia: " + "".join(map(unicode, s))

def die(*s):
	warn(*s)
	sys.exit(1)

def hidden_file_re():
	return re.compile(r'^\..*$')

def media_file_re():
	return re.compile(r'^.*\.(avi|mp3|mp4|mpg|mpeg|mkv|ogg|ogm|ssa|png|jpg|jpeg)$', re.IGNORECASE)

def video_file_re():
	return re.compile(r'^.*\.(avi|mp4|mpg|mpeg|mkv|ogm)$', re.IGNORECASE)

def audio_file_re():
	return re.compile(r'^.*\.(mp3|ogg)$', re.IGNORECASE)

def subtitle_file_re():
	return re.compile(r'^.*\.(ssa)$', re.IGNORECASE)

class JSONFile(dict):
	def __init__(self, path):
		super(JSONFile, self).__init__()
		self.path = path
		self.loaded = False
		self.changed = False 

	def load_hook(self):
		pass
	def save_hook(self):
		pass

	def _load(self):
		try:
			fp = open(self.path, 'r')
			self.clear()
			self.update(json.loads(fp))
			fp.close()
			self.loaded = True
			self.changed = False
		except IOError:
			self.clear()
		self.load_hook()

	def load(self):
		if not self.loaded:
			self._load()

	def _save(self):
		self.save_hook()
		try:
			fp = open(self.path, 'w')
			json.dumps(fp, self)
			fp.close()
			self.changed = False
		except IOError as (errno, strerror):
			warn("unable to write " + self.path + " ({0}): {1}".format(errno, strerror))

	def save(self):
		if self.changed:
			self._save()

	def exists(self):
		return os.path.exists(self.path)

	def __setitem__(self, y, v):
		super(JSONFile, self).__setitem(y, v)
		self.changed = True


class MediaFile:
	def __init__(self, path, metadata=None):
		self.path = path
		self.metadata = metadata
	
	def _size(self):
		return os.stat(self.path).st_size
	def size(self):
		if self.metadata is None:
			return self._size()
		else:
			return self.metadata['size']

	def _mtime(self):
		return int(os.stat(self.path).st_mtime)
	def mtime(self):
		if self.metadata is None:
			return self._mtime()
		else:
			return self.metadata['mtime']

	def exists(self):
		return os.path.exists(self.path) and os.path.isfile(self.path)

	def changed(self):
		if self.metadata is None:
			return True
		else:
			return (self.mtime() != self._mtime()) or (self.size() != self._size())

	def probe(self):
		stat = os.stat(self.path)
		metadata = {
			'mtime': int(stat.st_mtime),
			'size': stat.st_size
		}
		
		raw_probe = subprocess.check_output(['ffprobe', self.path], stderr=subprocess.STDOUT)
		
		raw_duration = re.search(r'^\s*Duration:\s*(\d+):(\d+):(\d+)\.(\d+).*', raw_probe, re.IGNORECASE | re.MULTILINE)
		raw_video = re.search(r'^\s*Stream\s#\d+:\d+(?:\[.*?\])?:\s*Video:\s*(.*?),\s*(.*?),\s*(\d+)x(\d+).*', raw_probe, re.IGNORECASE | re.MULTILINE)

		if raw_duration is not None:
			hours = float(raw_duration.group(1))
			minutes = float(raw_duration.group(2))
			seconds = float(raw_duration.group(3))
			factions = float(raw_duration.group(4))
			length = (hours * 60.0 * 60.0) + (minutes * 60.0) + seconds + factions
			metadata['length'] = length
		
		if raw_video is not None:
			metadata['codec'] = raw_video.group(1)
			metadata['colourspace'] = raw_video.group(2)
			metadata['width'] = raw_video.group(3)
			metadata['height'] = raw_video.group(4)
		
		# FIXME: probe audio for language

		return metadata
	
	def update_if_changed(self):
		if self.changed():
			if self.metadata is None:
				self.metadata = {
					'language': 'unknown',
					'score': 1.0
				}
			self.metadata.update(self.probe())
			return True
		else:
			return False
	
	def is_video(self):
		return (video_file_re().match(self.path) is not None)
	def is_audio(self):
		return (audio_file_re().match(self.path) is not None)
	def is_subtitles(self):
		return (subtitle_file_re().match(self.path) is not None)


class TagList:
	def __init__(self, path):
		self.path = path
		self.data = []
		self.loaded = False
		self.changed = False
	
	def _load(self):
		try:
			fp = open(self.path, 'r')
			lines = fp.readlines()
			fp.close()
			self.data.clear()
			for line in lines:
				tag = line.strip() # FIXME: \r\n?
				self.data.append(tag)
			self.loaded = True
			self.changed = False
		except IOError:
			self.data.clear()

	def load(self):
		if not self.loaded:
			self._load()

	def _save(self):
		try:
			fp = open(self.path, 'w')
			for tag in self.data:
				fp.write(tag + "\r\n")
			fp.close()
			self.changed = False
		except IOError as (errno, strerror):
			warn("unable to write " + self.path + " ({0}): {1}".format(errno, strerror))

	def save(self):
		if self.changed:
			self._save()

	def exists(self):
		return os.path.exists(self.path)
	
	def create(self):
		if not self.exists():
			self._save()

	def items(self):
		return self.data

class MediaDescriptor(JSONFile):
	def __init__(self, parent):
		super(MediaDescriptor, self).__init__(parent.element_path('description.json'))
		self.parent = parent
	
	def save_hook(self):
		self['id'] = parent.name
		self['tags'] = parent.tags.items()
	
	def subtitles(self):
		return self['subtitles']

	def set_subtitles(self, files):
		metadata = []
		for file in files:
			entry = {
				'url': "/".join(['source', urllib.quote(file.name)]),
				'language': file.metadata['language']
			}
			metadata.append(entry)
		self['subtitles'] = metdata

class MediaSources(JSONFile):
	def __init__(self, parent):
		super(MediaSources, self).__init__(parent.element_path('sources.json'))
		self.parent = parent
		self.index = {}

	def load_hook(self):
		self.index.clear()
		for (name, metadata) in self.items():
			self.index[name] = MediaFile(self.parent.element_path('source', name), metadata=metadata)

	def save_hook(self):
		for (name, source) in self.index.items():
			self[name] = source.metadata

	def dir_path(self):
		return parent.element_path('source')
	
	def index(self):
		self.load()

		missing = []
		deleted = []
		changed = []
		
		for name in parent.source_files():
			if not self.index.has_key(name):
				missing.append(name)
			elif not self.index[name].exists():
				deleted.append(name)
			elif self.index[name].changed():
				changed.append(name)

		if (len(missing) + len(deleted) + len(changed)) == 0:
			return False

		for name in deleted:
			self.parent.log("del source: " + name)
			del self.index[name]
		for name in missing:
			self.parent.log("add source: " + name)
			self.index[name] = MediaFile(self.parent.element_path('source', name))
		for (name, source) in self.index.items():
			source.update_if_changed()
		
		self.changed = True
		self.save()

	def subtitles(self):
		files = []
		for (name, source) in self.index.items():
			if source.is_subtitles():
				files.append(name)
		return files

class MediaEncoding(JSONFile):
	def __init__(self, parent):
		super(MediaEncoding, self).__init__(parent.element_path('encoding.json'))
		self.parent = parent


class MediaItem:
	def __init__(self, path):
		self.name = (os.path.split(path))[1]
		self.path = path

		self.descriptor = MediaDescriptor(self)
		self.sources = MediaSources(self)
		self.encoding = MediaEncoding(self)
		self.tags = TagList(self.element_path('tags.txt'))

		self.source_path = self.element_path('source')
		self.preview_path = self.element_path('preview')
		self.thumbnail_path = self.element_path('thumbnail')
		self.video_path = self.element_path('video')
		self.tmp_path = self.element_path('tmp')

		self.hidden_re = hidden_file_re()
		self.media_re = media_file_re()
	
	def log(self, *s):
		log('"' + self.name + '": ', *s)

	def element_path(self, *e):
		return os.path.join(self.path, *e)

	def initialise_sources(self):
		if os.path.exists(self.source_path):
			return
		else:
			media_files = []
			for name in os.listdir(self.path):
				path = os.path.join(self.path, name)
				if (not self.hidden_re.match(name)) and os.isfile(path) and self.media_re.match(name):
					media_files.append(name)

			self.log("mkdir " + self.source_path)
			os.mkdir(self.source_path)
			for name in media_files:
				old_path = os.path.join(self.path, name)
				new_path = os.path.join(self.source_path, name)
				self.log("mv " + old_path + " => " + new_path)
				os.rename(old_path, new_path)
	
	def create_directory(self, name):
		path = self.element_path(name)
		if os.path.exists(path):
			return
		else:
			self.log("mkdir " + path)
			os.mkdir(path)

	def initialise_layout(self):
		self.initialise_sources(self)
		self.create_directory('preview')
		self.create_directory('thumbnail')
		self.create_directory('video')
		self.create_directory('tmp')

	def source_files(self):
		sources = []
		for name in os.listdir(self.source_path):
			path = os.path.join(self.source_path, name)
			if (not self.hidden_re.match(name)) and os.isfile(path) and self.media_re.match(name):
				sources.append(name)
		return sources
	
	def valid(self):
		return True # FIXME: do some testing

	def import_stage(self):
		self.log("import stage")
		self.initialise_layout()
		# FIXME: extract subtitle files
		# FIXME: populate tags

	def index_stage(self):
		self.log("index stage")
		self.sources.index()
		subtitles = self.subtitles()
		self.descriptor.set_subtitles(subtitles)

	def run_stages(self):
		self.log("processing")
		self.import_stage()
		self.index_stage()

def find_items(path):
	hidden_re = hidden_file_re()
	items = []
	for entry in os.listdir(path):
		entry_path = os.path.join(path, entry)
		if not hidden_re.match(name):
			pass
		elif os.path.isdir(entry_path):
			item = MediaItem(entry_path)
			if item.valid():
				items.append(item)
	return items

def prepare_items(path, label=None):
	hidden_re = hidden_file_re()
	media_re = media_file_re()
	
	files = os.listdir(path)
	items = {}

	dir_n = 0
	item_n = 0
	media_n = 0
	rename_n = 0

	for file_name in files:
		file_path = os.path.join(path, file_name)
		if (not hidden_re.match(file_name)) and os.path.isfile(file_path) and media_re.match(file_name):
			(item_name, extension) = os.path.splitext(file_name)
			if label is not None:
				item_name = label + " - " + item_name
			if not items.has_key(item_name):
				items[item_name] = []
			items[item_name].append(file_name)
			media_n += 1

	for (item, files) in items.items():
		item_dir = os.path.join(path, item)
		item_n += 1
		
		if not os.path.exists(item_dir):
			log("mkdir " + item_dir)
			os.mkdir(item_dir)
			dir_n += 1

		for file_name in files:
			old_path = os.path.join(path, file_name)
			new_path = os.path.join(path, item, file_name)
			log("  " + old_path + " => " + new_path)
			os.rename(old_path, new_path)
			rename_n += 1

	log("found {0} media files (from {1} things)".format(media_n, len(files)))
	log("moved {0} files into {1} media items".format(rename_n, item_n))
	log("created {0} directories".format(dir_n))

def probe_test(files):
	for file in files:
		mf = MediaFile(file)
		metadata = mf.probe()
		print metadata

def usage(f):
        print >>f, """Usage:
  processmedia.py <command> ...
 
Where <command> is one of:
  
  process <media-root>
    Scan <media-root> for media items.
    Perform all processing stages on items.

  prepare <media-root> [<label>]
    Gather all similarly name media files in <media-root> into directories.
    This creates media items for processing with the 'process' command.
    If <label> is supplied it is prepended to the name of each item created.

  probe-test <file> [<file> ...]
    Test media probing functionality on file(s).
"""

def main(args):
	if len(args) < 2:
		usage(sys.stderr)
		sys.exit(1)
	else:
		command = args[0]
		root = args[1]
		if command == 'process':
			media = find_items(root)
			for item in media:
				item.run_stages()
		elif command == 'prepare':
			if len(args) > 2:
				prepare_items(root, args[2])
			else:
				prepare_items(root)
		elif command == 'probe-test':
			probe_test(args[1:])
		else:
			usage(sys.stderr)
			sys.exit(1)
			

if __name__ == "__main__":
        main(sys.argv[1:])
