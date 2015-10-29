import re
from collections import namedtuple
from datetime import time
from itertools import zip_longest

re_time = re.compile(r'(?P<hour>\d{1,2}):(?P<min>\d{2}):(?P<sec>\d{2})[\.,](?P<ms>\d{1,4})')
re_srt_line = re.compile(r'(?P<index>\d+)\s*(?P<start>.+)\s*-->\s*(?P<end>.+)\s*(?P<text>[\w ]*)(\n\n|$)', flags=re.MULTILINE)
re_ssa_line = re.compile(r'Dialogue:(?P<marked>.*?),(?P<start>.+?),(?P<end>.+?),.*,(?P<text>.+)[\n$]')

Subtitle = namedtuple('Subtitle', ['start', 'end', 'text'])


def _parse(source):
    return None


def _parse_time(time_str):
    """
    >>> _parse_time('  1:23:45.67  ')
    datetime.time(1, 23, 45, 67)
    >>> _parse_time('1:23:45,67')
    datetime.time(1, 23, 45, 67)
    """
    time_dict = re_time.search(time_str).groupdict()
    return time(*(int(time_dict[k]) for k in ('hour', 'min', 'sec', 'ms')))


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
    def parse_line(line):
        return Subtitle(
            _parse_time(line['start']),
            _parse_time(line['end']),
            line['text'],
        )
    return [parse_line(line_match.groupdict()) for line_match in re_srt_line.finditer(source)]


def _parse_ssa(source):
    r"""

    >>> ssa = r'''
    ... [Events]
    ... Format: Marked, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
    ... Dialogue: Marked=0,0:00:00.00,0:00:05.00,*Default,NTP,0000,0000,0000,!Effect,{\a6}Ishida Yoko - {\c&HFFFF00&}Towa no Hana{\c&HFFFF&}\N{\c&HFFFFFF&}{\c&H8080FF&}Ai Yori Aoshi OP
    ... Dialogue: Marked=0,0:00:07.00,0:00:13.25,*Default,NTP,0000,0000,0000,!Effect,awaku saita hana no kao\N{\c&HFFFFFF&}nokoshi kisetsu wa sugimasu
    ... Dialogue: Marked=0,0:00:13.25,0:00:19.20,*Default,NTP,0000,0000,0000,!Effect,nokoshi kisetsu wa sugimasu\N{\c&HFFFFFF&}ame mo agari sora ni kumo
    ... '''
    >>> _parse_ssa(ssa)
    [Subtitle(start=datetime.time(0, 0), end=datetime.time(0, 0, 5), text=''), Subtitle(start=datetime.time(0, 0, 7), end=datetime.time(0, 0, 13, 25), text='awaku saita hana no kao'), Subtitle(start=datetime.time(0, 0, 13, 25), end=datetime.time(0, 0, 19, 20), text='nokoshi kisetsu wa sugimasu\name mo agari sora ni kumo')]
    """
    def clean_line(text):
        if '{\\a6}' in text:
            return ''
        return re.sub(r'{.*?}', '', text).replace('\\N', '\n')
    def parse_line(line):
        return Subtitle(
            _parse_time(line['start']),
            _parse_time(line['end']),
            clean_line(line['text']),
        )
    lines = [parse_line(line_match.groupdict()) for line_match in re_ssa_line.finditer(source)]
    def remove_duplicate_line(line_current, line_next):
        if not line_next:
            return line_current
        _current = line_current.text.split('\n')
        _next = line_next.text.split('\n')
        return Subtitle(line_current.start, line_current.end, '\n'.join(line for line in _current if line not in _next))
    lines = [remove_duplicate_line(line_current, line_next) for line_current, line_next in zip_longest(lines, lines[1:])]
    return lines


def create_ssa(source):
    return None
