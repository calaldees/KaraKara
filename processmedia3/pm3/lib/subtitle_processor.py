#!/usr/bin/env python
## -*- coding: utf-8 -*-

import difflib
import json
import logging
import re
import typing as t
from datetime import timedelta
from itertools import zip_longest
from pathlib import Path

log = logging.getLogger(__name__)


class SubtitleParseException(Exception):
    pass


class SubtitleFormatException(Exception):
    pass


class SubTime(timedelta):
    @classmethod
    def from_str(cls, time_str: str) -> SubTime:
        """
        >>> SubTime.from_str('  1:23:45.6700  ')
        SubTime(seconds=5025, microseconds=670000)
        >>> SubTime.from_str('1:23:45,67')
        SubTime(seconds=5025, microseconds=670000)
        >>> SubTime.from_str('1:02:03.05')
        SubTime(seconds=3723, microseconds=50000)
        >>> SubTime.from_str('1:02:03.05').ssa
        '1:02:03.05'
        >>> SubTime.from_str('0:00:60.50')
        SubTime(seconds=60, microseconds=500000)
        >>> SubTime.from_str('0:59:60.1000001')
        SubTime(seconds=3600, microseconds=100000)
        """
        match = SubFile.re_time.search(time_str)
        if not match:
            raise SubtitleParseException(f"Can't parse time: {time_str}")
        time_dict = match.groupdict()
        return cls(
            hours=int(time_dict["hours"]),
            minutes=int(time_dict["minutes"]),
            seconds=float(time_dict["seconds"].replace(",", ".")),
        )

    def __add__(self, other: timedelta, /) -> SubTime:
        return SubTime(seconds=super().__add__(other).total_seconds())

    def __sub__(self, other: timedelta, /) -> SubTime:
        return SubTime(seconds=super().__sub__(other).total_seconds())

    def __mul__(self, other: int | float, /) -> SubTime:
        return SubTime(seconds=super().__mul__(other).total_seconds())

    @t.overload
    def __truediv__(self, value: timedelta, /) -> float: ...

    @t.overload
    def __truediv__(self, value: int | float, /) -> SubTime: ...

    def __truediv__(self, value: timedelta | int | float, /) -> SubTime | float:
        result = super().__truediv__(value)
        if isinstance(result, float) or isinstance(result, int):
            return result
        return SubTime(seconds=result.total_seconds())

    @property
    def srt(self) -> str:
        """
        >>> SubTime(hours=1, minutes=23, seconds=45, microseconds=671000).srt
        '01:23:45,671'
        >>> SubTime(hours=0, minutes=0, seconds=0, microseconds=0).srt
        '00:00:00,000'
        >>> SubTime(hours=1, minutes=2, seconds=3, microseconds=50000).srt
        '01:02:03,050'
        """
        return "{:02d}:{:02d}:{:06.03f}".format(
            self.seconds // 60 // 60,
            (self.seconds % (60 * 60)) // 60,
            self.seconds % 60 + self.microseconds / 1000000,
        ).replace(".", ",")

    @property
    def ssa(self) -> str:
        """
        >>> SubTime(hours=1, minutes=23, seconds=45, microseconds=671000).ssa
        '1:23:45.67'
        >>> SubTime(hours=0, minutes=0, seconds=0, microseconds=0).ssa
        '0:00:00.00'
        >>> SubTime(hours=1, minutes=2, seconds=3, microseconds=50000).ssa
        '1:02:03.05'
        """
        return "{}:{:02d}:{:05.02f}".format(
            self.seconds // 60 // 60,
            (self.seconds % (60 * 60)) // 60,
            self.seconds % 60 + self.microseconds / 1000000,
        )

    @property
    def vtt(self) -> str:
        """
        >>> SubTime(hours=1, minutes=23, seconds=45, microseconds=671000).vtt
        '01:23:45.671'
        >>> SubTime(hours=0, minutes=0, seconds=0, microseconds=0).vtt
        '00:00:00.000'
        >>> SubTime(hours=1, minutes=2, seconds=3, microseconds=50000).vtt
        '01:02:03.050'
        """
        return "{:02d}:{:02d}:{:06.03f}".format(
            self.seconds // 60 // 60,
            (self.seconds % (60 * 60)) // 60,
            self.seconds % 60 + self.microseconds / 1000000,
        )


