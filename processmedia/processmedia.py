#!/usr/bin/python

import math, fcntl, os, re, string, sys, time
import subprocess, urllib
import hashlib
import json

from operator import itemgetter, attrgetter

avconv_loglevel = 'warning'
avconv_threads = '1'
logs = [sys.stdout]

def log(*s):
	for f in logs:
		try:
			print >>f, "".join(map(unicode, s))
		except:
			pass # out of space, etc

def log_add(filename):
	global logs
	try:
		fp = open(filename, 'a')
		logs.append(fp)
	except IOError as (errno, strerror):
		warn("unable to add log file " + filename + " ({0}): {1}".format(errno, strerror))	

def warn(*s):
	print >>sys.stderr, "processmedia: " + "".join(map(unicode, s))

def die(*s):
	warn(*s)
	sys.exit(1)

def list_hash(x):
	return hashlib.sha1(json.dumps(x)).hexdigest()

def dictionary_hash(x):
	l = [ (k, x[k]) for k in sorted(x.keys()) ]
	h = hashlib.sha1(json.dumps(l))
	return h.hexdigest()

def time_string(t=None):
	if not t:
		t = time.localtime()
	return time.strftime("%Y-%m-%d %H:%M:%S", t)

def hidden_file_re():
	return re.compile(r'^\..*$')

def media_file_re():
	return re.compile(r'^.*\.(avi|aac|mp3|mp4|mpg|mpeg|mkv|ogg|ogm|rm|wav|wmv|ass|ssa|bmp|png|jpg|jpeg)$', re.IGNORECASE)

def video_file_re():
	return re.compile(r'^.*\.(avi|mp4|mpg|mpeg|mkv|rm|ogm|wmv)$', re.IGNORECASE)

def audio_file_re():
	return re.compile(r'^.*\.(aac|mp3|ogg|wav)$', re.IGNORECASE)

def image_file_re():
	return re.compile(r'^.*\.(bmp|png|jpg|jpeg)$', re.IGNORECASE)

def subtitle_file_re():
	return re.compile(r'^.*\.(ass|ssa)$', re.IGNORECASE)

def avlib_safe_path(path):
	# avconv does not correctly handle percentage signs in image paths
	if image_file_re().match(path):
		return re.subn(r'%', '%%', path)[0]
	else:
		return path

def parse_timestamp(ts):
	ts_match = re.search(r'(\d+):(\d+):(\d+)\.(\d+)', ts)
	if ts_match:
		hours = float(ts_match.group(1)) * 60.0 * 60.0
		minutes = float(ts_match.group(2)) * 60.0
		seconds = float(ts_match.group(3))
		fraction = ts_match.group(4)
		fraction = float(fraction) / (10**(len(fraction)))
		#print ts, hours, minutes, seconds, fraction, (hours + minutes + seconds + fraction)
		return hours + minutes + seconds + fraction
	else:
		return 0.0

def run_command(cmd, label="", log_object=None, success=True, fail=False):
	def do_log(msg):
		if log_object:
			log_object.log(msg)
		else:
			log(msg)

	try:
		cmd = map(unicode, cmd)
		do_log('+++ ' + " ".join(cmd))
		output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
		if output:
			do_log("---\n" + output + "---")
		return success
	except subprocess.CalledProcessError as error:
		do_log(error.output)
		if label:
			do_log(label + " failed - " + unicode(error))
		else:
			do_log.log(unicode(error))
		return fail

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
		self.clear()

		if os.path.exists(self.path):
			try:
				fp = open(self.path, 'rb')
				data = json.load(fp)
				fp.close()
				super(JSONFile, self).update(data)
			except IOError as (errno, strerror):
				warn("unable to read " + self.path + " ({0}): {1}".format(errno, strerror))
			except ValueError as strerror:
				warn("unable to read JSON from " + self.path + ": " + strerror)

		self.loaded = True
		self.changed = False
		self.load_hook()

	def load(self):
		if (not self.loaded) and (not self.changed):
			self._load()

	def _save(self):
		self.save_hook()
		try:
			fp = open(self.path, 'wb')
			json.dump(self, fp, sort_keys=True, indent=4)
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
		super(JSONFile, self).__setitem__(y, v)
		self.changed = True

