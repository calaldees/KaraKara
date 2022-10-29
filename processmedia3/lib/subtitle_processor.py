## -*- coding: utf-8 -*-

import re
from datetime import timedelta
from itertools import zip_longest, tee, chain
from sqlite3 import Timestamp
from typing import NamedTuple, List

import logging
from typing import NamedTuple

log = logging.getLogger(__name__)


SSA_NEWLINE = "\\N"
SSA_NEXT_COLOR = "{\\c&HFFFFFF&}"
SSA_HEIGHT_TO_FONT_SIZE_RATIO = 14

SRT_FORMAT = """\
{index}
{start} --> {end}
{text}

"""

re_time = re.compile(
    r"(?P<hours>\d{1,2}):(?P<minutes>\d{2}):(?P<seconds>\d{2}[\.,]\d+)"
)
re_srt_line = re.compile(
    r"(?P<index>\d+)\n(?P<start>[\d:,]+) --> (?P<end>[\d:,]+)\n(?P<text>.*)(\n\n|$)",
    flags=re.MULTILINE,
)
re_ssa_line = re.compile(
    r"Dialogue:.+?,(?P<start>.+?),(?P<end>.+?),(?P<style>.*?),(?P<name>.*?),(?P<marginL>.*?),(?P<marginR>.*?),(?P<marginV>.*?),(?P<effect>.*?),(?P<text>.+)[\n$]"
)


class Subtitle(NamedTuple):
    start: timedelta = timedelta()
    end: timedelta = timedelta()
    text: str = ""
    top: bool = False


class TextOverlap(NamedTuple):
    idx: int
    text: str


def commonOverlap(text1: str, text2: str) -> TextOverlap:
    """
    https://neil.fraser.name/news/2010/11/04/

    >>> commonOverlap('Fire at Will', 'William Riker is number one')
    TextOverlap(idx=4, text='Will')
    >>> commonOverlap('Have some CoCo and CoCo', 'CoCo and CoCo is here.')
    TextOverlap(idx=13, text='CoCo and CoCo')

    """
    index = min(len(text1), len(text2))
    while index > 0:
        if text1[-index:] == text2[:index]:
            break
        index -= 1
    return TextOverlap(index, text2[:index])


def _ssa_time(t: timedelta) -> str:
    """
    >>> _ssa_time(timedelta(hours=1, minutes=23, seconds=45, microseconds=671000))
    '1:23:45.67'
    >>> _ssa_time(timedelta(hours=0, minutes=0, seconds=0, microseconds=0))
    '0:00:00.00'
    >>> _ssa_time(timedelta(hours=1, minutes=2, seconds=3, microseconds=50000))
    '1:02:03.05'
    """
    return "{}:{:02d}:{:05.02f}".format(
        t.seconds // 60 // 60,
        (t.seconds % (60 * 60)) // 60,
        t.seconds % 60 + t.microseconds / 1000000,
    )


def _srt_time(t: timedelta) -> str:
    """
    >>> _srt_time(timedelta(hours=1, minutes=23, seconds=45, microseconds=671000))
    '01:23:45,671'
    >>> _srt_time(timedelta(hours=0, minutes=0, seconds=0, microseconds=0))
    '00:00:00,000'
    >>> _srt_time(timedelta(hours=1, minutes=2, seconds=3, microseconds=50000))
    '01:02:03,050'
    """
    return "{:02d}:{:02d}:{:06.03f}".format(
        t.seconds // 60 // 60,
        (t.seconds % (60 * 60)) // 60,
        t.seconds % 60 + t.microseconds / 1000000,
    ).replace(".", ",")


def _vtt_time(t: timedelta) -> str:
    """
    >>> _vtt_time(timedelta(hours=1, minutes=23, seconds=45, microseconds=671000))
    '01:23:45.671'
    >>> _vtt_time(timedelta(hours=0, minutes=0, seconds=0, microseconds=0))
    '00:00:00.000'
    >>> _vtt_time(timedelta(hours=1, minutes=2, seconds=3, microseconds=50000))
    '01:02:03.050'
    """
    return "{:02d}:{:02d}:{:06.03f}".format(
        t.seconds // 60 // 60,
        (t.seconds % (60 * 60)) // 60,
        t.seconds % 60 + t.microseconds / 1000000,
    )


