import re
from collections import namedtuple
from datetime import time

re_srt_line = re.compile(r'(?P<index>\d+)\s*(?P<start_hour>\d{1,2}):(?P<start_min>\d{1,2}):(?P<start_sec>\d{1,2}),(?P<start_ms>\d{1,4})\s*-->\s*(?P<end_hour>\d{1,2}):(?P<end_min>\d{1,2}):(?P<end_sec>\d{1,2}),(?P<end_ms>\d{1,4})\s*(?P<text>[\w ]*)(\n\n|$)', flags=re.MULTILINE)


Subtitle = namedtuple('Subtitle', ['start', 'end', 'text'])


def _parse(source):
    return None


def _parse_srt(source):
    """
    >>> srt = '''
    ... 1
    ... 00:00:13,500 --> 00:00:22,343
    ... mugen ni ikitai mugen ni ikiraretara
    ...
    ... 2
    ... 00:00:22,343 --> 00:00:25,792
    ... subete kanau
    ... '''
    >>> _parse_srt(srt)
    [Subtitle(start=datetime.time(0, 0, 13, 500), end=datetime.time(0, 0, 22, 343), text='mugen ni ikitai mugen ni ikiraretara'), Subtitle(start=datetime.time(0, 0, 22, 343), end=datetime.time(0, 0, 25, 792), text='subete kanau')]
    """
    def time_args(prefix, data):
        return (int(data['{}_{}'.format(prefix, k)]) for k in ('hour', 'min', 'sec', 'ms'))
    def parse_line(line):
        return Subtitle(
            time(*time_args('start', line)),
            time(*time_args('end', line)),
            line['text'],
        )
    return [parse_line(line_match.groupdict()) for line_match in re_srt_line.finditer(source)]


def _parse_ssa(source):
    return None


def convert_srt_to_ssa(source):
    return None


def normalise_ssa(source):
    return None