class SSAFile:
	def __init__(self, path):
		self.path = path
		self.data = []
		self.titles = []
		self.load()

	def load(self):
		self.data[:] = []
		try:
			fp = open(self.path, 'r')
			lines = fp.readlines()
			fp.close()
			for line in lines:
				try:
					line = line.decode('utf-8')
				except UnicodeDecodeError:
					line = line.decode('latin-1')
				self.data.append(line.strip())
		except IOError:
			self.data.clear()

		self.parse()
	
	def save(self, path):
		try:
			fp = open(path, 'w')
			for line in self.data:
				fp.write(line + "\r\n")
			fp.close()
			return True
		except IOError as (errno, strerror):
			warn("unable to write " + self.path + " ({0}): {1}".format(errno, strerror))
			return False

	def parse(self):
		dialogue_re = re.compile(r'^Dialogue:\s*(.*)')
		self.titles[:] = []
		for line in self.data:
			dialogue = dialogue_re.match(line)
			if dialogue:
				parts = dialogue.group(1).split(',', 10)
				if len(parts) == 10:
					start = parse_timestamp(parts[1])
					end = parse_timestamp(parts[2])
					text = parts[9]
					self.titles.append((start, end, text))
	
	def play_res(self):
		res_x = None
		res_y = None

		res_re = re.compile(r'^PlayRes(X|Y):\s*(\d+).*', re.IGNORECASE)
		for line in self.data:
			m = res_re.match(line)
			if m:
				x_y = m.group(1)
				res = int(m.group(2))
				if x_y.lower() == 'x':
					res_x = res
				else:
					res_y = res
		
		return (res_x, res_y)
	
	def calculate_play_res(self, display_x, display_y):
		(res_x, res_y) = self.play_res()
		if res_x and res_y:
			return (res_x, res_y)
		elif res_x:
			return (res_x, int(res_x * (float(display_y) / float(display_x))))
		elif res_y:
			return (int(res_y * (float(display_x) / float(display_y))), res_y)
		else:
			return (display_x, display_y)

	def rewrite_play_res(self, res_x, res_y):
		script_type_re = re.compile(r'^ScriptType:\s*v\d+.*', re.IGNORECASE)
		res_re = re.compile(r'^PlayRes(X|Y):\s*(\d+).*', re.IGNORECASE)
		
		script_pos = None
		to_delete = []

		for (n, line) in enumerate(self.data):
			if script_type_re.match(line):
				script_pos = n
			elif res_re.match(line):
				to_delete.append(n)

		if not script_pos:
			return False

		to_delete.reverse()
		for n in to_delete:
			del self.data[n]

		self.data.insert(script_pos + 1, "PlayResX: {0}".format(res_x))
		self.data.insert(script_pos + 2, "PlayResY: {0}".format(res_y))

		return True
	
	def raw_lines(self):
		lines = []
		for (start, end, text) in sorted(self.titles, key=itemgetter(0)):
			lines.append(text)
		return lines
	
	def dedup_lines(self, src_lines):
		src_lines.reverse()
		lines = []
		previous = []
		for line in src_lines:
			line = line.strip()
			parts = re.split("\n", line)
			for (n, p) in enumerate(parts):
				if p.strip().lower() in previous:
					parts[n] = None
			parts = [ p.strip() for p in parts if p ]
			previous = [ p.lower() for p in parts ]
			line = "\n".join(parts)
			lines.append(line)
		lines.reverse()
		return lines

	def clean_lines(self, dedup=True):
		lines = []
		previous = []
		for line in self.raw_lines():
			(line, n) = re.subn(r'({.*?})', '', line)
			(line, n) = re.subn(r'(\s+)', ' ', line)
			(line, n) = re.subn(r'(\\N)', "\n", line, flags=re.IGNORECASE)
			lines.append(line)
		if dedup:
			return self.dedup_lines(lines)
		else:
			return lines

	def length(self):
		max_end = 0.0
		for (start, end, text) in self.titles:
			if end > max_end:
				max_end = end
		return max_end
	
	def lang_ratio(self, match_words):
		r = 0.0
		for (start, end, text) in self.titles:
			words = re.split(r'\s+', text.lower())
			r += float(sum([ 1 for word in words if match_words.has_key(word) ])) / float(len(words))
		return r

	def jpn_ratio(self):
		match_words = {}
		for m in [ 'wa', 'no', 'yo', 'da', 'ni', 'ga', 'wo', 'kare', 'koi', 'ai' ]:
			match_words[m] = True
		return self.lang_ratio(match_words)
	
	def eng_ratio(self):
		match_words = {}
		for m in [ 'the', 'a', 'on', 'i', 'you', 'he', 'she', 'is', 'yes', 'no' ]:
			match_words[m] = True
		return self.lang_ratio(match_words)

	def guess_language(self):
		ratios = {
			'jpn': self.jpn_ratio(),
			'eng': self.eng_ratio()
		}
		langs = sorted(ratios.keys(), key=lambda x:ratios[x], reverse=True)
		if ratios[langs[0]] < 0.1:
			return 'und'
		else:
			return langs[0]


