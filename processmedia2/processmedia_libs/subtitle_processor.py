import re
from collections import namedtuple, OrderedDict
from datetime import time
from itertools import zip_longest

SSA_NEWLINE = '\\N'
SSA_NEXT_COLOR = '{\\c&HFFFFFF&}'
SSA_HEIGHT_TO_FONT_SIZE_RATIO = 14

re_time = re.compile(r'(?P<hour>\d{1,2}):(?P<min>\d{2}):(?P<sec>\d{2})[\.,](?P<ms>\d{1,5})')
re_srt_line = re.compile(r'(?P<index>\d+)\s*(?P<start>.+)\s*-->\s*(?P<end>.+)\s*(?P<text>[\w ]*)(\n\n|$)', flags=re.MULTILINE)
re_ssa_line = re.compile(r'Dialogue:.+?,(?P<start>.+?),(?P<end>.+?),.*Effect,(?P<text>.+)[\n$]')  # the "Effect," is a hack! I cant COUNT the ',' in a regex and am assuming that all text has "!Effect,"

Subtitle = namedtuple('Subtitle', ('start', 'end', 'text'))


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
    """
    time_dict = re_time.search(time_str).groupdict()
    time_dict['ms'] = '{:0<6}'.format(time_dict['ms'])
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
    [Subtitle(start=datetime.time(0, 0, 13, 500000), end=datetime.time(0, 0, 22, 343000), text='mugen ni ikitai mugen ni ikiraretara'), Subtitle(start=datetime.time(0, 0, 22, 343000), end=datetime.time(0, 0, 25, 792000), text='subete kanau')]
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
    [Subtitle(start=datetime.time(0, 0), end=datetime.time(0, 0, 5), text=''), Subtitle(start=datetime.time(0, 0, 7), end=datetime.time(0, 0, 13, 250000), text='awaku saita hana no kao'), Subtitle(start=datetime.time(0, 0, 13, 250000), end=datetime.time(0, 0, 19, 200000), text='nokoshi kisetsu wa sugimasu\name mo agari sora ni kumo')]

    TODO: Upcoming bug!
        This only works for items with '!Effect,' (it's in the regex as a hack)
        We should count the ',' and grab the text after that index
    def (s, c): [s.index(c, index+1) for index in range(s.count(c))]
    """
    def clean_line(text):
        if '{\\a6}' in text:
            return ''
        text = re.sub(r'{.*?}', '', text)
        return '\n'.join(l.strip() for l in text.split('\\N'))
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
        deduped_text = '\n'.join(line for line in _current if line not in _next)
        return Subtitle(line_current.start, line_current.end, deduped_text)
    lines = [remove_duplicate_line(line_current, line_next) for line_current, line_next in zip_longest(lines, lines[1:])]
    return lines


def parse_subtiles(data=None, filename=None, filehandle=None):
    """
    >>> srt = '''
    ... 1
    ... 00:00:00,000 --> 00:00:01,000
    ... srt
    ... '''
    >>> ssa = '''
    ... Dialogue: Marked=0,0:00:00.00,0:00:01.00,*Default,NTP,0000,0000,0000,!Effect,ssa
    ... '''
    >>> parse_subtiles(srt)
    [Subtitle(start=datetime.time(0, 0), end=datetime.time(0, 0, 1), text='srt')]
    >>> parse_subtiles(ssa)
    [Subtitle(start=datetime.time(0, 0), end=datetime.time(0, 0, 1), text='ssa')]
    >>> parse_subtiles('not real subtitles')
    []
    """
    if filehandle:
        data = filehandle.read()
    if filename:
        with open(filename, mode='r', encoding='utf-8') as filehandle:
            data = filehandle.read()
    assert isinstance(data, str), 'Subtitle data should be a string'
    return _parse_srt(data) or _parse_ssa(data)


SSASection = namedtuple('SSASection', ('name', 'line', 'format_order'))


def create_ssa(subtitles, font_size=None, width=None, height=None, margin_h_size_multiplyer=1, margin_v_size_multiplyer=1, font_ratio=SSA_HEIGHT_TO_FONT_SIZE_RATIO):
    """
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
    Dialogue: Marked=0,0:00:00.00,0:01:00.00,*Default,NTP,0000,0000,0000,!Effect,first\\N{\\c&HFFFFFF&}second
    Dialogue: Marked=0,0:02:00.00,0:03:00.51,*Default,NTP,0000,0000,0000,!Effect,second
    <BLANKLINE>

    >>> _parse_ssa(ssa)
    [Subtitle(start=datetime.time(0, 0), end=datetime.time(0, 1), text='first'), Subtitle(start=datetime.time(0, 2), end=datetime.time(0, 3, 0, 510000), text='second')]

    """
    if not font_size and height:
        font_size = height / font_ratio
    if not font_size:
        font_size = font_ratio
    header = OrderedDict((
        ('Title', '<untitled>'),
        ('Original Script', '<unknown>'),
        ('ScriptType', 'v4.00'),
    ))
    if width:
        header['PlayResX'] = width
    if height:
        header['PlayResY'] = height
    ssa_template = OrderedDict((
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
                'Text': '{}{}{}{}'.format(subtitle.text, SSA_NEWLINE, SSA_NEXT_COLOR, subtitle_next.text) if subtitle_next else subtitle.text,
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

        o.append('[{0}]'.format(section_name))

        if section_meta is None:
            for key, value in section_data.items():
                o.append('{0}: {1}'.format(key, value))
        if isinstance(section_meta, SSASection):
            o.append('Format: {0}'.format(', '.join(section_meta.format_order)))
            for item in section_data:
                o.append('{0}: {1}'.format(section_meta.line, ','.join(str(item[col_name]) for col_name in section_meta.format_order)))

        o.append('')

    return '\n'.join(o)
