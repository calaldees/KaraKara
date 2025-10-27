#!/usr/bin/env python
## -*- coding: utf-8 -*-

import re
from datetime import timedelta
from itertools import zip_longest
import typing as t
import logging
import difflib
import json

log = logging.getLogger(__name__)


SSA_NEWLINE = "\\N"
SSA_NEXT_COLOR = "{\\c&HFFFFFF&}"

re_time = re.compile(r"(?P<hours>\d{1,2}):(?P<minutes>\d{2}):(?P<seconds>\d{2}[\.,]\d+)")
re_srt_line = re.compile(
    r"(?P<index>\d+)\n(?P<start>[\d:,]+) --> (?P<end>[\d:,]+)\n(?P<text>.*?)(\n\n|$)",
    flags=re.DOTALL,
)
re_ssa_line = re.compile(
    r"Dialogue:.+?,(?P<start>.+?),(?P<end>.+?),(?P<style>.*?),(?P<name>.*?),(?P<marginL>.*?),(?P<marginR>.*?),(?P<marginV>.*?),(?P<effect>.*?),(?P<text>.+)[\n$]"
)


class SubtitleParseException(Exception):
    pass


class SubtitleFormatException(Exception):
    pass


class Subtitle(t.NamedTuple):
    start: timedelta = timedelta()
    end: timedelta = timedelta()
    text: str = ""
    top: bool = False


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
        raise SubtitleParseException(f"Can't parse time: {time_str}")
    time_dict = match.groupdict()
    return timedelta(
        hours=int(time_dict["hours"]),
        minutes=int(time_dict["minutes"]),
        seconds=float(time_dict["seconds"].replace(",", ".")),
    )


def clean_line(text: str) -> str:
    text = re.sub(r"{.*?}", "", text)
    return "\n".join(l.strip() for l in text.split("\\N"))


def _parse_srt(source: str) -> list[Subtitle]:
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

    def parse_line(line: dict[str, str]) -> Subtitle:
        return Subtitle(
            _parse_time(line["start"]),
            _parse_time(line["end"]),
            clean_line(line["text"]),
            "\\a6" in line["text"],
        )

    lines = [parse_line(line_match.groupdict()) for line_match in re_srt_line.finditer(source)]
    return [line for line in lines if line.text]


def _parse_ssa(source: str) -> list[Subtitle]:
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

    def parse_line(line: dict[str, str]) -> Subtitle:
        return Subtitle(
            _parse_time(line["start"]),
            _parse_time(line["end"]),
            clean_line(line["text"]),
            "\\a6" in line["text"],
        )

    return [parse_line(line_dict) for line_dict in lines]


def parse_subtitles(data: str) -> list[Subtitle]:
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
    return _parse_srt(data) or _parse_ssa(data)


def create_ssa(subtitles: list[Subtitle]) -> str:
    data = """[Script Info]
Title: <untitled>
Original Script: <unknown>
ScriptType: v4.00

[V4 Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, TertiaryColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, AlphaLevel, Encoding
Style: Default,Arial,14,65535,16777215,16777215,0,-1,0,3,1,1,2,14,14,14,0,128

[Events]
Format: Marked, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    for subtitle, subtitle_next in zip_longest(subtitles, subtitles[1:]):
        text = (
            "{}{}{}{}".format(
                subtitle.text,
                SSA_NEWLINE,
                SSA_NEXT_COLOR,
                subtitle_next.text,
            )
            if subtitle_next
            else subtitle.text
        ).replace("\n", SSA_NEWLINE)
        data += f"Dialogue: Marked=0,{_ssa_time(subtitle.start)},{_ssa_time(subtitle.end)},*Default,NTP,0000,0000,0000,!Effect,{text}\n"
    return data


def create_srt(subtitles: list[Subtitle]) -> str:
    SRT_FORMAT = """\
{index}
{start} --> {end}
{text}

"""
    return "".join(
        SRT_FORMAT.format(
            index=index + 1,
            start=_srt_time(subtitle.start),
            end=_srt_time(subtitle.end),
            text=("{\\a6}" if subtitle.top else "") + subtitle.text,
        )
        for index, subtitle in enumerate(subtitles)
        if subtitle.text
    )


def create_json(subtitles: list[Subtitle]) -> str:
    return (
        json.dumps(
            [
                {
                    "start": subtitle.start.total_seconds(),
                    "end": subtitle.end.total_seconds(),
                    "text": subtitle.text,
                    "top": subtitle.top,
                }
                for subtitle in subtitles
            ],
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )


def create_vtt(subtitles: list[Subtitle]) -> str:
    r"""
    https://developer.mozilla.org/en-US/docs/Web/API/WebVTT_API
    https://w3c.github.io/webvtt/
    https://caniuse.com/?search=vtt
    """
    VTT_FORMAT = """\
{index}
{start} --> {end}{format}
<v active>{active}
<v next>{next}

