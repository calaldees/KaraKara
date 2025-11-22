import unittest
from cmds.export import list_changes
from lib.track import TrackDict


class TestCreateSsa(unittest.TestCase):
    def test_same(self) -> None:
        t1: TrackDict = {
            "id": "track1",
            "tags": {"title": ["Song A"], "artist": ["Artist A"]},
            "duration": 300,
            "attachments": {
                "subtitle": [
                    {"mime": "text/srt", "variant": None, "path": "subs.srt"},
                ],
            },
        }
        t2: TrackDict = {
            "id": "track1",
            "tags": {"title": ["Song A"], "artist": ["Artist A"]},
            "duration": 300,
            "attachments": {
                "subtitle": [
                    {"mime": "text/srt", "variant": None, "path": "subs.srt"},
                ],
            },
        }
        self.assertEqual(list_changes(t1, t2), None)

    def test_diff(self) -> None:
        t1: TrackDict = {
            "id": "track1",
            "tags": {"title": ["Song A"], "artist": ["Artist A"]},
            "duration": 300,
            "attachments": {
                "subtitle": [
                    {"mime": "text/srt", "variant": None, "path": "subs1.srt"},
                ],
            },
        }
        t2: TrackDict = {
            "id": "track2",
            "tags": {"title": ["Song B"], "artist": ["Artist B"]},
            "duration": 300,
            "attachments": {
                "subtitle": [
                    {"mime": "text/srt", "variant": None, "path": "subs2.srt"},
                ],
            },
        }
        self.assertEqual(list_changes(t1, t2), None)
