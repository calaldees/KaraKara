## -*- coding: utf-8 -*-

import re
from datetime import time
from itertools import zip_longest, tee, chain
from typing import NamedTuple

import logging
from typing import NamedTuple
log = logging.getLogger(__name__)


SSA_NEWLINE = '\\N'
SSA_NEXT_COLOR = '{\\c&HFFFFFF&}'
SSA_HEIGHT_TO_FONT_SIZE_RATIO = 14

SRT_FORMAT = '''\
{index}
{start} --> {end}
{text}

'''

re_time = re.compile(r'(?P<hour>\d{1,2}):(?P<min>\d{2}):(?P<sec>\d{2})[\.,](?P<ms>\d{1,5})')
re_srt_line = re.compile(r'(?P<index>\d+)\n(?P<start>[\d:,]+) --> (?P<end>[\d:,]+)\n(?P<text>.*)(\n\n|$)', flags=re.MULTILINE)
re_ssa_line = re.compile(r'Dialogue:.+?,(?P<start>.+?),(?P<end>.+?),(?P<style>.*?),(?P<name>.*?),(?P<marginL>.*?),(?P<marginR>.*?),(?P<marginV>.*?),(?P<effect>.*?),(?P<text>.+)[\n$]')

class Subtitle(NamedTuple):
    start: time = time()
    end: time = time()
    text: str = ''


class TextOverlap(NamedTuple):
    index: int
    text: str
def commonOverlap(text1, text2):
    """
    https://neil.fraser.name/news/2010/11/04/

    >>> commonOverlap('Fire at Will', 'William Riker is number one')
    TextOverlap(index=4, text='Will')
    >>> commonOverlap('Have some CoCo and CoCo', 'CoCo and CoCo is here.')
    TextOverlap(index=13, text='CoCo and CoCo')

    """
    index = min(len(text1), len(text2))
    while index > 0:
        if text1[-index:] == text2[:index]:
            break
        index -= 1
    return TextOverlap(index, text2[:index])


def _ssa_time(t):
    """
    >>> _ssa_time(time(1, 23, 45, 671000))
    '1:23:45.67'
    >>> _ssa_time(time(0, 0, 0, 0))
    '0:00:00.00'
    >>> _ssa_time(time(1, 2, 3, 50000))
    '1:02:03.05'
    """
    return '{}:{:02d}:{:02d}.{:02d}'.format(t.hour, t.minute, t.second, int(t.microsecond/10000))


def _srt_time(t):
    """
    >>> _srt_time(time(1, 23, 45, 671000))
    '01:23:45,671'
    >>> _srt_time(time(0, 0, 0, 0))
    '00:00:00,000'
    >>> _srt_time(time(1, 2, 3, 50000))
    '01:02:03,050'
    """
    return '{:02d}:{:02d}:{:02d},{:03d}'.format(t.hour, t.minute, t.second, int(t.microsecond/1000))


def _vtt_time(t):
    """
    >>> _vtt_time(time(1, 23, 45, 671000))
    '01:23:45.671'
    >>> _vtt_time(time(0, 0, 0, 0))
    '00:00:00.000'
    >>> _vtt_time(time(1, 2, 3, 50000))
    '01:02:03.050'
    """
    return '{:02d}:{:02d}:{:02d}.{:03d}'.format(t.hour, t.minute, t.second, int(t.microsecond/1000))


def _parse_time(time_str):
    """
    >>> _parse_time('  1:23:45.6700  ')
    datetime.time(1, 23, 45, 670000)
    >>> _parse_time('1:23:45,67')
    datetime.time(1, 23, 45, 670000)
    >>> _parse_time('1:02:03.05')
    datetime.time(1, 2, 3, 50000)
    >>> _ssa_time(_parse_time('1:02:03.05'))
    '1:02:03.05'
    >>> _parse_time('0:00:60.50')
    datetime.time(0, 1, 0, 500000)

    ##>>> _parse_time('0:59:60.1000001')
    ##datetime.time(1, 0, 1)
    """
    time_dict = re_time.search(time_str).groupdict()
    time_dict['ms'] = int('{:0<6}'.format(time_dict['ms']))  # time_dict['ms'].ljust(6, '0')
    for k in ('hour', 'min', 'sec'):
        time_dict[k] = int(time_dict[k])
    #time_dict['sec'] += time_dict['ms'] // 1000000
    time_dict['min'] += time_dict.get('sec') // 60
    time_dict['hour'] += time_dict['min'] // 60
    #time_dict['ms'] = time_dict['ms'] % 1000000
    time_dict['sec'] = time_dict['sec'] % 60
    time_dict['min'] = time_dict['min'] % 60
    return time(*(time_dict[k] for k in ('hour', 'min', 'sec', 'ms')))