"""
    BIG_GAP = timedelta(seconds=5)
    BIG_GAP_PREVIEW = timedelta(seconds=3)

    last_end = timedelta(0)
    padded_lines: list[Subtitle] = []
    # Turn each line of source text into one or more lines of output text
    # by inserting blank lines or progress bars as needed
    for line in subtitles:
        gap = line.start - last_end
        if gap > BIG_GAP:
            # If there is a big gap at the start of the track, show nothing
            # until {first line time - $PREVIEW} seconds. At that point, show
            # a blank string as "active" (which causes the first line of the
            # lyrics to be shown as "next")
            if last_end == timedelta(0):
                padded_lines.append(
                    Subtitle(
                        start=line.start - BIG_GAP_PREVIEW,
                        end=line.start,
                        text="",
                        top=line.top,
                    )
                )
            # If there is a big gap in the middle of the track, show a
            # progress bar. Progress bars are made out of pairs of
            #
            #   [   ♫      ]
            #   {first line of next verse}
            #   [     ♫    ]
            #   {first line of next verse}
            #   [       ♫  ]
            #   {first line of next verse}
            #
            # where the "first line of next verse" is set to be zero-length,
            # so that what actually appears on screen is:
            #
            #   active: [   ♫      ]               <-- animated
            #   next: {first line of next verse}   <-- never actually shown as "active"
            else:
                parts = 50
                for n in range(0, parts):
                    g1 = "&nbsp;" * n
                    g2 = "&nbsp;" * (parts - n)
                    padded_lines.append(
                        Subtitle(
                            start=last_end + (gap / parts) * n,
                            end=last_end + (gap / parts) * (n + 1),
                            text=f"[ {g1}♫{g2} ]",
                            top=line.top,
                        )
                    )
                    padded_lines.append(
                        Subtitle(
                            start=last_end + (gap / parts) * (n + 1),
                            end=last_end + (gap / parts) * (n + 1),
                            text=line.text,
                            top=line.top,
                        )
                    )

        # If there is a short gap between line 1 and 2, eg:
        #
        #     1.0: 00:00 -> 00:02 line 1
        #     2.0: 00:04 -> 00:06 line 2
        #
        # we output:
        #
        #     1.0: 00:00 -> 00:02 line 1
        #     1.1: 00:02 -> 00:02 line 2
        #     1.2: 00:02 -> 00:04
        #     2.0: 00:04 -> 00:06 line 2
        #
        # the end result being:
        #
        #   active: line 1
        #   next: line 2       <-- the zero-length line2 shows as "next",
        #                          even though what's actually next is a
        #                          blank space
        #
        #   active:            <-- the gap-length blank line shows as "active"
        #   next: line 2           so that line2 is shown as "next", as opposed
        #                          to showing nothing when there is a gap
        #
        #   active: line 2
        #   next: line 3
        elif gap > timedelta(seconds=0):
            padded_lines.append(
                Subtitle(
                    start=line.start - gap,
                    end=line.start - gap,
                    text=line.text,
                    top=line.top,
                )
            )
            padded_lines.append(
                Subtitle(
                    start=line.start - gap,
                    end=line.start,
                    text="",
                    top=line.top,
                )
            )
        padded_lines.append(line)
        last_end = line.end

    # Add one final blank line because we render in (active line, next line)
    # pairs, and the final line of the lyrics needs to have a "next line" in
    # order to render properly
    padded_lines.append(Subtitle(start=last_end, end=last_end, text=""))

    # Turn the list of lines into a list of (active line, next line) pairs
    #
    # Skip the zero-length "active" lines - these placeholders are only added
    # so that the "next" text will show something useful (the next line of the
    # lyrics) as opposed to showing what is literally next (a blank space or
    # a progress bar)
    pairs = [
        (active, next) for (active, next) in zip(padded_lines[:-1], padded_lines[1:]) if active.start != active.end
    ]

    # Turn the list of (active line, next line) pairs into VTT-formated strings
    blocks = [
        VTT_FORMAT.format(
            index=index,
            start=_vtt_time(active.start),
            end=_vtt_time(active.end),
            format=" line:1" if active.top else "",
            active=active.text,
            next=next.text,
        )
        for index, (active, next) in enumerate(pairs, start=1)
    ]
    return "WEBVTT - KaraKara Subtitle\n\n" + "".join(blocks)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert between subtitle formats")
    parser.add_argument("input", type=str, help="input subtitle file")
    parser.add_argument("output", type=str, help="output subtitle file", nargs="?")
    parser.add_argument("--unblink", action="store_true", help="remove blinking subtitles")
    args = parser.parse_args()
    if args.output is None:
        args.output = args.input

    with open(args.input, "r") as f:
        indata = f.read()
        subs = parse_subtitles(indata)

    if args.unblink:
        for i in range(len(subs) - 1):
            diff = subs[i + 1].start - subs[i].end
            if timedelta(seconds=-0.01) < diff < timedelta(seconds=0.01):
                subs[i] = Subtitle(
                    start=subs[i].start,
                    end=subs[i + 1].start,
                    text=subs[i].text,
                    top=subs[i].top,
                )

    if args.output.endswith(".vtt"):
        outdata = create_vtt(subs)
    elif args.output.endswith(".srt"):
        outdata = create_srt(subs)
    elif args.output.endswith(".ssa"):
        outdata = create_ssa(subs)
    elif args.output.endswith(".json"):
        outdata = create_json(subs)
    else:
        raise SubtitleFormatException("Unknown output format")

    if args.input == args.output:
        diff = difflib.unified_diff(
            indata.splitlines(keepends=True),
            outdata.splitlines(keepends=True),
            fromfile=args.input,
            tofile=args.output,
        )
        print("".join(diff))
    with open(args.output, "w") as f:
        f.write(outdata)
