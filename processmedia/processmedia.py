#!/usr/bin/python

import math, os, re, string, sys
import subprocess, urllib
import cPickle, hashlib
import json

from operator import itemgetter

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

def dictionary_hash(x):
	return hashlib.sha1(cPickle.dumps(x))

def hidden_file_re():
	return re.compile(r'^\..*$')

def media_file_re():
	return re.compile(r'^.*\.(avi|mp3|mp4|mpg|mpeg|mkv|ogg|ogm|ssa|bmp|png|jpg|jpeg)$', re.IGNORECASE)

def video_file_re():
	return re.compile(r'^.*\.(avi|mp4|mpg|mpeg|mkv|ogm)$', re.IGNORECASE)

def audio_file_re():
	return re.compile(r'^.*\.(mp3|ogg)$', re.IGNORECASE)

def image_file_re():
	return re.compile(r'^.*\.(bmp|png|jpg|jpeg)$', re.IGNORECASE)

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

		(dir, name) = os.path.split(path)
		if name is not None:
			self.name = name
		else:
			self.name = path

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
	def is_image(self):
		return (image_file_re().match(self.path) is not None)
	def is_subtitles(self):
		return (subtitle_file_re().match(self.path) is not None)

	def __getitem__(self, y):
		if self.metadata.has_key(y):
			return self.metadata[y]
		else:
			return None

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
	
	def video(self):
		return self['video']
	def set_video(self, name, description):
		self['video'][name] = description
		self.changed = True
	def remove_video(self, name):
		del self['video'][name]
		self.changed = True
	

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

	def video(self):
		return [item for item in self.index.items() if item.is_video()]
	def audio(self):
		return [item for item in self.index.items() if item.is_audio()]
	def image(self):
		return [item for item in self.index.items() if item.is_image()]
	def subtitles(self):
		return [item for item in self.index.items() if item.is_subtitles()]


class MediaEncoding(JSONFile):
	def __init__(self, parent):
		super(MediaEncoding, self).__init__(parent.element_path('encoding.json'))
		self.parent = parent

	def update(self, encodings):
		self.load()

		n = 0
		files = {}
		for encoding in encodings:
			name = "{0}.mp4".format(n)
			files[name] = encoding
			n += 1
		
		changed = False
		for (name, new) in files.items():
			if self.has_key(name):
				old = self[name]
				if old.has_key('audio-shift'):
					new['audio-shift'] = old['audio-shift']
				if old.has_key('subtitle-shift'):
					new['subtitle-shift'] = old['subtitle-shift']
				if dictionary_hash(old) != dictionary_hash(new):
					self.parent.log("update encoding " + name)
					self[name] = new
					changed = True
			else:
				self.parent.log("add encoding " + name)
				self[name] = new
				changed = True
		to_remove = []
		for (name, old) in self.items():
			if not files.has_key(name):
				to_remove.append(name)
				changed = True
		for name in to_remove:
			self.parent.log("remove encoding " + name)
			del self[name]

		if changed:
			self.save()