def _parse_srt(source):
    """
    >>> srt = '''
    ... 1
    ... 00:00:13,500 --> 00:00:22,343
    ... test, it's, キ
    ...
    ... 2
    ... 00:00:22,343 --> 00:00:25,792
    ... second
    ...
    ... 3
    ... 00:00:30,000 --> 00:00:40,000
    ...
    ...
    ... '''
    >>> _parse_srt(srt)
    [Subtitle(start=datetime.time(0, 0, 13, 500000), end=datetime.time(0, 0, 22, 343000), text="test, it's, キ"), Subtitle(start=datetime.time(0, 0, 22, 343000), end=datetime.time(0, 0, 25, 792000), text='second')]
    """
    def parse_line(line):
        return Subtitle(
            _parse_time(line['start']),
            _parse_time(line['end']),
            line['text'],
        )
    lines = [parse_line(line_match.groupdict()) for line_match in re_srt_line.finditer(source)]
    return [line for line in lines if line.text]


def _parse_ssa(source):
    r"""

    Ignore text on top of screen
    Remove duplication

    >>> ssa = r'''
    ... [Events]
    ... Format: Marked, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
    ... Dialogue: Marked=0,0:00:00.00,0:00:05.00,*Default,NTP,0000,0000,0000,!Effect,{\a6}Ishida Yoko - {\c&HFFFF00&}Towa no Hana{\c&HFFFF&}\N{\c&HFFFFFF&}{\c&H8080FF&}Ai Yori Aoshi OP
    ... Dialogue: Marked=0,0:00:07.00,0:00:13.25,*Default,NTP,0000,0000,0000,!Effect,awaku saita hana no kao\N{\c&HFFFFFF&}nokoshi kisetsu wa sugimasu
    ... Dialogue: Marked=0,0:00:13.25,0:00:19.20,*Default,NTP,0000,0000,0000,!Effect,nokoshi kisetsu wa sugimasu\N{\c&HFFFFFF&}ame mo agari sora ni kumo
    ... '''
    >>> _parse_ssa(ssa)
    [Subtitle(start=datetime.time(0, 0, 7), end=datetime.time(0, 0, 13, 250000), text='awaku saita hana no kao'), Subtitle(start=datetime.time(0, 0, 13, 250000), end=datetime.time(0, 0, 19, 200000), text='nokoshi kisetsu wa sugimasu\name mo agari sora ni kumo')]

    Overlap of subtitles should be removed

    >>> ssa = r'''
    ... Dialogue: Marked=0,0:00:06.91,0:00:12.39,*Default,NTP,0000,0000,0000,!Effect,Tooi hi no kioku wo \N {\c&HFFFFFF&} Kanashimi no iki no ne wo
    ... Dialogue: Marked=0,0:00:12.49,0:00:21.53,*Default,NTP,0000,0000,0000,!Effect,Kanashimi no iki no ne wo tometekure yo \N {\c&HFFFFFF&} Saa ai ni kogareta mune
    ... '''
    >>> _parse_ssa(ssa)
    [Subtitle(start=datetime.time(0, 0, 6, 910000), end=datetime.time(0, 0, 12, 390000), text='Tooi hi no kioku wo'), Subtitle(start=datetime.time(0, 0, 12, 490000), end=datetime.time(0, 0, 21, 530000), text='Kanashimi no iki no ne wo tometekure yo\nSaa ai ni kogareta mune')]

    A file with almost all toptitles should be parsed normally

    >>> ssa = r'''
    ... Dialogue: Marked=0,0:00:01.00,0:00:02.00,*Default,NTP,0000,0000,0000,!Effect,{\someControlShit\a6}First
    ... Dialogue: Marked=0,0:00:02.00,0:00:03.00,*Default,NTP,0000,0000,0000,!Effect,{\a6}Second
    ... Dialogue: Marked=0,0:00:03.00,0:00:04.00,*Default,NTP,0000,0000,0000,!Effect,{\a6}Third
    ... '''
    >>> _parse_ssa(ssa)
    [Subtitle(start=datetime.time(0, 0, 1), end=datetime.time(0, 0, 2), text='First'), Subtitle(start=datetime.time(0, 0, 2), end=datetime.time(0, 0, 3), text='Second'), Subtitle(start=datetime.time(0, 0, 3), end=datetime.time(0, 0, 4), text='Third')]

    Small Overlap is rejected

    >>> ssa = r'''
    ... Dialogue: Marked=0,0:00:01.00,0:00:02.00,*Default,NTP,0000,0000,0000,!Effect, ga takaraMON da \N {\c&HFFFFFF&} ase mamire wa
    ... Dialogue: Marked=0,0:00:02.00,0:00:03.00,*Default,NTP,0000,0000,0000,!Effect,ase mamire
    ... '''
    >>> _parse_ssa(ssa)
    [Subtitle(start=datetime.time(0, 0, 1), end=datetime.time(0, 0, 2), text='ga takaraMON da\nase mamire wa'), Subtitle(start=datetime.time(0, 0, 2), end=datetime.time(0, 0, 3), text='ase mamire')]

    >>> ssa = r'''
    ... Dialogue: ,0:00:00.00,0:00:01.00,,,,,,,this is, text on same line
    ... '''
    >>> _parse_ssa(ssa)
    [Subtitle(start=datetime.time(0, 0), end=datetime.time(0, 0, 1), text='this is, text on same line')]

    """
    lines = [line_match.groupdict() for line_match in re_ssa_line.finditer(source)]

    # Keep 'toptitles' if the majority of the files are toptitles.
    toptitle_count = '\n'.join(line_dict['text'] for line_dict in lines).count('\\a6')
    remove_toptitles = toptitle_count < int(len(lines) * 0.8)

    def clean_line(text):
        if remove_toptitles and '\\a6' in text:
            return ''
        text = re.sub(r'{.*?}', '', text)
        return '\n'.join(l.strip() for l in text.split('\\N'))
    def parse_line(line):
        return Subtitle(
            _parse_time(line['start']),
            _parse_time(line['end']),
            clean_line(line['text']),
        )
    lines = [parse_line(line_dict) for line_dict in lines]
    def remove_duplicate_line(line_current, line_next):
        if not line_next:
            return line_current
        _, overlap_text = commonOverlap(line_current.text, line_next.text)
        if len(overlap_text) < int(len(line_next.text) * 0.3):
            log.debug('Subtitle text overlap is suspiciously small, ignoring the overlap current:"{}" - next:"{}" - overlap:"{}"'.format(line_current.text, line_next.text, overlap_text))
            overlap_text = ''
        return Subtitle(line_current.start, line_current.end, line_current.text.replace(overlap_text, '').strip())
    lines = [remove_duplicate_line(line_current, line_next) for line_current, line_next in zip_longest(lines, lines[1:])]
    return [line for line in lines if line.text]


