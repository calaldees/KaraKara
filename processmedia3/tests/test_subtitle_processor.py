## -*- coding: utf-8 -*-

import unittest
from datetime import timedelta
from lib.subtitle_processor import (
    create_srt,
    create_ssa,
    create_vtt,
    Subtitle,
    _remove_duplicate_lines,
    parse_subtitles,
)
from pathlib import Path


class TestCreateSsa(unittest.TestCase):
    def test_create_ssa(self) -> None:
        ssa = create_ssa(
            (
                Subtitle(timedelta(minutes=0), timedelta(minutes=1), "first"),
                Subtitle(
                    timedelta(minutes=2),
                    timedelta(minutes=3, microseconds=510000),
                    "second",
                ),
            )
        )
        self.assertEqual(
            ssa,
            r"""[Script Info]
Title: <untitled>
Original Script: <unknown>
ScriptType: v4.00

[V4 Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, TertiaryColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, AlphaLevel, Encoding
Style: Default,Arial,14,65535,16777215,16777215,0,-1,0,3,1,1,2,14,14,14,0,128

[Events]
Format: Marked, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: Marked=0,0:00:00.00,0:01:00.00,*Default,NTP,0000,0000,0000,!Effect,first\N{\c&HFFFFFF&}second
Dialogue: Marked=0,0:02:00.00,0:03:00.51,*Default,NTP,0000,0000,0000,!Effect,second
""",
        )

        self.assertEqual(
            _remove_duplicate_lines(parse_subtitles(ssa)),
            [
                Subtitle(
                    start=timedelta(0),
                    end=timedelta(seconds=60),
                    text="first",
                    top=False,
                ),
                Subtitle(
                    start=timedelta(seconds=120),
                    end=timedelta(seconds=180, microseconds=510000),
                    text="second",
                    top=False,
                ),
            ],
        )

    def test_newline(self) -> None:
        ssa = create_ssa(
            (Subtitle(timedelta(minutes=0), timedelta(minutes=1), "newline\ntest"),)
        )
        self.assertIn("newline\\Ntest", ssa)


class TestCreateSrt(unittest.TestCase):
    def test_create_srt(self) -> None:
        srt = create_srt(
            (
                Subtitle(timedelta(minutes=0), timedelta(minutes=1), "first"),
                Subtitle(
                    timedelta(minutes=2),
                    timedelta(minutes=3, microseconds=510000),
                    "second",
                ),
                Subtitle(timedelta(minutes=4), timedelta(minutes=5), ""),
            )
        )
        self.assertEqual(
            srt,
            """1
00:00:00,000 --> 00:01:00,000
first

2
00:02:00,000 --> 00:03:00,510
second

""",
        )
        self.assertEqual(
            parse_subtitles(srt),
            [
                Subtitle(
                    start=timedelta(0),
                    end=timedelta(seconds=60),
                    text="first",
                    top=False,
                ),
                Subtitle(
                    start=timedelta(seconds=120),
                    end=timedelta(seconds=180, microseconds=510000),
                    text="second",
                    top=False,
                ),
            ],
        )


class TestCreateVtt(unittest.TestCase):
    def test_files(self) -> None:
        self.maxDiff = 1000
        for case in Path("tests/subs").glob("*.srt"):
            with self.subTest(case.stem):
                srt_data = case.read_text()
                vtt_data = case.with_suffix(".vtt").read_text()
                self.assertEqual(vtt_data, create_vtt(parse_subtitles(srt_data)))