def _parse_time(time_str: str) -> timedelta:
    """
    >>> _parse_time('  1:23:45.6700  ')
    datetime.timedelta(seconds=5025, microseconds=670000)
    >>> _parse_time('1:23:45,67')
    datetime.timedelta(seconds=5025, microseconds=670000)
    >>> _parse_time('1:02:03.05')
    datetime.timedelta(seconds=3723, microseconds=50000)
    >>> _ssa_time(_parse_time('1:02:03.05'))
    '1:02:03.05'
    >>> _parse_time('0:00:60.50')
    datetime.timedelta(seconds=60, microseconds=500000)
    >>> _parse_time('0:59:60.1000001')
    datetime.timedelta(seconds=3600, microseconds=100000)
    """
    match = re_time.search(time_str)
    if not match:
        raise Exception(f"Can't parse time: {time_str}")
    time_dict = match.groupdict()
    return timedelta(
        hours=int(time_dict["hours"]),
        minutes=int(time_dict["minutes"]),
        seconds=float(time_dict["seconds"].replace(",", ".")),
    )


def clean_line(text: str) -> str:
    text = re.sub(r"{.*?}", "", text)
    return "\n".join(l.strip() for l in text.split("\\N"))


def _parse_srt(source: str) -> List[Subtitle]:
    r"""
    >>> srt = r'''
    ... 1
    ... 00:00:13,500 --> 00:00:22,343
    ... test, it's, キ
    ...
    ... 2
    ... 00:00:22,343 --> 00:00:25,792
    ... {\a6}second {\c&HFFFF80&}coloured bit
    ...
    ... 3
    ... 00:00:30,000 --> 00:00:40,000
    ...
    ...
    ... '''
    >>> _parse_srt(srt)
    [Subtitle(start=datetime.timedelta(seconds=13, microseconds=500000), end=datetime.timedelta(seconds=22, microseconds=343000), text="test, it's, キ", top=False), Subtitle(start=datetime.timedelta(seconds=22, microseconds=343000), end=datetime.timedelta(seconds=25, microseconds=792000), text='second coloured bit', top=True)]
    """

    def parse_line(line):
        return Subtitle(
            _parse_time(line["start"]),
            _parse_time(line["end"]),
            clean_line(line["text"]),
            "\\a6" in line["text"],
        )

    lines = [
        parse_line(line_match.groupdict())
        for line_match in re_srt_line.finditer(source)
    ]
    return [line for line in lines if line.text]


def _parse_ssa(source: str) -> List[Subtitle]:
    r"""
    >>> ssa = r'''
    ... [Events]
    ... Format: Marked, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
    ... Dialogue: Marked=0,0:00:00.00,0:00:05.00,*Default,NTP,0000,0000,0000,!Effect,{\a6}Ishida Yoko - {\c&HFFFF00&}Towa no Hana{\c&HFFFF&}\N{\c&HFFFFFF&}{\c&H8080FF&}Ai Yori Aoshi OP
    ... Dialogue: Marked=0,0:00:07.00,0:00:13.25,*Default,NTP,0000,0000,0000,!Effect,awaku saita hana no kao\N{\c&HFFFFFF&}nokoshi kisetsu wa sugimasu
    ... '''
    >>> _parse_ssa(ssa)
    [Subtitle(start=datetime.timedelta(0), end=datetime.timedelta(seconds=5), text='Ishida Yoko - Towa no Hana\nAi Yori Aoshi OP', top=True), Subtitle(start=datetime.timedelta(seconds=7), end=datetime.timedelta(seconds=13, microseconds=250000), text='awaku saita hana no kao\nnokoshi kisetsu wa sugimasu', top=False)]

    >>> ssa = r'''
    ... Dialogue: ,0:00:00.00,0:00:01.00,,,,,,,this is, text on same line
    ... '''
    >>> _parse_ssa(ssa)
    [Subtitle(start=datetime.timedelta(0), end=datetime.timedelta(seconds=1), text='this is, text on same line', top=False)]

    """
    lines = [line_match.groupdict() for line_match in re_ssa_line.finditer(source)]

    def parse_line(line):
        return Subtitle(
            _parse_time(line["start"]),
            _parse_time(line["end"]),
            clean_line(line["text"]),
            "\\a6" in line["text"],
        )

    return [parse_line(line_dict) for line_dict in lines]