def parse_subtitles(data):
    """
    >>> srt = '''
    ... 1
    ... 00:00:00,000 --> 00:00:01,000
    ... srt
    ... '''
    >>> ssa = '''
    ... Dialogue: Marked=0,0:00:00.00,0:00:01.00,*Default,NTP,0000,0000,0000,!Effect,ssa
    ... '''
    >>> parse_subtitles(srt)
    [Subtitle(start=datetime.time(0, 0), end=datetime.time(0, 0, 1), text='srt')]
    >>> parse_subtitles(ssa)
    [Subtitle(start=datetime.time(0, 0), end=datetime.time(0, 0, 1), text='ssa')]
    >>> parse_subtitles('not real subtitles')
    []
    """
    assert isinstance(data, str), 'Subtitle data should be a string'
    return _parse_srt(data) or _parse_ssa(data)


class SSASection(NamedTuple):
    name: str
    line: int
    format_order: tuple
def create_ssa(subtitles, font_size=None, width=None, height=None, margin_h_size_multiplyer=1, margin_v_size_multiplyer=1, font_ratio=SSA_HEIGHT_TO_FONT_SIZE_RATIO):
    r"""
    >>> ssa = create_ssa((
    ...     Subtitle(time(0,0,0,0), time(0,1,0,0), 'first'),
    ...     Subtitle(time(0,2,0,0), time(0,3,0,510000), 'second'),
    ... ))
    >>> print(ssa)
    [Script Info]
    Title: <untitled>
    Original Script: <unknown>
    ScriptType: v4.00
    <BLANKLINE>
    [V4 Styles]
    Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, TertiaryColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, AlphaLevel, Encoding
    Style: Default,Arial,14,65535,16777215,16777215,0,-1,0,3,1,1,2,14,14,14,0,128
    <BLANKLINE>
    [Events]
    Format: Marked, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
    Dialogue: Marked=0,0:00:00.00,0:01:00.00,*Default,NTP,0000,0000,0000,!Effect,first\N{\c&HFFFFFF&}second
    Dialogue: Marked=0,0:02:00.00,0:03:00.51,*Default,NTP,0000,0000,0000,!Effect,second
    <BLANKLINE>

    >>> _parse_ssa(ssa)
    [Subtitle(start=datetime.time(0, 0), end=datetime.time(0, 1), text='first'), Subtitle(start=datetime.time(0, 2), end=datetime.time(0, 3, 0, 510000), text='second')]

    >>> ssa = create_ssa((
    ...     Subtitle(time(0,0,0,0), time(0,1,0,0), 'newline\ntest'),
    ... ))
    >>> 'newline\\Ntest' in ssa
    True

    """
    if not font_size and height:
        font_size = height / font_ratio
    if not font_size:
        font_size = font_ratio
    header = dict((
        ('Title', '<untitled>'),
        ('Original Script', '<unknown>'),
        ('ScriptType', 'v4.00'),
    ))
    if width:
        header['PlayResX'] = width
    if height:
        header['PlayResY'] = height
    ssa_template = dict((
        ('Script Info', header),
        (SSASection('V4 Styles', 'Style', ('Name', 'Fontname', 'Fontsize', 'PrimaryColour', 'SecondaryColour', 'TertiaryColour', 'BackColour', 'Bold', 'Italic', 'BorderStyle', 'Outline', 'Shadow', 'Alignment', 'MarginL', 'MarginR', 'MarginV', 'AlphaLevel', 'Encoding')), (
            {
                'Name': 'Default',
                'Fontname': 'Arial',
                'Fontsize': int(font_size),
                'PrimaryColour': 65535,
                'SecondaryColour': 16777215,
                'TertiaryColour': 16777215,
                'BackColour': 0,
                'Bold': -1,
                'Italic': 0,
                'BorderStyle': 3,
                'Outline': 1,
                'Shadow': 1,
                'Alignment': 2,
                'MarginL': int(margin_h_size_multiplyer * font_size),
                'MarginR': int(margin_h_size_multiplyer * font_size),
                'MarginV': int(margin_v_size_multiplyer * font_size),
                'AlphaLevel': 0,
                'Encoding': 128,
            },
        )),
        (SSASection('Events', 'Dialogue', ('Marked', 'Start', 'End', 'Style', 'Name', 'MarginL', 'MarginR', 'MarginV', 'Effect', 'Text')), (
            {
                'Marked': 'Marked=0',
                'Start': _ssa_time(subtitle.start),
                'End': _ssa_time(subtitle.end),
                'Style': '*Default',
                'Name': 'NTP',
                'MarginL': '0000',
                'MarginR': '0000',
                'MarginV': '0000',
                'Effect': '!Effect',
                'Text': ('{}{}{}{}'.format(subtitle.text, SSA_NEWLINE, SSA_NEXT_COLOR, subtitle_next.text) if subtitle_next else subtitle.text).replace('\n', SSA_NEWLINE),
            }
            for subtitle, subtitle_next in zip_longest(subtitles, subtitles[1:])
        )),
    ))

    o = []
    for key, section_data in ssa_template.items():
        if isinstance(key, SSASection):
            section_name = key.name
            section_meta = key
        else:
            section_name = key
            section_meta = None

        # Section Header
        o.append('[{0}]'.format(section_name))

        # No field list - just print the dict
        if section_meta is None:
            for key, value in section_data.items():
                o.append('{0}: {1}'.format(key, value))
        # Specific field list required for this section
        if isinstance(section_meta, SSASection):
            # Section field description
            o.append('Format: {0}'.format(', '.join(section_meta.format_order)))
            # Add each row
            for item in section_data:
                o.append('{0}: {1}'.format(section_meta.line, ','.join(str(item[col_name]) for col_name in section_meta.format_order)))

        o.append('')

    return '\n'.join(o)


