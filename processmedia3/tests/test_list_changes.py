import unittest

from pm3.cmds.export import list_changes
from pm3.lib.track import TrackDict


class TestListChanges(unittest.TestCase):
    def test_same(self) -> None:
        # identical tracks
        t1: TrackDict = {
            "id": "track1",
            "tags": {
                "title": ["Song A"],
                "category": ["test"],
                "vocaltrack": ["on"],
                "artist": ["Artist A"],
            },
            "duration": 300,
            "attachments": {
                "video": [],
                "image": [],
                "subtitle": [
                    {"mime": "text/srt", "variant": "Default", "path": "subs.srt"},
                ],
            },
            "sources": ["test1.txt", "test.srt", "test1.mp4"],
        }
        t2: TrackDict = {
            "id": "track1",
            "tags": {
                "title": ["Song A"],
                "category": ["test"],
                "vocaltrack": ["on"],
                "artist": ["Artist A"],
            },
            "duration": 300,
            "attachments": {
                "video": [],
                "image": [],
                "subtitle": [
                    {"mime": "text/srt", "variant": "Default", "path": "subs.srt"},
                ],
            },
            "sources": ["test1.txt", "test.srt", "test1.mp4"],
        }
        self.assertEqual(list_changes(t1, t2), None)

    def test_diff_tags_subtitles(self) -> None:
        # tag changes
        t1: TrackDict = {
            "id": "track1",
            "tags": {
                "title": ["Snog A"],
                "category": ["test"],
                "vocaltrack": ["on"],
                "artist": ["Artist A"],
            },
            "duration": 300,
            "attachments": {
                "video": [],
                "image": [],
                "subtitle": [
                    {"mime": "text/srt", "variant": "Default", "path": "subs1.srt"},
                ],
            },
            "sources": ["test1.txt", "test.srt", "test1.mp4"],
        }
        t2: TrackDict = {
            "id": "track1",
            "tags": {
                "title": ["Song A"],
                "category": ["test"],
                "vocaltrack": ["on"],
                "artist": ["Artistee"],
            },
            "duration": 300,
            "attachments": {
                "video": [],
                "image": [],
                "subtitle": [
                    {"mime": "text/srt", "variant": "Default", "path": "subs2.srt"},
                ],
            },
            "sources": ["test1.txt", "test.srt", "test1.mp4"],
        }
        self.assertEqual(list_changes(t1, t2), "tags (artist, title), subtitle")

    def test_diff_new(self) -> None:
        t1: TrackDict = {
            "id": "track1",
            "tags": {
                "title": ["Song A"],
                "artist": ["Artist A"],
                "category": ["anime"],
                "vocaltrack": ["on"],
                "_new": ["new"],
                "new": ["2020-04-16"],
            },
            "duration": 300,
            "attachments": {
                "video": [],
                "image": [],
                "subtitle": [],
            },
            "sources": ["test1.txt", "test.srt", "test1.mp4"],
        }
        t2: TrackDict = {
            "id": "track1",
            "tags": {
                "title": ["Song A"],
                "artist": ["Artist A"],
                "category": ["anime"],
                "vocaltrack": ["on"],
            },
            "duration": 300,
            "attachments": {
                "video": [],
                "image": [],
                "subtitle": [],
            },
            "sources": ["test1.txt", "test.srt", "test1.mp4"],
        }
        self.assertEqual(list_changes(t1, t2), None)