class MediaFile:
	def __init__(self, path, metadata=None):
		self.path = path
		self.metadata = metadata
		self.log = None

		(dir, name) = os.path.split(path)
		if name:
			self.name = name
		else:
			self.name = path

	def unlink(self):
		if self.exists():
			try:
				os.remove(self.path)
			except OSError as (errno, strerror):
				self.log("unable to remove " + self.path + " ({0}): {1}".format(errno, strerror))

	def _size(self):
		try:
			return long(os.stat(self.path).st_size)
		except:
			return 0
	def size(self):
		if self.metadata and self.metadata.has_key('size'):
			return self.metadata['size']
		else:
			return self._size()

	def _mtime(self):
		try:
			return int(os.stat(self.path).st_mtime)
		except:
			return 0
	def mtime(self):
		if self.metadata and self.metadata.has_key('mtime'):
			return self.metadata['mtime']
		else:
			return self._mtime()

	def exists(self):
		return os.path.exists(self.path) and os.path.isfile(self.path)

	def valid(self):
		return (self.exists() and (self.metadata is not None))

	def has_changed(self):
		if self.metadata and self.metadata.has_key('mtime') and self.metadata.has_key('size'):
			return (self.mtime() != self._mtime()) or (self.size() != self._size())
		else:
			return True

	def calculate_aspect(self, width, height):
		if width >= height:
			reverse = False
		else:
			(width, height) = (height, width)
			reverse = True

		pure_ratio = float(width) / float(height)
		ratio = math.floor(pure_ratio * 10.0) / 10.0
		
		if ratio == 1.0:
			result = [1, 1]
		elif ratio == 1.3:
			result = [4, 3]
		elif ratio == 1.5:
			result = [3, 2]
		elif ratio == 1.6:
			result = [5, 2]
		elif (ratio == 1.7) or (ratio == 1.8):
			result = [16, 9]
		else:
			result = [float("%.2f" % pure_ratio), 1.0]

		if reverse:
			result.reverse()

		return result

	def sanitise_aspect(self, aspect):
		return self.calculate_aspect(aspect[0], aspect[1])

	def subfile(self):
		return SSAFile(self.path)

	def probe(self):
		try:
			stat = os.stat(self.path)
		except:
			return None

		metadata = {
			'mtime': int(stat.st_mtime),
			'size': long(stat.st_size)
		}
		
		try:
			raw_probe = subprocess.check_output(['avprobe', avlib_safe_path(self.path)], stderr=subprocess.STDOUT)
		except subprocess.CalledProcessError:
			return None
		
		raw_duration = re.search(r'^\s*Duration:\s*(\d+):(\d+):(\d+)\.(\d+).*', raw_probe, re.IGNORECASE | re.MULTILINE)
		raw_bitrate = re.search(r',\s*bitrate:\s*(\d+)\s*kb/s', raw_probe, re.IGNORECASE | re.MULTILINE)
		raw_video = re.search(r'^\s*Stream\s*#\d+[:.]\d+(?:\[.*?\])?(?:\(.*?\))?:\s*Video:\s*(.*)', raw_probe, re.IGNORECASE | re.MULTILINE)
		raw_video_lang = re.search(r'^\s*Stream\s*#\d+[:.]\d+\((.+)\):\s*Video', raw_probe, re.IGNORECASE | re.MULTILINE)
		raw_audio = re.search(r'^\s*Stream\s*#\d+[:.]\d+(?:\[.*?\])?(?:\(.*?\))?:\s*Audio:\s*(.*)', raw_probe, re.IGNORECASE | re.MULTILINE)
		raw_audio_lang = re.search(r'^\s*Stream\s*#\d+[:.]\d+\((.+)\):\s*Audio', raw_probe, re.IGNORECASE | re.MULTILINE)

		if raw_duration:
			hours = float(raw_duration.group(1)) * 60.0 * 60.0
			minutes = float(raw_duration.group(2)) * 60.0
			seconds = float(raw_duration.group(3))
			fraction = raw_duration.group(4)
			fraction = float(fraction) / (10**(len(fraction)))
			metadata['length'] = hours + minutes + seconds + fraction
		
		if raw_bitrate:
			metadata['bitrate'] = int(raw_bitrate.group(1))

		if raw_video:
			data = raw_video.group(1)
			
			parts = re.split(r'\s*,\s*', data)
			wxh = re.search(r'\s*(\d+)x(\d+)', data)
			vbr = re.search(r'(\d+)\s*kb/s', data)
			aspect = re.search(r'PAR\s*(\d+):(\d+)\s*DAR\s*(\d+):(\d+)', data)

			metadata['vcodec'] = parts[0]
			metadata['colourspace'] = parts[1]
			if wxh:
				metadata['width'] = int(wxh.group(1))
				metadata['height'] = int(wxh.group(2))
			if vbr:
				metadata['vbitrate'] = int(vbr.group(1))
			if aspect:
				par = [int(aspect.group(1)), int(aspect.group(2))]
				dar = [int(aspect.group(3)), int(aspect.group(4))]
				metadata['par'] = self.sanitise_aspect(par)
				metadata['dar'] = self.sanitise_aspect(dar)
			elif wxh:
				metadata['par'] = [1, 1]
				metadata['dar'] = self.calculate_aspect(metadata['width'], metadata['height'])

		if raw_video_lang:
			metadata['vlang'] = raw_video_lang.group(1) 

		if raw_audio:
			parts = re.split(r'\s*,\s*', raw_audio.group(1))
			abr = re.findall(r'(\d+)\s*kb/s', raw_audio.group(1))
			metadata['acodec'] = parts[0]
			if abr and len(abr) > 0:
				metadata['abitrate'] = int(abr[0])
		if raw_audio_lang:
			metadata['alang'] = raw_audio_lang.group(1) 
		
		if metadata.has_key('alang'):
			metadata['language'] = metadata['alang']
		elif metadata.has_key('vlang'):
			metadata['language'] = metadata['vlang']

		if self.is_subtitles():
			subfile = self.subfile()
			metadata['length'] = subfile.length()
			metadata['language'] = subfile.guess_language()

		return metadata
	
	def _score(self):
		score = 1.0
		if self.metadata.has_key('width') and self.metadata.has_key('height'):
			score *= float((self.metadata['width'] * self.metadata['height'])) / (640.0 * 480.0)
		#if self.metadata.has_key('vbitrate'):
		#	score *= (self.metadata['vbitrate'] / 1024.0)
		if self.metadata.has_key('abitrate'):
			score *= (self.metadata['abitrate'] / 128.0)
		return float("%.2f" % score)

	def update_if_changed(self):
		if self.has_changed():
			new_metadata = self.probe()

			if not new_metadata:
				self.metadata = None
			elif not self.metadata:
				self.metadata = {'language': 'und'}
				self.metadata.update(new_metadata)
				self.metadata['score'] = self._score()
			else:
				self.metadata.update(new_metadata)
			
			return True
		else:
			return False
	
	def length(self):
		if self.metadata and self.metadata.has_key('length'):
			return float(self.metadata['length'])
		else:
			return 0.0

	def generate_thumbnails(self, times, files, width=-1, height=-1):
		if len(times) != len(files):
			return False
		
		self.update_if_changed()
		
		if not self.valid():
			return False
		if not (self.is_video() or self.is_image()):
			return False
		if self.length() is None:
			return False
		
		result = []
		for (time, path) in zip(times, files):
			if time >= (self.length() - 0.1):
				time = self.length() - 0.1
			if time < 0.0:
				time = 0.0
			
			ok = run_command([
				'avconv',
				'-loglevel', avconv_loglevel,
				'-threads', avconv_threads,
				'-y',
				'-ss', str(time),
				'-i', self.path,
				'-vframes', 1,
				'-an',
				'-vf', 'scale={0}:{1}'.format(int(width), int(height)),
				avlib_safe_path(path)
			], label="thumbnail", log_object=self.log)
			if ok:
				result.append((time, path))

		return result
	
	def is_video(self):
		return bool(video_file_re().match(self.path))
	def is_audio(self):
		return bool(audio_file_re().match(self.path))
	def is_image(self):
		return bool(image_file_re().match(self.path))
	def is_subtitles(self):
		return bool(subtitle_file_re().match(self.path))

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
			self.loaded = True
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
	
	def add(self, tag):
		if tag not in self.data:
			self.data.append(tag)
			self.changed = True
		