class Subtitle(t.NamedTuple):
    idx: int = 0
    start: SubTime = SubTime()
    end: SubTime = SubTime()
    text: str = ""
    top: bool = False

    def __str__(self) -> str:
        return f"{self.idx}: {self.start} -> {self.end}: {self.text.replace('\n', '\\N')}{' (top)' if self.top else ''}".strip()


class SubFile:
    """A class representing a subtitle file with methods for manipulating and exporting subtitles."""

    SSA_NEWLINE = "\\N"
    SSA_NEXT_COLOR = "{\\c&HFFFFFF&}"

    re_time = re.compile(r"(?P<hours>\d{1,2}):(?P<minutes>\d{2}):(?P<seconds>\d{2}[\.,]\d+)")
    re_srt_line = re.compile(
        r"(?P<idx>\d+)\n(?P<start>[\d:,\.]+) --> (?P<end>[\d:,\.]+)\n(?P<text>.*?)(\n\n|$)",
        flags=re.DOTALL,
    )
    re_ssa_line = re.compile(
        r"Dialogue:.+?,(?P<start>.+?),(?P<end>.+?),(?P<style>.*?),(?P<name>.*?),(?P<marginL>.*?),(?P<marginR>.*?),(?P<marginV>.*?),(?P<effect>.*?),(?P<text>.+)[\n$]"
    )

    def __init__(self, data: str):
        """
        >>> srt = '''
        ... 1
        ... 00:00:00,000 --> 00:00:01,000
        ... srt
        ... '''
        >>> print(SubFile(srt))
        1: 0:00:00 -> 0:00:01: srt

        >>> ssa = '''
        ... Dialogue: Marked=0,0:00:00.00,0:00:01.00,*Default,NTP,0000,0000,0000,!Effect,ssa
        ... '''
        >>> print(SubFile(ssa))
        1: 0:00:00 -> 0:00:01: ssa

        >>> print(SubFile('not real subtitles'))
        <BLANKLINE>
        """
        self.subtitles = self._parse_srt(data) or self._parse_ssa(data)

    def __str__(self) -> str:
        return "\n".join(str(subtitle) for subtitle in self.subtitles)

    @staticmethod
    def _parse_srt(source: str) -> list[Subtitle]:
        """
        >>> srt = r'''
        ... 1
        ... 00:00:13,500 --> 00:00:22,343
        ... test, it's, キ
        ...
        ... 2
        ... 00:00:22,343 --> 00:00:25,792
        ... ^second bit
        ...
        ... 3
        ... 00:00:30,000 --> 00:00:40,000
        ...
        ...
        ... '''
        >>> print(SubFile(srt))
        1: 0:00:13.500000 -> 0:00:22.343000: test, it's, キ
        2: 0:00:22.343000 -> 0:00:25.792000: second bit (top)

        Test with period as decimal separator (non-standard, but some software with some locale settings does it...):
        >>> srt_period = r'''
        ... 1
        ... 00:00:13.500 --> 00:00:22.343
        ... test with periods
        ... '''
        >>> print(SubFile(srt_period))
        1: 0:00:13.500000 -> 0:00:22.343000: test with periods
        """

        def parse_line(line: dict[str, str]) -> Subtitle:
            return Subtitle(
                int(line["idx"]),
                SubTime.from_str(line["start"]),
                SubTime.from_str(line["end"]),
                line["text"].lstrip("^"),
                line["text"].startswith("^"),
            )

        lines = [parse_line(line_match.groupdict()) for line_match in SubFile.re_srt_line.finditer(source)]

        # Aegisub has a bug where lines sometimes overlap or have a gap of <10ms -
        # rather than manually fixing these in the source files, let's just assume
        # all such cases are unintentional and fix them here.
        # https://github.com/TypesettingTools/Aegisub/issues/448
        for i in range(len(lines) - 1):
            tdiff = lines[i + 1].start - lines[i].end
            if timedelta(seconds=-0.010) < tdiff < timedelta(seconds=0.010):
                lines[i] = Subtitle(
                    idx=lines[i].idx,
                    start=lines[i].start,
                    end=lines[i + 1].start,
                    text=lines[i].text,
                    top=lines[i].top,
                )

        return [line for line in lines if line.text]

    @staticmethod
    def _parse_ssa(source: str) -> list[Subtitle]:
        """
        >>> ssa = r'''
        ... [Events]
        ... Format: Marked, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
        ... Dialogue: Marked=0,0:00:00.00,0:00:05.00,*Default,NTP,0000,0000,0000,!Effect,{\\a6}Ishida Yoko - {\\c&HFFFF00&}Towa no Hana{\\c&HFFFF&}\\N{\\c&HFFFFFF&}{\\c&H8080FF&}Ai Yori Aoshi OP
        ... Dialogue: Marked=0,0:00:07.00,0:00:13.25,*Default,NTP,0000,0000,0000,!Effect,awaku saita hana no kao\\N{\\c&HFFFFFF&}nokoshi kisetsu wa sugimasu
        ... '''
        >>> print(SubFile(ssa))
        1: 0:00:00 -> 0:00:05: Ishida Yoko - Towa no Hana\\NAi Yori Aoshi OP (top)
        2: 0:00:07 -> 0:00:13.250000: awaku saita hana no kao\\Nnokoshi kisetsu wa sugimasu

        >>> ssa = r'''
        ... Dialogue: ,0:00:00.00,0:00:01.00,,,,,,,this is, text on same line
        ... '''
        >>> print(SubFile(ssa))
        1: 0:00:00 -> 0:00:01: this is, text on same line
        """
        lines = [line_match.groupdict() for line_match in SubFile.re_ssa_line.finditer(source)]

        def strip_formatting(text: str) -> str:
            text = re.sub(r"{.*?}", "", text)
            return "\n".join(l.strip() for l in text.split("\\N"))

        def parse_line(line: dict[str, str], idx: int) -> Subtitle:
            return Subtitle(
                idx,
                SubTime.from_str(line["start"]),
                SubTime.from_str(line["end"]),
                strip_formatting(line["text"]),
                "\\a6" in line["text"] or "\\an8" in line["text"],
            )

        return [parse_line(line_dict, i + 1) for i, line_dict in enumerate(lines)]

    def create_ssa(self) -> str:
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

        for subtitle, subtitle_next in zip_longest(self.subtitles, self.subtitles[1:]):
            text = (
                "{}{}{}{}".format(
                    subtitle.text,
                    SubFile.SSA_NEWLINE,
                    SubFile.SSA_NEXT_COLOR,
                    subtitle_next.text,
                )
                if subtitle_next
                else subtitle.text
            ).replace("\n", SubFile.SSA_NEWLINE)
            data += f"Dialogue: Marked=0,{subtitle.start.ssa},{subtitle.end.ssa},*Default,NTP,0000,0000,0000,!Effect,{text}\n"
        return data

    def create_srt(self) -> str:
        SRT_FORMAT = """\
{idx}
{start} --> {end}
{text}

"""
        return "".join(
            SRT_FORMAT.format(
                idx=idx,
                start=subtitle.start.srt,
                end=subtitle.end.srt,
                text=("^" if subtitle.top else "") + subtitle.text,
            )
            for idx, subtitle in enumerate(self.subtitles, 1)
            if subtitle.text
        )

    def create_json(self) -> str:
        return (
            json.dumps(
                [
                    {
                        "start": subtitle.start.total_seconds(),
                        "end": subtitle.end.total_seconds(),
                        "text": subtitle.text,
                        "top": subtitle.top,
                    }
                    for subtitle in self.subtitles
                ],
                indent=2,
                ensure_ascii=False,
            )
            + "\n"
        )

    def create_vtt(self) -> str:
        r"""
        https://developer.mozilla.org/en-US/docs/Web/API/WebVTT_API
        https://w3c.github.io/webvtt/
        https://caniuse.com/?search=vtt
        """
        VTT_FORMAT = """\
{idx}
{start} --> {end}{format}
<v active>{active}
<v next>{next}

"""
        # remove gaps smaller than this
        UNBLINK_GAP = timedelta(seconds=0.250)
        # if the same line of lyrics appears twice in a row
        # back-to-back, insert a gap of this length
        REPEAT_GAP = timedelta(seconds=0.100)
        # if there's a gap larger than this between lines,
        # show a progress bar as well as the upcoming line
        BIG_GAP = timedelta(seconds=5)
        # if there's a gap bigger than BIG_GAP at the start, show
        # upcoming-line this early before it becomes current-line
        BIG_GAP_PREVIEW = timedelta(seconds=3)

        subtitles = list(self.subtitles)  # Make a copy to avoid modifying the original

        # Remove tiny gaps between lines, which are distractingly blinky
        #   AAAAA-BBBBB-CCCCC
        # becomes
        #   AAAAAABBBBBBCCCCC
        for i in range(len(subtitles) - 1):
            tdiff = subtitles[i + 1].start - subtitles[i].end
            if tdiff < UNBLINK_GAP:
                subtitles[i] = Subtitle(
                    idx=subtitles[i].idx,
                    start=subtitles[i].start,
                    end=subtitles[i + 1].start,
                    text=subtitles[i].text,
                    top=subtitles[i].top,
                )

        # If the same line of lyrics appears twice in a row, insert a
        # gap between them so that it's clear when the line is changing,
        # the blink is useful in this one specific case
        #   AAAAAAAAAAAAAAAAA
        # becomes
        #   AAAAA-AAAAA-AAAAA
        for i in range(len(subtitles) - 1):
            if subtitles[i].text == subtitles[i + 1].text and subtitles[i].end == subtitles[i + 1].start:
                subtitles[i] = Subtitle(
                    idx=subtitles[i].idx,
                    start=subtitles[i].start,
                    end=subtitles[i + 1].start - REPEAT_GAP,
                    text=subtitles[i].text,
                    top=subtitles[i].top,
                )

        last_end = SubTime(0)
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
                #
                # so
                #   ---------AAAA-BBBB-CCCC
                #   ---------BBBB-CCCC-DDDD
                # becomes
                #   ----    -AAAA-BBBB-CCCC
                #   ----AAAA-BBBB-CCCC-DDDD
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
                #
                # so
                #   AAAA------BBBB
                #   BBBB------CCCC
                # becomes
                #   AAAA-[..]-BBBB
                #   BBBB-BBBB-CCCC
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
            #
            # so
            #   AAAA--BBBB <-- nothing displayed during the gap
            #   BBBB--CCCC
            # becomes
            #   AAAA  BBBB <-- empty string displayed as "active" (so that the next
            #   BBBBBBCCCC     line of the lyrics is shown as "next") during the gap
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
                idx=idx,
                start=active.start.vtt,
                end=active.end.vtt,
                format=" line:1" if active.top else "",
                active=active.text,
                next=next.text,
            )
            for idx, (active, next) in enumerate(pairs, start=1)
        ]
        return "WEBVTT - KaraKara Subtitle\n\n" + "".join(blocks)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Convert between subtitle formats")
    parser.add_argument("input", type=Path, help="input subtitle file")
    parser.add_argument("output", type=Path, help="output subtitle file", nargs="?")
    args = parser.parse_args()
    if args.output is None:
        args.output = args.input

    indata = args.input.read_text()
    subfile = SubFile(indata)

    if args.output.endswith(".vtt"):
        outdata = subfile.create_vtt()
    elif args.output.endswith(".srt"):
        outdata = subfile.create_srt()
    elif args.output.endswith(".ssa"):
        outdata = subfile.create_ssa()
    elif args.output.endswith(".json"):
        outdata = subfile.create_json()
    else:
        raise SubtitleFormatException("Unknown output format")

    if args.input == args.output:
        linediff = difflib.unified_diff(
            indata.splitlines(keepends=True),
            outdata.splitlines(keepends=True),
            fromfile=args.input,
            tofile=args.output,
        )
        print("".join(linediff))
    args.output.write_text(outdata)


if __name__ == "__main__":
    main()