def _remove_duplicate_lines(lines: List[Subtitle]) -> List[Subtitle]:
    r"""
    Overlap of subtitles should be removed

    >>> lines = [
    ...     Subtitle(start=timedelta(seconds=1), end=timedelta(seconds=2), text='Tooi hi no kioku wo\nKanashimi no iki no ne wo'),
    ...     Subtitle(start=timedelta(seconds=3), end=timedelta(seconds=4), text='Kanashimi no iki no ne wo tometekure yo\nSaa ai ni kogareta mune'),
    ... ]
    >>> [l.text for l in _remove_duplicate_lines(lines)]
    ['Tooi hi no kioku wo', 'Kanashimi no iki no ne wo tometekure yo\nSaa ai ni kogareta mune']

    Small Overlap is rejected

    >>> lines = [
    ...     Subtitle(start=timedelta(seconds=1), end=timedelta(seconds=2), text=' ga takaraMON da\nase mamire wa'),
    ...     Subtitle(start=timedelta(seconds=2), end=timedelta(seconds=3), text='ase mamire'),
    ... ]
    >>> [l.text for l in _remove_duplicate_lines(lines)]
    ['ga takaraMON da\nase mamire wa', 'ase mamire']

    """

    def remove_duplicate_line(line_current, line_next):
        if not line_next:
            return line_current
        _, overlap_text = commonOverlap(line_current.text, line_next.text)
        if len(overlap_text) < int(len(line_next.text) * 0.3):
            log.debug(
                'Subtitle text overlap is suspiciously small, ignoring the overlap current:"{}" - next:"{}" - overlap:"{}"'.format(
                    line_current.text, line_next.text, overlap_text
                )
            )
            overlap_text = ""
        return Subtitle(
            line_current.start,
            line_current.end,
            line_current.text.replace(overlap_text, "").strip(),
            line_current.top,
        )

    lines = [
        remove_duplicate_line(line_current, line_next)
        for line_current, line_next in zip_longest(lines, lines[1:])
    ]
    return [line for line in lines if line.text]


def _strip_toptitles(lines: List[Subtitle]) -> List[Subtitle]:
    r"""
    If there are many subs on top, keep them (they're normally trying
    to get out of the way of something on the bottom of the screen)

    >>> import datetime
    >>> lines = [
    ...     Subtitle(text='First', top=True),
    ...     Subtitle(text='Second', top=True),
    ...     Subtitle(text='Third', top=True),
    ... ]
    >>> [(l.text, l.top) for l in _strip_toptitles(lines)]
    [('First', True), ('Second', True), ('Third', True)]

    If there are only a few subs on top, strip them (they're normally
    duplicates of the song title)

    >>> lines = [
    ...     Subtitle(text='First', top=True),
    ...     Subtitle(text='Second', top=False),
    ...     Subtitle(text='Third', top=False),
    ... ]
    >>> [(l.text, l.top) for l in _strip_toptitles(lines)]
    [('Second', False), ('Third', False)]

    """
    if len([s for s in lines if s.top]) < len(lines) * 0.8:
        lines = [s for s in lines if not s.top]
    return lines


def parse_subtitles(data: str) -> List[Subtitle]:
    """
    >>> srt = '''
    ... 1
    ... 00:00:00,000 --> 00:00:01,000
    ... srt
    ... '''
    >>> parse_subtitles(srt)
    [Subtitle(start=datetime.timedelta(0), end=datetime.timedelta(seconds=1), text='srt', top=False)]

    >>> ssa = '''
    ... Dialogue: Marked=0,0:00:00.00,0:00:01.00,*Default,NTP,0000,0000,0000,!Effect,ssa
    ... '''
    >>> parse_subtitles(ssa)
    [Subtitle(start=datetime.timedelta(0), end=datetime.timedelta(seconds=1), text='ssa', top=False)]

    >>> parse_subtitles('not real subtitles')
    []
    """
    assert isinstance(data, str), "Subtitle data should be a string"
    # Only two tracks actually have duplicate lines - the two .ssa ones.
    # Other tracks have intentionally repeated lyrics, don't mess with those.
    lines = _parse_srt(data) or _remove_duplicate_lines(_parse_ssa(data))
    lines = _strip_toptitles(lines)
    return lines


class SSASection(NamedTuple):
    name: str
    line: int
    format_order: tuple