class MediaDescriptor(JSONFile):
	def __init__(self, parent):
		super(MediaDescriptor, self).__init__(parent.element_path('description.json'))
		self.parent = parent
		self.elements = ['previews', 'thumbnails', 'subtitles', 'videos']
		self.load_hook()
	
	def load_hook(self):
		for key in self.elements:
			if not self.has_key(key):
				self[key] = []
		self.changed = False

	def save_hook(self):
		if not self.has_key('name'):
			self['name'] = self.parent.name
		self['tags'] = self.parent.tags.items()
		for key in self.elements:
			self[key] = sorted(self[key], key=lambda x:x['name'])
	
	def subtitles(self):
		return self['subtitles']
	def set_subtitles(self, metadata):
		self['subtitles'] = metadata
		self.changed = True
	
	def videos(self):
		return self['videos']
	def add_video(self, description):
		self.remove_video(description['name'])
		self['videos'].append(description)
		self.changed = True
	def remove_video(self, name):
		self['videos'] = [ video for video in self.videos() if video['name'] != name ]
		self.changed = True
	
	def thumbnails(self):
		return self['thumbnails']
	def add_thumbnail(self, description):
		self.remove_thumbnails(name=description['name'])
		self['thumbnails'].append(description)
		self.changed = True
	def remove_thumbnails(self, name=None, video=None):
		if name:
			self['thumbnails'] = [ thumbnail for thumbnail in self.thumbnails() if thumbnail['name'] != name ]
		elif video:
			self['thumbnails'] = [ thumbnail for thumbnail in self.thumbnails() if thumbnail['src'] != video ]
		self.changed = True
	
	def previews(self):
		return self['previews']
	def add_preview(self, description):
		self.remove_previews(name=description['name'])
		self['previews'].append(description)
		self.changed = True
	def remove_previews(self, name=None, video=None):
		if name:
			self['previews'] = [ preview for preview in self.previews() if preview['name'] != name ]
		elif video:
			self['previews'] = [ preview for preview in self.previews() if preview['src'] != video ]
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
	
	def index_files(self):
		self.load()

		missing = []
		deleted = []
		changed = []
		
		for name in self.parent.source_files():
			if not self.index.has_key(name):
				missing.append(name)
		for name in self.index.keys():
			if not self.index[name].exists():
				deleted.append(name)
			elif self.index[name].has_changed():
				changed.append(name)

		if (len(missing) + len(deleted) + len(changed)) == 0:
			return False

		for name in deleted:
			self.parent.log("del source: " + name)
			del self.index[name]
		deleted[:] = []

		for name in missing:
			self.parent.log("add source: " + name)
			self.index[name] = MediaFile(self.parent.element_path('source', name))
		for (name, source) in self.index.items():
			source.update_if_changed()
			if not source.valid():
				deleted.append(name)
		for name in deleted:
			self.parent.log("del invalid source: " + name)
			del self.index[name]
		
		self.changed = True
		self.save()

	def video(self):
		return [item for item in self.index.values() if item.is_video()]
	def audio(self):
		return [item for item in self.index.values() if item.is_audio()]
	def image(self):
		return [item for item in self.index.values() if item.is_image()]
	def subtitles(self):
		return [item for item in self.index.values() if item.is_subtitles()]