def create_srt(subtitles):
    """
    >>> srt = create_srt((
    ...     Subtitle(time(0,0,0,0), time(0,1,0,0), 'first'),
    ...     Subtitle(time(0,2,0,0), time(0,3,0,510000), 'second'),
    ...     Subtitle(time(0,4,0,0), time(0,5,0,0), ''),
    ... ))
    >>> print(srt)
    1
    00:00:00,000 --> 00:01:00,000
    first
    <BLANKLINE>
    2
    00:02:00,000 --> 00:03:00,510
    second
    <BLANKLINE>
    <BLANKLINE>

    >>> _parse_srt(srt)
    [Subtitle(start=datetime.time(0, 0), end=datetime.time(0, 1), text='first'), Subtitle(start=datetime.time(0, 2), end=datetime.time(0, 3, 0, 510000), text='second')]
    """
    return ''.join(
        SRT_FORMAT.format(
            index=index+1,
            start=_srt_time(subtitle.start),
            end=_srt_time(subtitle.end),
            text=subtitle.text,
        )
        for index, subtitle in enumerate(subtitles)
        if subtitle.text
    )




def pairwise(iterable, fillvalue=None):
    """
    now part of standard lib itertools.pairwise
    https://stackoverflow.com/a/5434936/3356840
    s -> (s0,s1), (s1,s2), (s2, s3), ...

    >>> tuple(pairwise((1,2,3)))
    ((None, 1), (1, 2), (2, 3), (3, None))
    """
    a, b = tee(iterable)
    return chain(((fillvalue, next(b, fillvalue)),), zip_longest(a, b, fillvalue=fillvalue))

