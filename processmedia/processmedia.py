#!/usr/bin/python

import os, re, string, sys
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


class JSONFile(dict):
	def __init__(self, path):
		super(JSONFile, self).__init__()
		self.path = path
		self.loaded = False
		self.changed = False 

	def load(self):
		try:
			fp = open(self.path, 'r')
			self.clear()
			self.update(json.loads(fp))
			fp.close()
			self.loaded = True
			self.changed = False
		except IOError:
			self.clear()

	def save(self):
		try:
			fp = open(self.path, 'w')
			json.dumps(fp, self)
			fp.close()
			self.changed = False
		except IOError as (errno, strerror):
			warn("unable to write " + self.path + " ({0}): {1}".format(errno, strerror))
	
	def exists(self):
		return os.path.exists(self.path)

	def __getitem__(self, y):
		if not self.loaded:
			self.load()
		return super(JSONFile, self).__getitem__(y)
	def __setitem__(self, y, v):
		super(JSONFile, self).__setitem(y, v)
		self.changed = True


class MediaDescriptor(JSONFile):
	def __init__(self, path):
		super(MediaDescriptor, self).__init__(path)


class MediaSources(JSONFile):
	def __init__(self, path):
		super(MediaSources, self).__init__(path)


class MediaEncoding(JSONFile):
	def __init__(self, path):
		super(MediaEncoding, self).__init__(path)


class TagList:
	def __init__(self, path):
		self.path = path
		self.data = []
		self.loaded = False
		self.changed = False
	
	def load(self):
		try:
			fp = open(self.path, 'r')
			lines = fp.readlines()
			fp.close()
			self.data.clear()
			for line in lines:
				tag = line.strip() # FIXME: \r\n?
				self.data.add(tag)
			self.loaded = True
			self.changed = False
		except IOError:
			self.data.clear()

	def save(self):
		try:
			fp = open(self.path, 'w')
			for tag in self.data:
				fp.write(tag + "\r\n")
			fp.close()
			self.changed = False
		except IOError as (errno, strerror):
			warn("unable to write " + self.path + " ({0}): {1}".format(errno, strerror))
	
	def exists(self):
		return os.path.exists(self.path)
	
	def create(self):
		if not self.exists():
			self.save()


class MediaItem:
	def __init__(self, path):
		self.name = (os.path.split(path))[1]
		self.path = path

		self.descriptor = MediaDescriptor(self.element_path('description.json'))
		self.sources = MediaSources(self.element_path('sources.json'))
		self.encoding = MediaEncoding(self.element_path('encoding.json'))
		self.tags = TagList(self.element_path('tags.txt'))

		self.source_path = self.element_path('source')
		self.preview_path = self.element_path('preview')
		self.thumbnail_path = self.element_path('thumbnail')
		self.video_path = self.element_path('video')

		self.hidden_re = re.compile(r'^\.')
		self.media_re = re.compile(r'\.(avi|mp3|mp4|mkv|ogg|png|jpg|jpeg)$', re.IGNORECASE)
	
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
					media_files.add(name)

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

	def source_files(self):
		sources = []
		for name in os.listdir(self.source_path):
			path = os.path.join(self.source_path, name)
			if (not self.hidden_re.match(name)) and os.isfile(path) and self.media_re.match(name):
				sources.add(name)
		return sources
	
	def valid(self):
		return True # FIXME: do some testing

	def stage_import(self):
		self.log("import stage")

	def run_stages(self):
		self.log("processing")
		self.stage_import()

def find_items(path):
	hidden_re = re.compile(r'^\.')
	items = []
	for entry in os.listdir(path):
		entry_path = os.path.join(path, entry)
		if not hidden_re.match(name):
			pass
		elif os.path.isdir(entry_path):
			item = MediaItem(entry_path)
			if item.valid():
				items.add(item)
	return items

def usage(f):
        print >>f, """Usage:
  processmedia.py <media-root>
"""

def main(args):
	if args == []:
		usage(sys.stderr)
		sys.exit(1)
	else:
		root = args[0]
		media = find_items(root)
		for item in media:
			item.run_stages()

if __name__ == "__main__":
        main(sys.argv[1:])
