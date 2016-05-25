import chardet

import processmedia_libs.subtitle_processor as subtitle_processor
from processmedia_libs.subtitle_processor import *


def binary_decode_to_unicode(data, fallback_encoding='utf-8'):
    """
    http://stackoverflow.com/a/26382720/3356840
    """
    return data.decode(encoding=chardet.detect(data).get('encoding') or fallback_encoding, errors='ignore')


def parse_subtitles(data=None, filename=None, filehandle=None):
    """
    TODO: doctest?
    """
    if filehandle:
        data = filehandle.read()
    elif filename:
        with open(filename, mode='rb') as filehandle:
            data = filehandle.read()
    if isinstance(data, bytes):
        data = binary_decode_to_unicode(data)
    data = data.replace('\r\n', '\n')
    return subtitle_processor.parse_subtitles(data)