def create_ssa(
    subtitles,
    font_size=None,
    width=None,
    height=None,
    margin_h_size_multiplyer=1,
    margin_v_size_multiplyer=1,
    font_ratio=SSA_HEIGHT_TO_FONT_SIZE_RATIO,
):
    r"""
    >>> ssa = create_ssa((
    ...     Subtitle(timedelta(minutes=0), timedelta(minutes=1), 'first'),
    ...     Subtitle(timedelta(minutes=2), timedelta(minutes=3,microseconds=510000), 'second'),
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

    >>> _remove_duplicate_lines(_parse_ssa(ssa))
    [Subtitle(start=datetime.timedelta(0), end=datetime.timedelta(seconds=60), text='first', top=False), Subtitle(start=datetime.timedelta(seconds=120), end=datetime.timedelta(seconds=180, microseconds=510000), text='second', top=False)]

    >>> ssa = create_ssa((
    ...     Subtitle(timedelta(minutes=0), timedelta(minutes=1), 'newline\ntest'),
    ... ))
    >>> 'newline\\Ntest' in ssa
    True

    """
    if not font_size and height:
        font_size = height / font_ratio
    if not font_size:
        font_size = font_ratio
    header = dict(
        (
            ("Title", "<untitled>"),
            ("Original Script", "<unknown>"),
            ("ScriptType", "v4.00"),
        )
    )
    if width:
        header["PlayResX"] = width
    if height:
        header["PlayResY"] = height
    ssa_template = dict(
        (
            ("Script Info", header),
            (
                SSASection(
                    "V4 Styles",
                    "Style",
                    (
                        "Name",
                        "Fontname",
                        "Fontsize",
                        "PrimaryColour",
                        "SecondaryColour",
                        "TertiaryColour",
                        "BackColour",
                        "Bold",
                        "Italic",
                        "BorderStyle",
                        "Outline",
                        "Shadow",
                        "Alignment",
                        "MarginL",
                        "MarginR",
                        "MarginV",
                        "AlphaLevel",
                        "Encoding",
                    ),
                ),
                (
                    {
                        "Name": "Default",
                        "Fontname": "Arial",
                        "Fontsize": int(font_size),
                        "PrimaryColour": 65535,
                        "SecondaryColour": 16777215,
                        "TertiaryColour": 16777215,
                        "BackColour": 0,
                        "Bold": -1,
                        "Italic": 0,
                        "BorderStyle": 3,
                        "Outline": 1,
                        "Shadow": 1,
                        "Alignment": 2,
                        "MarginL": int(margin_h_size_multiplyer * font_size),
                        "MarginR": int(margin_h_size_multiplyer * font_size),
                        "MarginV": int(margin_v_size_multiplyer * font_size),
                        "AlphaLevel": 0,
                        "Encoding": 128,
                    },
                ),
            ),
            (
                SSASection(
                    "Events",
                    "Dialogue",
                    (
                        "Marked",
                        "Start",
                        "End",
                        "Style",
                        "Name",
                        "MarginL",
                        "MarginR",
                        "MarginV",
                        "Effect",
                        "Text",
                    ),
                ),
                (
                    {
                        "Marked": "Marked=0",
                        "Start": _ssa_time(subtitle.start),
                        "End": _ssa_time(subtitle.end),
                        "Style": "*Default",
                        "Name": "NTP",
                        "MarginL": "0000",
                        "MarginR": "0000",
                        "MarginV": "0000",
                        "Effect": "!Effect",
                        "Text": (
                            "{}{}{}{}".format(
                                subtitle.text,
                                SSA_NEWLINE,
                                SSA_NEXT_COLOR,
                                subtitle_next.text,
                            )
                            if subtitle_next
                            else subtitle.text
                        ).replace("\n", SSA_NEWLINE),
                    }
                    for subtitle, subtitle_next in zip_longest(subtitles, subtitles[1:])
                ),
            ),
        )
    )

    o = []
    for key, section_data in ssa_template.items():
        if isinstance(key, SSASection):
            section_name = key.name
            section_meta = key
        else:
            section_name = key
            section_meta = None

        # Section Header
        o.append("[{0}]".format(section_name))

        # No field list - just print the dict
        if section_meta is None:
            for key, value in section_data.items():
                o.append("{0}: {1}".format(key, value))
        # Specific field list required for this section
        if isinstance(section_meta, SSASection):
            # Section field description
            o.append("Format: {0}".format(", ".join(section_meta.format_order)))
            # Add each row
            for item in section_data:
                o.append(
                    "{0}: {1}".format(
                        section_meta.line,
                        ",".join(
                            str(item[col_name])
                            for col_name in section_meta.format_order
                        ),
                    )
                )

        o.append("")

    return "\n".join(o)