class MediaEncoding(JSONFile):
	def __init__(self, parent):
		super(MediaEncoding, self).__init__(parent.element_path('encoding.json'))
		self.parent = parent

	def update(self, encodings):
		self.load()

		files = {}
		for (n, encoding) in enumerate(encodings):
			name = "{0}.mp4".format(n)
			files[name] = encoding
		
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
	PROFILE_IPHONE = 1
	PROFILE_ANDROID = 2
	PROFILE_GENERIC = 3

	profile_names = {
		PROFILE_IPHONE: 'iphone',
		PROFILE_ANDROID: 'android',
		PROFILE_GENERIC: 'generic'
	}
	profile_extensions = {
		PROFILE_IPHONE: '.mp4',
		PROFILE_ANDROID: '.mp4',
		PROFILE_GENERIC: '.mp4'
	}
	profile_parameters = {
		PROFILE_IPHONE: [
			'-vf',		'scale=320:-1',
			#'-r',		'30000/1001',
			'-vcodec',	'libx264',
			'-pre:v',	'libx264-ipod320',
			'-acodec',	'aac',
			'-ac',		'1',
			'-ar',		'48000',
			'-ab',		'64k',
			'-b',		'200k',
			'-bt',		'240k'
		],
		PROFILE_ANDROID: [
			'-vf',		'scale=320:-1',
			'-vcodec', 	'libx264',
			'-profile:v',	'baseline',
			'-acodec', 	'aac',
			'-ac',		'1',
			'-ar', 		'48000',
			'-ab',		'64k',
			'-b',		'200k',
			'-bt',		'240k'
		],
		PROFILE_GENERIC: [
			'-vf',		'scale=320:-1',
			'-r',		'13',
			'-vcodec',	'mpeg4',
			'-acodec',	'aac',
			'-ac',		'1',
			'-ar',		'16000',
			'-ab',		'64k'
		]
	}

	@classmethod
	def profile_id(cls, profile):
		if MediaEncoder.profile_names.has_key(profile):
			return profile
		else:
			for (k, v) in MediaEncoder.profile_names.items():
				if v == profile:
					return k
			return None
	@classmethod
	def profile_name(cls, profile):
		return MediaEncoder.profile_names[profile]
	
	@classmethod
	def profile_extension(cls, profile):
		profile = MediaEncoder.profile_id(profile)
		if MediaEncoder.profile_extensions.has_key(profile):
			return MediaEncoder.profile_extensions[profile]
		else:
			return None
	
	def __init__(self, parent, path):
		self.path = path
		self.parent = parent

		self.video = None
		self.image = None
		self.audio = None
		self.audio_shift = 0.0
		self.subtitles = None
		self.subtitle_shift = 0.0
		self.language = None
		
		self.base_width = 1024
		self.base_height = 768

		self.temp_files = []

	def valid_for_encode(self):
		video = bool(self.video)
		image = bool(self.image)
		audio = bool(self.audio)
		subtitles = bool(self.subtitles)

		type_1 = video and not (image or audio or subtitles)
		type_2 = video and subtitles and not (image or audio)
		type_3 = video and audio and subtitles and not image
		type_4 = image and audio and subtitles and not video
		
		return type_1 or type_2 or type_3 or type_4

	def valid_for_transcode(self):
		return (self.video is not None)

	def filebase(self):
		(dirname, filename) = os.path.split(self.path)
		(filebase, ext) = os.path.splitext(filename)
		return filebase
	
	def temp_file(self, name):
		file_path = os.path.join(self.parent.temp_path, self.filebase() + '_' + name)
		self.temp_files.append(file_path)
		return file_path

	def probe_media(self):
		if self.video:
			v_source = self.video
		elif self.image:
			v_source = self.image
		if self.audio:
			a_source = self.audio
		else:
			a_source = self.video

		output_width = self.base_width
		output_height = self.base_height
		output_border = 0

		v_media = MediaFile(v_source)
		v_metadata = v_media.probe()
		aspect = [4, 3]
		length = 0.0
		
		if v_metadata:
			width = v_metadata['width']
			height = v_metadata['height']
			length = v_metadata['length']

			if v_metadata.has_key('dar'):
				aspect = v_metadata['dar']
				#if aspect[0] == aspect[1]:
				#	aspect = [ width, height ]
			elif width > 0.0 and height > 0.0:
				aspect = [ width, height ]

			aspect = [ float(aspect[0]), float(aspect[1]) ]

			self.original_sub_width = int(height * (aspect[0] / aspect[1]))
			self.original_sub_height = height
			
		if (aspect[1] / aspect[0]) <= 0.75:
			output_height = math.floor((output_width / aspect[0]) * aspect[1])
		else:
			output_width = math.floor((output_height / aspect[1]) * aspect[0])
			output_border = math.floor((self.base_width - output_width) / 2.0)
			output_width += self.base_width - (output_width + (output_border * 2.0))

		self.width = output_width
		self.height = output_height
		self.border = output_border
		self.aspect = aspect
		self.length = length

		if not a_source:
			return

		a_media = MediaFile(a_source)
		a_metadata = a_media.probe()

		if a_metadata:
			if (length == 0.0) or ((a_metadata['length'] + self.audio_shift) > length):
				length = a_metadata['length'] + self.audio_shift

		self.length = length

	def aspect_string(self):
		fractional = [ math.floor(a) != a for a in self.aspect ]
		if True in fractional:
			return "%.5f" % (self.aspect[0] / self.aspect[1])
		else:
			return "%d:%d" % (self.aspect[0], self.aspect[1])
	
	def clean_temp_files(self):
		for file_path in self.temp_files:
			try:
				os.unlink(file_path)
			except:
				pass
		self.temp_files[:] = []

	def _run_cmd(self, cmd, success=True, fail=False, label=None):
		return run_command(cmd, log_object=self.parent, label=label, success=success, fail=fail)

	def encode_video(self):
		if self.video:
			source = self.video
		elif self.image:
			source = self.temp_file('imagery.avi')
			parameters = [
				'avconv',
				'-loglevel', avconv_loglevel,
				'-threads', avconv_threads,
				'-y', 
				'-loop', '1', 
				'-i', self.image,
				'-r', '24',
				'-t', str(self.length),
				'-vf', 'scale={0}:{1}'.format(int(self.base_width), -1),
				avlib_safe_path(source)
			]
			result = self._run_cmd(parameters, True, None, "image to video conversation")
			if not result:
				return None
		else:
			return None

		filters = [ 'ass', 'scale={0}:{1}'.format(int(self.width), int(self.height)) ]
		if self.border >= 0.0:
			filters += [ 'expand={0}:{1}'.format(int(self.base_width), int(self.height)) ]

		temp_video = self.temp_file('video.avi')
		parameters = [
			'mencoder',
			'-quiet',
			source,
			'-ass',
			'-nosound',
			'-aspect', self.aspect_string(),
			'-ovc', 'x264',
			'-x264encopts', 'profile=main:preset=slow',
			'-o', temp_video,
			'-vf', ",".join(filters)
		]
		
		if self.subtitles:
			subpath = self.subtitles
			subfile = MediaFile(subpath).subfile()
			
			(res_x, res_y) = subfile.play_res()
			if (res_x is None) or (res_y is None):
				subpath = self.temp_file('subs.ssa')
				(res_x, res_y) = subfile.calculate_play_res(self.original_sub_width, self.original_sub_height)
				subfile.rewrite_play_res(res_x, res_y)
				if not subfile.save(subpath):
					subpath = self.subtitles
			
			parameters += ['-sub', subpath]
			parameters += ['-subdelay', self.subtitle_shift]
		
		return self._run_cmd(parameters, temp_video, None, "video encoding")

	def encode_audio(self):
		if self.audio:
			source = self.audio
		else:
			source = self.video

		source_parameters = ['-i', source]

		temp_audio = self.temp_file('audio.wav')

		if self.audio_shift > 0.0:
			temp_pad = self.temp_file('audio_pad.wav')
			result = self._run([
				'sox', 
				'-null', temp_pad, 
				'trim', '0', str(self.audio_shift)
			])
			if not result:
				return None
			source_parameters = ['-i', temp_pad] + source_parameters
		elif self.audio_shift < 0.0:
			temp_raw = self.temp_file('audio_raw.wav')
			result = self._run(['avconv', '-threads', avconv_threads, '-y', '-i', avlib_safe_path(source), '-vcodec', 'none', temp_raw])
			if not result:
				return None
			temp_cut = self.temp_file('audio_cut.wav')
			result = self._run([
				'sox', 
				temp_raw, temp_cut, 
				'trim', str(-self.audio_shift), str(self.length)
			])
			if not result:
				return None
			source_parameters = ['-i', avlib_safe_path(temp_cut)]

		parameters = ['avconv', '-threads', '1', '-y', '-loglevel', avconv_loglevel] + source_parameters + [
			'-vcodec', 'none',
			'-strict', 'experimental',
			avlib_safe_path(temp_audio)
		]
		
		return self._run_cmd(parameters, temp_audio, None, "audio encoding")

	def mux(self, video, audio):
		parameters = [
			'avconv',
			'-loglevel', avconv_loglevel,
			'-threads', avconv_threads,
			'-y',
			'-i', avlib_safe_path(video),
			'-i', avlib_safe_path(audio),
			'-strict', 'experimental',
			'-vcodec', 'copy',
		]
		if self.language:
			parameters += [
				'-metadata:s:0', 'language=' + self.language, 
				'-metadata:s:1', 'language=' + self.language 
			]
		if self.aspect:
			parameters += [ '-aspect', self.aspect_string() ]

		muxed = self.temp_file('mux.mp4')
		parameters += [ muxed ]

		ok = self._run_cmd(parameters, True, False, "a/v muxing")
		if ok:
			return self._run_cmd(
				['qt-faststart', muxed, self.path],
				True, False,
				'stream optimising'
			)
		else:
			return False

	def encode(self):
		if not self.valid_for_encode():
			return False

		# setup width, height and duration
		self.probe_media()

		# encode video stream with hard subtitles
		video = self.encode_video()
		if not video:
			self.clean_temp_files()
			return False

		# encode audio stream
		audio = self.encode_audio()
		if not audio:
			self.clean_temp_files()
			return False

		# mux video and audio
		result = self.mux(video, audio)
		self.clean_temp_files()
		
		return result

	def transcode(self, profile, offset=0.0, length=0.0):
		if not self.valid_for_transcode():
			return False
		if profile not in MediaEncoder.profile_names.keys(): 
			return False

		transcode = self.temp_file("transcode" + MediaEncoder.profile_extension(profile))
		
		parameters = [
			'avconv',
			'-loglevel', avconv_loglevel,
			'-threads', avconv_threads,
			'-y',
			'-i', avlib_safe_path(self.video),
		]
		parameters += MediaEncoder.profile_parameters[profile]
		parameters += [
			'-strict', 'experimental',
			transcode
		]
		
		ok = self._run_cmd(parameters, True, False, "transcoding")
		if ok:
			ok = self._run_cmd(
				['qt-faststart', transcode, self.path],
				True, False,
				'stream optimising'
			)
		
		self.clean_temp_files()

		return ok