class MediaEncoder:
	def __init__(self, parent, path):
		self.path = path
		self.parent = parent

		self.video = None
		self.image = None
		self.audio = None
		self.audio_shift = 0.0
		self.subtitles = None
		self.subtitle_shift = 0.0
		
		self.base_width = 1024
		self.base_height = 768

	def valid(self):
		type_4 = ((self.image is not None) and (self.audio is not None) and (self.subtitle is not None))
		type_3 = ((self.video is not None) and (self.audio is not None) and (self.subtitle is not None))
		type_2 = ((self.video is not None) and (self.subtitle is not None))
		type_1 = (self.video is not None)
		return type_1 or type_2 or type_3 or type_4

	def filebase(self):
		(dirname, filename) = os.path.split(self.path)
		(filebase, ext) = os.path.splitext(filename)
		return filebase
	
	def temp_file(self, name):
		return os.join(self.parent.temp_path, self.filebase() + '_' + name)

	def probe_media(self):
		if self.video is not None:
			v_source = self.video
		elif self.image is not None:
			v_source = self.image
		if self.audio is not None:
			a_source = self.audio
		else:
			a_source = self.video

		output_width = self.base_width
		output_height = self.base_height
		output_border = 0

		v_media = MediaFile(v_source)
		v_metadata = source_media.probe()
		aspect = 0.75
		length = 0.0
		
		if v_metadata is not None:
			width = v_metadata['width']
			height = v_metadata['height']
			if width > 0.0 and height > 0.0:
				aspect = height / width
			length = v_metadata['length'] 

		if aspect <= 0.75:
			output_height = output_width * aspect
		else:
			output_width = math.floor(output_height / aspect)
			output_border = math.floor((base_width - output_width) / 2.0)
			output_width += base_width - (output_width + (output_border * 2.0))

		self.width = output_width
		self.height = output_height
		self.border = output_border
		self.length = length

		if not a_source:
			return

		a_media = MediaFile(a_source)
		a_metadata = a_media.probe()

		if a_metadata is not None:
			if (length == 0.0) or (a_metadata['length'] < length):
				length = a_metadata['length']

		self.length = length

	def _clean_files(self, files):
		for file_path in files:
			(path_head, path_tail) = os.path.split(file_path)
			path = os.path.join(self.parent.temp_path, path_tail)
			if os.path.samefile(path, file_path):
				os.unlink(file_path)

	def _run_cmd(self, cmd, success, fail, label):
		try:
			self.parent.log(" ".join(cmd))
			ok = subprocess.check_call(cmd)
			if ok == 0:
				return success
			else:
				self.parent.log(label + " failed")
				return fail
		except subprocess.CalledProcessError as error:
			self.parent.log(label + " failed - " + error)
			return fail

	def encode_video(self):
		if self.video is not None:
			source = self.video
		elif self.image is not None:
			source = self.temp_file('imagery.avi')
			parameters = [
				'avconv',
				'-y', 
				'-loop', '1', 
				'-i', self.image,
				'-r', '24',
				'-t', str(self.length),
				source
			]
			result = self._run_cmd(parameters, True, None, "image to video conversation")
			if result is None:
				return None
		else:
			return None

		filters = [ 'ass', 'scale={0}:{1}'.format(self.width, self.height) ]
		if self.border >= 0.0:
			filters = [ 'expand={0}:{1}:{2}'.format(self.base_width, self.height) ]

		temp_video = self.temp_file('video.mp4')
		parameters = [
			'mencoder',
			source,
			'-ass',
			'-ovc', 'x264',
			'-oac', 'none',
			'-o', temp_video,
			'-vf', ",".join(filters)
		]
		
		if self.subtitles is not None:
			parameters += ['-sub', self.subtitles]
			parameters += ['-subdelay', self.subtitle_shift]
		
		result = self._run_cmd(parameters, temp_video, None, "video encoding")
		if source != self.video:
			self._clean_files([source])
		return result

	def encode_audio():
		if self.audio is not None:
			source = self.audio
		else:
			source = self.video

		temp_audio = self.temp_file('audio.aac')
		parameters = [
			'avconv',
			'-y',
			'-i', source,
			'-vcodec', 'none',
			'-strict', 'experimental',
			temp_audio
		]
		
		return self._run_cmd(parameters, temp_audio, None, "audio encoding")

	def mux(self, video, audio):
		parameters = [
			'avconv',
			'-y',
			'-i', video,
			'-vcodec', 'copy',
			'-vcodec', 'none',
			'-i', audio,
			'-vcodec', 'none',
			'-acodec', 'copy',
			self.path
		]
		return self._run_cmd(parameters, True, False, "a/v muxing")

	def run(self):
		if not self.valid():
			return False

		# setup width, height and duration
		self.probe_media()
		# encode video stream with hard subtitles
		video = self.encode_video()
		if video is None:
			return False
		# encode audio stream
		audio = self.encode_audio()
		if audio is None:
			return False
		# mux video and audio
		result = self.mux(video, audio)
		self._clean_files([video, audio])
		
		return result

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
		self.temp_path = self.element_path('tmp')

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
		# FIXME: only save if changed
		self.descriptor.set_subtitles(subtitles)
		self.descriptor.save()

	def select_highest_quality(self, files, language=None):
		if language is not None:
			matching_files = [file for file in files if file['language'] == language]
			unknown_files = [file for file in files if file['language'] == 'unknown']
			if len(matching_files) > 0:
				files = matching_files
			elif len(unknown_files) > 0:
				files = unknown_files
				
		if len(files) > 0:
			sorted_files = sorted(files, key='quality', reverse=True)
			return sorted_files[0]
		else:
			return None
	
	def sort_languages(self, languages):
		priority = { 'ja': 0, 'en': 1, 'unknown': 9000 }
		results = {}
		p_n = 10
		
		for lang in languages:
			if priority.has_key(lang):
				results[lang] = priority[lang]
			else:
				results[lang] = p_n
				p_n += 1

		return map(itemgetter(0), sorted(results.items(), key=itemgetter(1)))

	def pick_and_mix_stage(self):
		self.log("pick-and-mix stage")
		
		video_files = self.sources.video()
		audio_files = self.sources.audio()
		image_files = self.sources.image()
		subtitle_files = self.sources.subtitles()
		
		languages = {}
		for subtitles in subtitle_files:
			language = subtitles['language']
			if not languages.has_key(lang):
				languages[lang] = []
			languages[lang].append(subtitles)

		encodings = []
		if (len(languages) == 0) and (len(video_files) > 0):
			encodings.append({
				'video': self.select_highest_quality(video_files),
				'language': 'unknown'
			})
		elif len(languages) > 0:
			for lang in self.sort_languages(languages.keys()):
				subtitles = self.select_highest_quality(subtitle_files, language=lang)
				video = self.select_highest_quality(video_files, language=lang)
				audio = self.select_highest_quality(audio_files, language=lang)
				image = self.select_highest_quality(image_files)

				encoding = {
					'subtitles': subtitles.name,
					'subtitle-shift': 0.0,
					'language': lang
				}
				if video is not None:
					encoding['video'] = video.name
				elif image is not None:
					encoding['image'] = image.name

				if audio is not None:
					encoding['audio'] = audio.name
					encoding['audio-shift'] = 0.0

				encodings.append(encoding)

		self.encodings.update(encodings)

	def encode_stage(self):
		self.log("encode stage")

		encodings = {}
		for (name, encoding) in self.encodings.items():
			expanded = dict(encoding)
			for key in ['video', 'audio', 'image', 'subtitle']:
				if encoding.has_key(key):
					expanded[key + '-metadata'] = self.sources[encoding[key]]
			expanded['encode-hash'] = dictionary_hash(expanded)
			encodings[name] = expanded

		added = []
		updated = []
		removed = []

		video = self.descriptor.video
		
		for (name, encoding) in encodings.items():
			if video.has_key(name):
				if video[name]['encode-hash'] != encoding['encode-hash']:
					changed.append(name)
				elif not os.path.exists(self.element_path('video', name)):
					changed.append(name)
			else:
				added.append(name)
		for (name, description) in video.items():
			if not encodings.has_key(name):
				removed.append(name)

		if (len(added) + len(updated) + len(removed)) == 0:
			self.log("nothing to encode")
			return

		for name in removed:
			path = self.element_path('video', name)
			self.log("rm " + path)
			try:
				os.remove(path)
			except OSError as (errno, strerror):
				self.log("unable to remove " + path + " ({0}): {1}".format(errno, strerror))
			self.descriptor.remove_video(name)

		self.descriptor.save()

		for name in (added + removed):
			self.log("encoding " + name)
			encoding = encodings[name]
			
			ok = True
			path = self.element_path('video', name)
			if os.path.exists(path):
				try:
					self.log("rm " + path)
					os.remove(path)
				except OSError as (errno, strerror):
					self.log("unable to remove " + path + " ({0}): {1}".format(errno, strerror))
					ok = False

			if ok:
				encoder = MediaEncoder(self, self.element_path('video', name))
				if encoding.has_key('video'):
					encoder.video = self.element_path('source', encoding['video'])
				elif encoding.has_key('image'):
					encoder.image = self.element_path('source', encoding['image'])
				if encoding.has_key('audio'):
					encoder.audio = self.element_path('source', encoding['audio'])
					encoder.audio_shift = encoding['audio-shift']
				if encoding.has_key('subtitles'):
					encoder.subtitles = self.element_path('source', encoding['subtitles'])
					encoder.subtitle_shift = encoding['subtitle-shift']
				ok = encoder.run()
			
			if ok:
				self.log("  complete")
				media = MediaFile(path)
				metadata = media.probe()
				metadata['url'] = "/".join(['video', urllib.quote(name)]),
				metadata['src'] = name
				metadata['encode-hash'] = encoding['encode-hash']
				metadata['language'] = encoding['language']
				self.descriptor.set_video(name, metadata)
			else:
				self.log("  failed")
				self.descriptor.remove_video(name)

			self.descriptor.save()

	def run_stages(self):
		self.log("processing")
		self.import_stage()
		self.index_stage()
		self.pick_and_mix_stage()
		self.encode_stage()

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
