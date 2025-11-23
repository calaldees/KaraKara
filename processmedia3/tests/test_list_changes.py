import unittest
from pm3.cmds.export import list_changes
from pm3.lib.track import TrackDict, MediaType


class TestCreateSsa(unittest.TestCase):
    def test_same(self) -> None:
        # identical tracks
        t1: TrackDict = {
            "id": "track1",
            "tags": {"title": ["Song A"], "artist": ["Artist A"]},
            "duration": 300,
            "attachments": {
                MediaType.SUBTITLE: [
                    {"mime": "text/srt", "variant": None, "path": "subs.srt"},
                ],
            },
        }
        t2: TrackDict = {
            "id": "track1",
            "tags": {"title": ["Song A"], "artist": ["Artist A"]},
            "duration": 300,
            "attachments": {
                MediaType.SUBTITLE: [
                    {"mime": "text/srt", "variant": None, "path": "subs.srt"},
                ],
            },
        }
        self.assertEqual(list_changes(t1, t2), None)

    def test_diff_tags_subtitles(self) -> None:
        # tag changes
        t1: TrackDict = {
            "id": "track1",
            "tags": {"title": ["Snog A"], "artist": ["Artist A"]},
            "duration": 300,
            "attachments": {
                MediaType.SUBTITLE: [
                    {"mime": "text/srt", "variant": None, "path": "subs1.srt"},
                ],
            },
        }
        t2: TrackDict = {
            "id": "track1",
            "tags": {"title": ["Song A"], "artist": ["Artistee"]},
            "duration": 300,
            "attachments": {
                MediaType.SUBTITLE: [
                    {"mime": "text/srt", "variant": None, "path": "subs2.srt"},
                ],
            },
        }
        self.assertEqual(list_changes(t1, t2), "tags (artist, title), subtitle")

    def test_diff_new(self) -> None:
        t1: TrackDict = {
            "id": "track1",
            "tags": {
                "title": ["Song A"],
                "artist": ["Artist A"],
                "category": ["anime", "new"],
                "new": ["2020-04-16"],
            },
            "duration": 300,
            "attachments": {},
        }
        t2: TrackDict = {
            "id": "track1",
            "tags": {
                "title": ["Song A"],
                "artist": ["Artist A"],
                "category": ["anime"],
            },
            "duration": 300,
            "attachments": {},
        }
        self.assertEqual(list_changes(t1, t2), None)