def create_srt(subtitles):
    """
    >>> srt = create_srt((
    ...     Subtitle(timedelta(minutes=0), timedelta(minutes=1), 'first'),
    ...     Subtitle(timedelta(minutes=2), timedelta(minutes=3, microseconds=510000), 'second'),
    ...     Subtitle(timedelta(minutes=4), timedelta(minutes=5), ''),
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
    [Subtitle(start=datetime.timedelta(0), end=datetime.timedelta(seconds=60), text='first', top=False), Subtitle(start=datetime.timedelta(seconds=120), end=datetime.timedelta(seconds=180, microseconds=510000), text='second', top=False)]
    """
    return "".join(
        SRT_FORMAT.format(
            index=index + 1,
            start=_srt_time(subtitle.start),
            end=_srt_time(subtitle.end),
            text=subtitle.text,
        )
        for index, subtitle in enumerate(subtitles)
        if subtitle.text
    )


def create_vtt(subtitles):
    r"""
    https://developer.mozilla.org/en-US/docs/Web/API/WebVTT_API
    https://w3c.github.io/webvtt/
    https://caniuse.com/?search=vtt

    >>> vtt = create_vtt(tuple())
    >>> print(vtt)
    WEBVTT - KaraKara Subtitle
    <BLANKLINE>
    <BLANKLINE>

    >>> vtt = create_vtt((
    ...     Subtitle(timedelta(minutes=1), timedelta(minutes=2), 'first'),
    ...     Subtitle(timedelta(minutes=2), timedelta(minutes=3, milliseconds=510), 'second'),
    ... ))
    >>> print(vtt)
    WEBVTT - KaraKara Subtitle
    <BLANKLINE>
    1
    00:00:55.000 --> 00:01:00.000
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

    >>> vtt = create_vtt((
    ...     Subtitle(timedelta(minutes=1), timedelta(minutes=2), 'first', top=True),
    ...     Subtitle(timedelta(minutes=2), timedelta(minutes=3, microseconds=510000), 'second', top=True),
    ...     Subtitle(timedelta(minutes=4), timedelta(minutes=5), 'third', top=True),
    ...     Subtitle(timedelta(minutes=5), timedelta(minutes=6, microseconds=510000), 'fourth', top=True),
    ... ))
    >>> print(vtt)
    WEBVTT - KaraKara Subtitle
    <BLANKLINE>
    1
    00:00:55.000 --> 00:01:00.000 line:1
    <v active>
    <v next>first
    <BLANKLINE>
    2
    00:01:00.000 --> 00:02:00.000 line:1
    <v active>first
    <v next>second
    <BLANKLINE>
    3
    00:02:00.000 --> 00:03:00.510 line:1
    <v active>second
    <v next>
    <BLANKLINE>
    4
    00:03:55.000 --> 00:04:00.000 line:1
    <v active>
    <v next>third
    <BLANKLINE>
    5
    00:04:00.000 --> 00:05:00.000 line:1
    <v active>third
    <v next>fourth
    <BLANKLINE>
    6
    00:05:00.000 --> 00:06:00.510 line:1
    <v active>fourth
    <v next>
    <BLANKLINE>
    <BLANKLINE>
    """
    VTT_FORMAT = """\
{index}
{start} --> {end}{format}
<v active>{active}
<v next>{next}

"""
    last_end = timedelta(0)
    padded_lines = []
    for line in subtitles:
        if line.start - last_end > timedelta(seconds=5):
            padded_lines.append(
                Subtitle(
                    start=line.start - timedelta(seconds=5),
                    end=line.start,
                    text="",
                    top=line.top,
                )
            )
        padded_lines.append(line)
        last_end = line.end
    padded_lines.append(Subtitle(start=last_end, end=last_end, text=""))

    return "WEBVTT - KaraKara Subtitle\n\n" + "".join(
        VTT_FORMAT.format(
            index=index + 1,
            start=_vtt_time(subtitle1.start),
            end=_vtt_time(subtitle1.end),
            format=" line:1" if subtitle1.top else "",
            active=subtitle1.text,
            next=subtitle2.text,
        )
        for index, (subtitle1, subtitle2) in enumerate(
            zip(padded_lines[:-1], padded_lines[1:])
        )
    )