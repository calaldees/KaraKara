from types import MappingProxyType

EXTS = MappingProxyType(dict(
    video=['rm', 'mpg', 'avi', 'mkv', 'ogm', 'mp4', 'webm'],
    audio=['mp2', 'mp3', 'ogg', 'flac'],
    image=['jpg', 'png', 'avif', 'bmp', 'jp2', 'webp'],
    sub=['ssa', 'srt'],
    data=['yml', 'yaml'],
    tag=['txt', ]
))
ALL_EXTS = tuple(j for i in EXTS.values() for j in i)

EXT_TO_TYPE = MappingProxyType({
    ext: _type 
    for _type, exts in EXTS.items()
    for ext in exts
})

PENDING_ACTION = dict(
    encode='encode',
)