def create_vtt(subtitles):
    r"""
    https://developer.mozilla.org/en-US/docs/Web/API/WebVTT_API
    https://w3c.github.io/webvtt/
    https://caniuse.com/?search=vtt

    >>> vtt = create_vtt((
    ...     Subtitle(time(0,1,0,0), time(0,2,0,0), 'first'),
    ...     Subtitle(time(0,2,0,0), time(0,3,0,510000), 'second'),
    ... ))
    >>> print(vtt)
    WEBVTT - KaraKara Subtitle
    <BLANKLINE>
    1
    00:00:00.000 --> 00:01:00.000
    <v active>
    <v next>first
    <BLANKLINE>
    2
    00:01:00.000 --> 00:02:00.000
    <v active>first
    <v next>second
    <BLANKLINE>
    3
    00:02:00.000 --> 00:03:00.510
    <v active>second
    <v next>
    <BLANKLINE>
    <BLANKLINE>
    """
    VTT_FORMAT = """\
<v active>{active}
<v next>{next}"""
    return 'WEBVTT - KaraKara Subtitle\n\n' + ''.join(
        SRT_FORMAT.format(
            index=index+1,
            start=_vtt_time(subtitle1.start),
            end=_vtt_time(subtitle1.end if subtitle1.end != time() else subtitle2.start),
            text=VTT_FORMAT.format(active=subtitle1.text, next=subtitle2.text),
        )
        for index, (subtitle1, subtitle2) in enumerate(pairwise(subtitles, fillvalue=Subtitle()))
    )
