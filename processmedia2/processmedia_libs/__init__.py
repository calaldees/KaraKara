EXTS = dict(
    video=('rm', 'mpg', 'avi', 'mkv', 'ogm', 'mp4'),
    audio=('mp2', 'mp3', 'ogg', 'flac'),
    image=('jpg', 'png'),
    sub=('ssa', 'srt'),
    data=('yml', 'yaml'),
    tag=('txt', )
)
ALL_EXTS = tuple(j for i in EXTS.values() for j in i)

PENDING_ACTION = dict(
    encode='encode',
)
