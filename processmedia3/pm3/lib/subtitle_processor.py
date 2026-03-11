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
from textwrap import dedent

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

    @staticmethod
    def _mk(idx: int, start: float, end: float, text: str, top: bool = False) -> Subtitle:
        return Subtitle(idx=idx, start=SubTime(seconds=start), end=SubTime(seconds=end), text=text, top=top)

    def __str__(self) -> str:
        return f"{self.idx}: {self.start.vtt} -> {self.end.vtt}: {self.text.replace('\n', '\\N')}{' (top)' if self.top else ''}".strip()


class SubFilters:
    @staticmethod
    def remove_blank_lines(lines: list[Subtitle]) -> list[Subtitle]:
        """
        >>> lines = [
        ...     Subtitle._mk(1, 0.000, 1.000, "line 1"),
        ...     Subtitle._mk(2, 1.000, 2.000, ""),
        ...     Subtitle._mk(3, 2.000, 3.000, "line 3"),
        ... ]
        >>> for line in SubFilters.remove_blank_lines(lines):
        ...     print(line)
        1: 00:00:00.000 -> 00:00:01.000: line 1
        3: 00:00:02.000 -> 00:00:03.000: line 3
        """
        return [line for line in lines if line.text]

    @staticmethod
    def fix_aegisub_overlaps(lines: list[Subtitle]) -> list[Subtitle]:
        """
        Aegisub has a bug where lines sometimes overlap or have a gap of <10ms -
        rather than manually fixing these in the source files, let's just assume
        all such cases are unintentional and fix them here.
        https://github.com/TypesettingTools/Aegisub/issues/448

        >>> lines = [
        ...     Subtitle._mk(1, 0.100, 2.000, "line 1"),
        ...     Subtitle._mk(2, 1.999, 4.000, "line 2"), # starts too early
        ...     Subtitle._mk(3, 4.009, 6.000, "line 3"), # starts too late
        ... ]
        >>> for line in SubFilters.fix_aegisub_overlaps(lines):
        ...     print(line)
        1: 00:00:00.100 -> 00:00:01.999: line 1
        2: 00:00:01.999 -> 00:00:04.009: line 2
        3: 00:00:04.009 -> 00:00:06.000: line 3
        """
        if not lines:
            return []
        new_lines = []
        for i in range(len(lines) - 1):
            tdiff = lines[i + 1].start - lines[i].end
            if timedelta(seconds=-0.010) < tdiff < timedelta(seconds=0.010):
                new_lines.append(
                    Subtitle(
                        idx=lines[i].idx,
                        start=lines[i].start,
                        end=lines[i + 1].start,
                        text=lines[i].text,
                        top=lines[i].top,
                    )
                )
            else:
                new_lines.append(lines[i])
        new_lines.append(lines[-1])
        return new_lines

    @staticmethod
    def remove_tiny_gaps(lines: list[Subtitle], gap: timedelta) -> list[Subtitle]:
        """
        Remove tiny gaps between lines, which are distractingly blinky
          AAAAA-BBBBB-CCCCC
        becomes
          AAAAAABBBBBBCCCCC

        >>> lines = [
        ...     Subtitle._mk(1, 0.000, 2.000, "line 1"),
        ...     Subtitle._mk(2, 2.001, 4.000, "line 2"), # tiny gap
        ...     Subtitle._mk(3, 4.100, 6.000, "line 3"), # big gap
        ... ]
        >>> for line in SubFilters.remove_tiny_gaps(lines, timedelta(seconds=0.010)):
        ...     print(line)
        1: 00:00:00.000 -> 00:00:02.001: line 1
        2: 00:00:02.001 -> 00:00:04.000: line 2
        3: 00:00:04.100 -> 00:00:06.000: line 3
        """
        if not lines:
            return []
        new_lines = []
        for i in range(len(lines) - 1):
            tdiff = lines[i + 1].start - lines[i].end
            if tdiff < gap:
                new_lines.append(
                    Subtitle(
                        idx=lines[i].idx,
                        start=lines[i].start,
                        end=lines[i + 1].start,
                        text=lines[i].text,
                        top=lines[i].top,
                    )
                )
            else:
                new_lines.append(lines[i])
        new_lines.append(lines[-1])
        return new_lines

    @staticmethod
    def distinguish_repeats(lines: list[Subtitle], gap: timedelta) -> list[Subtitle]:
        """
        If the same line of lyrics appears twice in a row, insert a
        gap between them so that it's clear when the line is changing,
        the blink is useful in this one specific case
          AAAAAAAAAAAAAAAAA
        becomes
          AAAAA-AAAAA-AAAAA

        >>> lines = [
        ...     Subtitle._mk(1, 0.000, 2.000, "line 1"),
        ...     Subtitle._mk(2, 2.000, 4.000, "line 1"), # same text, no gap
        ...     Subtitle._mk(3, 4.000, 6.000, "line 2"), # different text, no gap
        ...     Subtitle._mk(4, 6.000, 8.000, "line 2"), # same text, no gap
        ...     Subtitle._mk(5, 8.000, 10.000, "line 2"), # same text, no gap
        ... ]
        >>> for line in SubFilters.distinguish_repeats(lines, timedelta(seconds=0.1)):
        ...     print(line)
        1: 00:00:00.000 -> 00:00:01.900: line 1
        2: 00:00:02.000 -> 00:00:04.000: line 1
        3: 00:00:04.000 -> 00:00:05.900: line 2
        4: 00:00:06.000 -> 00:00:07.900: line 2
        5: 00:00:08.000 -> 00:00:10.000: line 2
        """
        if not lines:
            return []
        new_lines = []
        for i in range(len(lines) - 1):
            if lines[i].text == lines[i + 1].text and lines[i].end == lines[i + 1].start:
                new_lines.append(
                    Subtitle(
                        idx=lines[i].idx,
                        start=lines[i].start,
                        end=lines[i + 1].start - gap,
                        text=lines[i].text,
                        top=lines[i].top,
                    )
                )
            else:
                new_lines.append(lines[i])
        new_lines.append(lines[-1])
        return new_lines

    @staticmethod
    def preview_first_line(lines: list[Subtitle], gap: timedelta, preview: timedelta) -> list[Subtitle]:
        """
        If there is a big gap at the start of the track, show nothing
        until {first line time - $PREVIEW} seconds. At that point, show
        a blank string as "active" (which causes the first line of the
        lyrics to be shown as "next")

        so
          ---------AAAA-BBBB-CCCC
          ---------BBBB-CCCC-DDDD
        becomes
          ----    -AAAA-BBBB-CCCC
          ----AAAA-BBBB-CCCC-DDDD

        >>> lines = [
        ...     Subtitle._mk(1, 5.000, 7.000, "line 1"),
        ...     Subtitle._mk(2, 7.000, 9.000, "line 2"),
        ...     Subtitle._mk(3, 9.000, 11.000, "line 3"),
        ... ]
        >>> for line in SubFilters.preview_first_line(lines, timedelta(seconds=3), timedelta(seconds=1)):
        ...     print(line)
        0: 00:00:04.000 -> 00:00:05.000:
        1: 00:00:05.000 -> 00:00:07.000: line 1
        2: 00:00:07.000 -> 00:00:09.000: line 2
        3: 00:00:09.000 -> 00:00:11.000: line 3
        """
        if not lines:
            return []

        if lines[0].start > gap:
            return [
                Subtitle(
                    start=lines[0].start - preview,
                    end=lines[0].start,
                    text="",
                    top=lines[0].top,
                )
            ] + lines
        return lines

    @staticmethod
    def fill_large_gaps(lines: list[Subtitle], big_gap: timedelta, parts: int = 50) -> list[Subtitle]:
        """
        If there is a big gap in the middle of the track, show a
        progress bar. Progress bars are made out of pairs of

          [   ♫      ]
          {first line of next verse}
          [     ♫    ]
          {first line of next verse}
          [       ♫  ]
          {first line of next verse}

        where the "first line of next verse" is set to be zero-length,
        so that what actually appears on screen is:

          active: [   ♫      ]               <-- animated
          next: {first line of next verse}   <-- never actually shown as "active"

        so
          AAAA------BBBB
          BBBB------CCCC
        becomes
          AAAA-[..]-BBBB
          BBBB-BBBB-CCCC

        >>> lines = [
        ...     Subtitle._mk(1, 0.000, 1.000, "line 1"),
        ...     Subtitle._mk(2, 19.000, 20.000, "line 2"),
        ... ]
        >>> for line in SubFilters.fill_large_gaps(lines, timedelta(seconds=3), 3):
        ...     print(line)
        1: 00:00:00.000 -> 00:00:01.000: line 1
        0: 00:00:01.000 -> 00:00:07.000: [ ♫&nbsp;&nbsp; ]
        0: 00:00:07.000 -> 00:00:07.000: line 2
        0: 00:00:07.000 -> 00:00:13.000: [ &nbsp;♫&nbsp; ]
        0: 00:00:13.000 -> 00:00:13.000: line 2
        0: 00:00:13.000 -> 00:00:19.000: [ &nbsp;&nbsp;♫ ]
        0: 00:00:19.000 -> 00:00:19.000: line 2
        2: 00:00:19.000 -> 00:00:20.000: line 2
        """
        if not lines:
            return []

        last_end = lines[0].start
        new_lines: list[Subtitle] = []
        for line in lines:
            gap = line.start - last_end
            if gap > big_gap:
                for n in range(0, parts):
                    g1 = "&nbsp;" * n
                    g2 = "&nbsp;" * (parts - n - 1)
                    new_lines.append(
                        Subtitle(
                            start=last_end + (gap / parts) * n,
                            end=last_end + (gap / parts) * (n + 1),
                            text=f"[ {g1}♫{g2} ]",
                            top=line.top,
                        )
                    )
                    new_lines.append(
                        Subtitle(
                            start=last_end + (gap / parts) * (n + 1),
                            end=last_end + (gap / parts) * (n + 1),
                            text=line.text,
                            top=line.top,
                        )
                    )
            new_lines.append(line)
            last_end = line.end

        return new_lines

    @staticmethod
    def fill_small_gaps(lines: list[Subtitle], big_gap: timedelta) -> list[Subtitle]:
        """
        If there is a short gap between line 1 and 2, eg:

            1.0: 00:00 -> 00:02 text 1
            2.0: 00:04 -> 00:06 text 2

        we output:

            1.0: 00:00 -> 00:02 text 1
            1.1: 00:02 -> 00:02 text 2
            1.2: 00:02 -> 00:04
            2.0: 00:04 -> 00:06 text 2

        the end result being:

          active: text 1
          next: text 2       <-- the zero-length line 1.1 shows as "next",
                                 even though what's actually next is a
                                 blank space

          active:            <-- the gap-length blank line shows as "active"
          next: text 2           so that line2 is shown as "next", as opposed
                                 to showing nothing when there is a gap

          active: text 2
          next: text 3

        so looking at the space between lines
          AAAA--BBBB <-- nothing displayed as "active"
          BBBB--CCCC <-- nothing displayed as "next"
        becomes
          AAAA  BBBB <-- empty string displayed as "active"
          BBBBBBCCCC <-- line B displayed as "next" during the gap

        >>> lines = [
        ...     Subtitle._mk(1, 0.000, 2.000, "line 1"),
        ...     Subtitle._mk(2, 4.000, 6.000, "line 2"), # gap of 2s
        ...     Subtitle._mk(3, 6.000, 8.000, "line 3"), # no gap
        ... ]
        >>> for line in SubFilters.fill_small_gaps(lines, timedelta(seconds=3)):
        ...     print(line)
        1: 00:00:00.000 -> 00:00:02.000: line 1
        0: 00:00:02.000 -> 00:00:02.000: line 2
        0: 00:00:02.000 -> 00:00:04.000:
        2: 00:00:04.000 -> 00:00:06.000: line 2
        3: 00:00:06.000 -> 00:00:08.000: line 3
        """
        if not lines:
            return []

        last_end = lines[0].start
        new_lines: list[Subtitle] = []
        for line in lines:
            gap = line.start - last_end
            if gap > timedelta(seconds=0) and gap < big_gap:
                new_lines.append(
                    Subtitle(
                        start=line.start - gap,
                        end=line.start - gap,
                        text=line.text,
                        top=line.top,
                    )
                )
                new_lines.append(
                    Subtitle(
                        start=line.start - gap,
                        end=line.start,
                        text="",
                        top=line.top,
                    )
                )
            new_lines.append(line)
            last_end = line.end

        return new_lines

    @staticmethod
    def get_pairs(lines: list[Subtitle]) -> list[tuple[Subtitle, Subtitle]]:
        """
        Turn the list of lines into a list of (active line, next line) pairs

        >>> lines = [
        ...     Subtitle._mk(1, 0.000, 2.000, "line 1"),
        ...     Subtitle._mk(2, 2.000, 4.000, "line 2"),
        ...     Subtitle._mk(3, 4.000, 6.000, "line 3"),
        ... ]
        >>> for active, next in SubFilters.get_pairs(lines):
        ...     print(f"active: {active.text}, next: {next.text}".strip())
        active: line 1, next: line 2
        active: line 2, next: line 3
        active: line 3, next:
        """
        if not lines:
            return []

        # Add one final blank line because we render in (active line, next line)
        # pairs, and the final line of the lyrics needs to have a "next line" in
        # order to render properly
        last_end = lines[-1].end
        lines.append(Subtitle(start=last_end, end=last_end, text=""))

        # Skip the zero-length "active" lines - these placeholders are only added
        # so that the "next" text will show something useful (the next line of the
        # lyrics) as opposed to showing what is literally next (a blank space or
        # a progress bar)
        pairs = [(active, next) for (active, next) in zip(lines[:-1], lines[1:]) if active.start != active.end]
        return pairs

    @staticmethod
    def sort_lines(lines: list[Subtitle]) -> list[Subtitle]:
        """
        >>> lines = [
        ...     Subtitle._mk(1, 2.000, 4.000, "line 1"),
        ...     Subtitle._mk(2, 0.000, 2.000, "line 2"),
        ...     Subtitle._mk(3, 4.000, 6.000, "line 3"),
        ... ]
        >>> for line in SubFilters.sort_lines(lines):
        ...     print(line)
        2: 00:00:00.000 -> 00:00:02.000: line 2
        1: 00:00:02.000 -> 00:00:04.000: line 1
        3: 00:00:04.000 -> 00:00:06.000: line 3
        """
        return sorted(lines, key=lambda line: line.start)

    @staticmethod
    def split_top_bottom(lines: list[Subtitle]) -> tuple[list[Subtitle], list[Subtitle]]:
        return ([line for line in lines if line.top], [line for line in lines if not line.top])

    @staticmethod
    def merge_top_bottom(tops: list[Subtitle], bots: list[Subtitle]) -> list[Subtitle]:
        return sorted(tops + bots, key=lambda line: line.start)


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
        1: 00:00:00.000 -> 00:00:01.000: srt

        >>> ssa = '''
        ... Dialogue: Marked=0,0:00:00.00,0:00:01.00,*Default,NTP,0000,0000,0000,!Effect,ssa
        ... '''
        >>> print(SubFile(ssa))
        1: 00:00:00.000 -> 00:00:01.000: ssa

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
        1: 00:00:13.500 -> 00:00:22.343: test, it's, キ
        2: 00:00:22.343 -> 00:00:25.792: second bit (top)

        Test with period as decimal separator (non-standard, but some software with some locale settings does it...):
        >>> srt_period = r'''
        ... 1
        ... 00:00:13.500 --> 00:00:22.343
        ... test with periods
        ... '''
        >>> print(SubFile(srt_period))
        1: 00:00:13.500 -> 00:00:22.343: test with periods
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
        lines = SubFilters.fix_aegisub_overlaps(lines)
        lines = SubFilters.remove_blank_lines(lines)
        return lines

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
        1: 00:00:00.000 -> 00:00:05.000: Ishida Yoko - Towa no Hana\\NAi Yori Aoshi OP (top)
        2: 00:00:07.000 -> 00:00:13.250: awaku saita hana no kao\\Nnokoshi kisetsu wa sugimasu

        >>> ssa = r'''
        ... Dialogue: ,0:00:00.00,0:00:01.00,,,,,,,this is, text on same line
        ... '''
        >>> print(SubFile(ssa))
        1: 00:00:00.000 -> 00:00:01.000: this is, text on same line
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
        data = dedent("""\
            [Script Info]
            Title: <untitled>
            Original Script: <unknown>
            ScriptType: v4.00

            [V4 Styles]
            Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, TertiaryColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, AlphaLevel, Encoding
            Style: Default,Arial,14,65535,16777215,16777215,0,-1,0,3,1,1,2,14,14,14,0,128

            [Events]
            Format: Marked, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
            """)

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
        SRT_FORMAT = dedent("""\
            {idx}
            {start} --> {end}
            {text}

            """)
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
        subtitles = SubFilters.sort_lines(self.subtitles)
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

    def create_vtt(self) -> str:
        r"""
        https://developer.mozilla.org/en-US/docs/Web/API/WebVTT_API
        https://w3c.github.io/webvtt/
        https://caniuse.com/?search=vtt
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
        subtitles = SubFilters.sort_lines(subtitles)

        tops, bots = SubFilters.split_top_bottom(subtitles)
        tops = SubFilters.remove_tiny_gaps(tops, UNBLINK_GAP)
        bots = SubFilters.remove_tiny_gaps(bots, UNBLINK_GAP)
        tops = SubFilters.distinguish_repeats(tops, REPEAT_GAP)
        bots = SubFilters.distinguish_repeats(bots, REPEAT_GAP)
        subtitles = SubFilters.merge_top_bottom(tops, bots)

        subtitles = SubFilters.preview_first_line(subtitles, BIG_GAP, BIG_GAP_PREVIEW)
        subtitles = SubFilters.fill_large_gaps(subtitles, BIG_GAP)
        subtitles = SubFilters.fill_small_gaps(subtitles, BIG_GAP)

        pairs = SubFilters.get_pairs(subtitles)
        # tops, bots = SubFilters.split_top_bottom(subtitles)
        # pairs = SubFilters.get_pairs(tops) + SubFilters.get_pairs(bots)
        # pairs = sorted(pairs, key=lambda pair: pair[0].start)

        # Turn the list of (active line, next line) pairs into VTT-formated strings
        VTT_FORMAT = dedent("""\
            {idx}
            {start} --> {end}{format}
            <v active>{active}
            <v next>{next}

            """)
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