class MediaItem:
	def __init__(self, path):
		self.name = (os.path.split(path))[1]
		self.path = path
		self.lock_fd = None
		self.last_log = None

		self.descriptor = MediaDescriptor(self)
		self.sources = MediaSources(self)
		self.encoding = MediaEncoding(self)
		self.tags = TagList(self.element_path('tags.txt'))

		self.source_path = self.element_path('source')
		self.preview_path = self.element_path('preview')
		self.thumbnail_path = self.element_path('thumbnail')
		self.video_path = self.element_path('video')
		self.temp_path = self.element_path('temp')

		self.hidden_re = hidden_file_re()
		self.media_re = media_file_re()
	
	def log(self, *s):
		now = time.time()
		
		if not self.last_log:
			log('>>> ' + self.name)
			self.last_log = 0

		if (now - self.last_log) > 30.0:
			log('@ ' + time_string())

		self.last_log = now
		log(*s)

	def element_path(self, *e):
		return os.path.join(self.path, *e)

	def initialise_sources(self):
		if os.path.exists(self.source_path):
			return
		else:
			media_files = []
			for name in os.listdir(self.path):
				path = os.path.join(self.path, name)
				if (not self.hidden_re.match(name)) and os.path.isfile(path) and self.media_re.match(name):
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
		self.initialise_sources()
		self.create_directory('preview')
		self.create_directory('thumbnail')
		self.create_directory('video')
		self.create_directory('temp')

	def source_files(self):
		sources = []
		for name in os.listdir(self.source_path):
			path = os.path.join(self.source_path, name)
			if (not self.hidden_re.match(name)) and os.path.isfile(path) and self.media_re.match(name):
				sources.append(name)
		return sources
	
	def valid(self):
		# FIXME: do some testing
		return True

	def add_initial_tags(self):
		data = self.name.split('-')
		for tag in data:
			tag = tag.strip().lower()
			if re.search(r'\(.+?\)', tag):
				matches = re.findall(r'\((.+?)\)', tag)
				tag = (re.subn(r'\s*\(.+?\)', '', tag))[0]
				for subtag in matches:
					self.tags.add(subtag)
					subtags = re.split(r'\s+', subtag)
					if len(subtags) > 1:
						for subsubtag in subtags:
							self.tags.add(subsubtag)

			if re.search(r'^ed\d*', tag):
				self.tags.add('ending')
			elif re.search(r'^op\d*', tag):
				self.tags.add('opening')
			
			self.tags.add(tag)

	def import_stage(self):
		self.log("import stage")
		self.initialise_layout()
		if not self.tags.exists():
			self.add_initial_tags()
			self.tags.save()
		# FIXME: extract subtitle files

	def index_stage(self):
		self.log("index stage")

		self.descriptor.load()
		self.sources.load()
		self.sources.index_files()
		
		metadata = []
		for file in self.sources.subtitles():
			subfile = file.subfile()
			entry = {
				'url': "/".join(['source', urllib.quote(file.name)]),
				'name': file.name,
				'language': file.metadata['language'],
				'lines' : subfile.clean_lines(),
				'raw_lines' : subfile.raw_lines()
			}
			metadata.append(entry)
		metadata = sorted(metadata, key=lambda x:x['name'])

		if list_hash(metadata) != list_hash(self.descriptor.subtitles()):
			self.descriptor.set_subtitles(metadata)
			self.descriptor.save()

	def select_highest_quality(self, files, language=None):
		if language:
			matching_files = [file for file in files if file['language'] == language]
			unknown_files = [file for file in files if file['language'] == 'und']
			if len(matching_files) > 0:
				files = matching_files
			elif len(unknown_files) > 0:
				files = unknown_files
				
		if len(files) > 0:
			sorted_files = sorted(files, key=lambda x:x['quality'], reverse=True)
			return sorted_files[0]
		else:
			return None
	
	def sort_languages(self, languages):
		priority = { 'jpn': 0, 'eng': 1, 'und': 9000 }
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
		
		self.sources.load()
		self.encoding.load()

		video_files = self.sources.video()
		audio_files = self.sources.audio()
		image_files = self.sources.image()
		subtitle_files = self.sources.subtitles()
		
		languages = {}
		for subtitles in subtitle_files:
			language = subtitles['language']
			if not languages.has_key(language):
				languages[language] = []
			languages[language].append(subtitles)

		encodings = []
		if (len(languages) == 0) and (len(video_files) > 0):
			encodings.append({
				'video': self.select_highest_quality(video_files),
				'language': 'und'
			})
		elif len(languages) > 0:
			for lang in self.sort_languages(languages.keys()):
				subtitles = self.select_highest_quality(subtitle_files, language=lang)
				video = self.select_highest_quality(video_files, language=lang)
				audio = self.select_highest_quality(audio_files, language=lang)
				image = self.select_highest_quality(image_files)
				valid = True

				encoding = {
					'subtitles': subtitles.name,
					'subtitle-shift': 0.0,
					'language': lang
				}

				if video:
					encoding['video'] = video.name
				elif image:
					encoding['image'] = image.name
				else:
					valid = False

				if audio:
					encoding['audio'] = audio.name
					encoding['audio-shift'] = 0.0

				if valid:
					encodings.append(encoding)

		self.encoding.update(encodings)

	def encode_stage(self):
		self.log("encode stage")

		self.descriptor.load()
		self.encoding.load()
		
		encodings = {}
		for (name, encoding) in self.encoding.items():
			expanded = dict(encoding)
			for key in ['video', 'audio', 'image', 'subtitle']:
				if encoding.has_key(key):
					source = self.sources[encoding[key]]
					for source_key in ['mtime', 'size', 'length', 'language']:
						if source.has_key(source_key):
							expanded[key + '-' + source_key] = source[source_key]
			expanded['encode-hash'] = dictionary_hash(expanded)
			encodings[name] = expanded

		added = []
		updated = []
		removed = []

		videos = {}
		for video in self.descriptor.videos():
			videos[video['name']] = video
		
		for (name, encoding) in encodings.items():
			if videos.has_key(name):
				if videos[name]['encode-hash'] != encoding['encode-hash']:
					updated.append(name)
				elif not os.path.exists(self.element_path('video', name)):
					updated.append(name)
			else:
				added.append(name)
		for (name, description) in videos.items():
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

		for name in (added + updated):
			self.log("encoding " + name)
			encoding = encodings[name]

			self.descriptor.remove_video(name)
			self.descriptor.save()
			
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
				if encoding.has_key('language'):
					encoder.language = encoding['language']
				ok = encoder.encode()
			
			if ok:
				self.log("encode complete")
				media = MediaFile(path)
				metadata = media.probe()
				metadata['url'] = "/".join(['video', urllib.quote(name)])
				metadata['name'] = name
				metadata['encode-hash'] = encoding['encode-hash']
				metadata['language'] = encoding['language']
				self.descriptor.add_video(metadata)
			else:
				self.log("encode failed")
				self.descriptor.remove_video(name)

			self.descriptor.save()

	def preview_stage(self):
		self.log("preview stage")
		targets = MediaEncoder.profile_names.values()
		
		# find existing previews
		previews = {}
		for preview in self.descriptor.previews():
			video_name = preview['src']
			target_name = preview['target']
			if not previews.has_key(video_name):
				previews[video_name] = {}
			previews[video_name][target_name] = MediaFile(
				self.element_path('preview', preview['name']), 
				metadata=preview
			)
		
		# find videos
		videos = {}
		for video in self.descriptor.videos():
			video_name = video['name']
			videos[video_name] = MediaFile(
				self.element_path('video', video_name), 
				metadata=video
			)

		# remove previews for none existent videos
		for video in previews:
			if not videos.has_key(video):
				self.log("video " + video + " no longer exists")	
				for preview in previews[video].values():
					self.log("rm " + preview.path)
					preview.unlink()
				self.descriptor.remove_previews(video=video)
		
		self.descriptor.save()
		
		# find videos for which previews need to be (re)generated
		to_generate = []
		for (name, video) in videos.items():
			if not previews.has_key(name):
				to_generate += [ (video, target) for target in targets ]
			else:
				to_generate += [ (video, preview['target']) for preview in previews[name].values() if (not preview.exists()) or (video.mtime() > preview.mtime()) ]
				to_generate += [ (video, target) for target in targets if target not in previews[name].keys() ]

		# generate previews
		for (video, target) in to_generate:
			video_name = video['name'] 
			self.log("generating " + target + " preview for " + video_name)
			
			# generate preview name
			(base_name, ext) = os.path.splitext(name)
			preview_name = base_name + "_" + target + MediaEncoder.profile_extension(target)
			path = self.element_path('preview', preview_name)
			
			# remove old metadata
			self.descriptor.remove_previews(name=preview_name)

			# encode video
			encoder = MediaEncoder(self, path)
			encoder.video = video.path
			
			self.log("encoding " + preview_name)
			ok = encoder.transcode(MediaEncoder.profile_id(target))
		
			if ok:
				self.log("encode complete")
				media = MediaFile(path)
				metadata = media.probe()
				metadata['target'] = target
				metadata['url'] = "/".join(['preview', urllib.quote(preview_name)])
				metadata['name'] = preview_name
				metadata['src'] = name
				metadata['language'] = video['language']
				self.descriptor.add_preview(metadata)
			else:
				self.log("encode failed")

			self.descriptor.save()

	def thumbnail_stage(self):
		self.log("thumbnail stage")
		
		self.descriptor.load()

		# find existing thumbnails
		thumbnails = {}
		for thumbnail in self.descriptor.thumbnails():
			video_name = thumbnail['src']
			if not thumbnails.has_key(video_name):
				thumbnails[video_name] = []
			thumbnails[video_name].append(
				MediaFile(
					self.element_path('thumbnail', thumbnail['name']), 
					metadata=thumbnail
				)
			)
		
		# find videos
		videos = {}
		for video in self.descriptor.videos():
			video_name = video['name']
			videos[video_name] = MediaFile(
				self.element_path('video', video_name), 
				metadata=video
			)

		# remove thumbnails for none existent videos
		for video in thumbnails:
			if not videos.has_key(video):
				self.log("video " + video + " no longer exists")	
				for thumbnail in thumbnails[video]:
					self.log("rm " + thumbnail.path)
					thumbnail.unlink()
				self.descriptor.remove_thumbnails(video=video)
		
		self.descriptor.save()
		
		# find videos for which thumbnails need to be (re)generated
		to_generate = {}
		for (name, video) in videos.items():
			if not thumbnails.has_key(name):
				to_generate[name] = video
			else:
				invalid = [ (not thumbnail.exists()) or (video.mtime() > thumbnail.mtime()) for thumbnail in thumbnails[name] ]
				if True in invalid:
					to_generate[name] = video

		# generate thumbnails
		for (name, video) in to_generate.items():
			self.log("generating thumbnails for " + name)
			
			# remove old metadata
			self.descriptor.remove_thumbnails(video=name)
			
			# setup time indexes
			times = []
			for offset in [0.2, 0.4, 0.6, 0.8]:
				times.append(float("%.3f" % (video.length() * offset)))
			self.log("thumbnail offset: " + str(times))

			# create file names and paths
			(base, ext) = os.path.splitext(name)
			names = {}
			files = []
			for (n, time) in enumerate(times):
				thumb_name = "{0}_{1}.jpg".format(base, n)
				thumb_path = self.element_path('thumbnail', thumb_name)
				names[thumb_path] = thumb_name
				files.append(thumb_path) 

			# generate thumbnail files
			video.log = self
			results = video.generate_thumbnails(times, files, width=240)

			# create thumbnail metadata
			for (time, path) in results:
				thumb_name = names[path]
				thumb_media = MediaFile(path)
				metadata = thumb_media.probe()
				metadata['url'] = "/".join(['thumbnail', urllib.quote(thumb_name)])
				metadata['name'] = thumb_name
				metadata['src'] = video['name']
				metadata['time-index'] = time
				if thumb_media.exists():
					self.descriptor.add_thumbnail(metadata)

			self.descriptor.save()
	
	def lock(self):
		if self.lock_fd:
			self.unlock()
		try:
			self.lock_fd = os.open(self.element_path('lock'), os.O_WRONLY | os.O_CREAT)
			fcntl.lockf(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
			return True
		except:
			return False
	
	def unlock(self):
		if not self.lock_fd:
			return
		
		try:
			fcntl.lockf(self.lock_fd, fcntl.LOCK_UN)
		except:
			pass
		finally:
			try:
				os.close(self.lock_fd)
			except:
				pass
		
		self.lock_fd = None

	def run_stages(self):
		self.log("start")
		if not self.lock():
			self.log("cannot lock; ignoring")
			return
		
		self.import_stage()
		self.index_stage()
		self.pick_and_mix_stage()
		self.encode_stage()
		self.preview_stage()
		self.thumbnail_stage()

		self.unlock()
		self.log("end")

def test_program(cmd, package):
	cmd = map(unicode, cmd)
	try:
		return subprocess.check_output(cmd, stderr=subprocess.STDOUT)
	except subprocess.CalledProcessError as error:
		warn('error: ' + cmd[0] + " missing or broken (install " + package + "?)")
		return None

def check_tools():
	ok = True 

	# avprobe
	result = test_program(['avprobe', '-version'], 'libav')
	ok = ok and (result is not None)

	# avconv
	result = test_program(['avconv', '-codecs'], 'libav')
	ok = ok and (result is not None)
	if result:
		aac = re.search(r'^\s*D?EA[\sSDT]+\s*aac', result, re.MULTILINE)
		libx264 = re.search(r'^\s*EV[\sSDT]+\s*libx264', result, re.MULTILINE)
		ok = ok and (aac and libx264)
		if not aac:
			warn("error: avconv does not support aac codec")
		if not libx264:
			warn("error: avconv does not support libx264 codec")

	# qt-faststart
	result = test_program(['qt-faststart'], 'libav/tools')
	ok = ok and (result is not None)

	# mencoder
	result = test_program(['mencoder', '-ovc', 'help'], 'mplayer')
	ok = ok and (result is not None)
	if result:
		x264 = re.search(r'^\s*x264', result, re.MULTILINE)
		ok = ok and x264
		if not x264:
			warn("error: mencoder does not support x264 codec")

	result = test_program(['mencoder', '-vf', 'help'], 'mplayer')
	ok = ok and (result is not None)
	if result:
		ass = re.search(r'^\s*ass', result, re.MULTILINE)
		ok = ok and ass
		if not ass:
			warn("error: mencoder does not support advanced subtitles (ass)")

	return ok

def find_items(path):
	hidden_re = hidden_file_re()
	items = []
	for entry in os.listdir(path):
		entry_path = os.path.join(path, entry)
		if hidden_re.match(entry):
			pass
		elif os.path.isdir(entry_path):
			item = MediaItem(entry_path)
			if item.valid():
				items.append(item)
	return sorted(items, key=lambda x:x.name)

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
			if label:
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
  
  check-tools
    Test that the appropriate 3rd party tools are installed.

  process <media-root> [<log-file>]
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
	if (len(args) >= 1) and (args[0] == 'check-tools'):
		ok = check_tools()
		if ok:
			log("system tools are present and correct")
		else:
			warn("system tools are missing or not suitable")
	elif len(args) >= 2:
		tools = check_tools()
		if not tools:
			warn("system tools are missing or not suitable")
			sys.exit(1)

		command = args[0]
		root = args[1]
		if command == 'process':
			if len(args) >= 3:
				log_file = args[2]
				log_add(log_file)
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

	else:
		usage(sys.stderr)
		sys.exit(1)

if __name__ == "__main__":
        main(sys.argv[1:])
	sys.exit(0)
