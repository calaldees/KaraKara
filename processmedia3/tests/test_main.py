import testslide
from tqdm import tqdm
from functools import partialmethod
import os
import logging
import glob
import tempfile
from pathlib import Path
import json

import main
import lib.kktypes

# disable progress bars in unit tests
tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)


class TestE2E(testslide.TestCase):
    def test_e2e(self):
        logging.basicConfig(level=logging.DEBUG)

        main.TARGET_TYPES = [
            lib.kktypes.TargetType.VIDEO_H264,
            lib.kktypes.TargetType.PREVIEW_H264,
            lib.kktypes.TargetType.IMAGE_WEBP,
            lib.kktypes.TargetType.SUBTITLES_VTT,
        ]

        with tempfile.TemporaryDirectory() as processed_str:
            processed = Path(processed_str)

            # Scan should detect source files for two tracks
            tracks = main.scan(Path("./tests/source"), processed, None, {})

            self.assertEqual(tracks[0].id, "test1")
            self.assertEqual(tracks[0].sources[0].type, lib.kktypes.SourceType.TAGS)
            self.assertEqual(
                tracks[0].targets[0].type, lib.kktypes.TargetType.VIDEO_H264
            )
            self.assertEqual(tracks[0].targets[0].path.stem, "XJ8S5jgxf_t")
            self.assertEqual(tracks[1].id, "test2")

            # Encode should generate output video
            main.encode(tracks)

            self.assertTrue(tracks[0].targets[0].path.exists())

            # Export should generate tracks.json
            main.export(processed, tracks)

            self.assertTrue((processed / "tracks.json").exists())
            tracks_json = json.loads((processed / "tracks.json").read_text())
            self.assertEqual(len(tracks_json), 2)

            for k, v in {
                "attachments": {
                    "image": [{"mime": "image/webp", "path": "X/XJ8S5jgxf_t.webp"}],
                    "preview": [{"mime": "video/mp4", "path": "q/qCVsvIU9PXx.mp4"}],
                    "subtitle": [{"mime": "text/vtt", "path": "i/iukvP6xESdF.vtt"}],
                    "video": [{"mime": "video/mp4", "path": "X/XJ8S5jgxf_t.mp4"}],
                },
                "duration": 30.0,
                "id": "test1",
                "lyrics": ["Red", "Green", "Blue"],
                "tags": {
                    "artist": ["Artipie"],
                    "category": ["anime"],
                    "contributor": ["ここにいくつかのテキストです。"],
                    "from": ["test series T"],
                    "title": ["Test1"],
                },
            }.items():
                self.assertEqual(tracks_json["test1"][k], v)
            for k, v in {
                "attachments": {
                    "image": [{"mime": "image/webp", "path": "F/FvGE73IaZ0C.webp"}],
                    "preview": [{"mime": "video/mp4", "path": "F/FvGE73IaZ0C.mp4"}],
                    "subtitle": [{"mime": "text/vtt", "path": "P/P0d_GoFdj8S.vtt"}],
                    "video": [{"mime": "video/mp4", "path": "F/FvGE73IaZ0C.mp4"}],
                },
                "duration": 15.0,
                "id": "test2",
                "lyrics": ["AA", "EE"],
                "tags": {
                    "artist": ["Mr Monkey"],
                    "category": ["anime"],
                    "contributor": ["contributor", "ここにいくつかのテキストです。"],
                    "from": ["gundam"],
                    "gundam": ["gundam seed"],
                    "title": ["Test2"],
                },
            }.items():
                self.assertEqual(tracks_json["test2"][k], v)

            # Cleanup should leave expected tracks alone
            main.cleanup(processed, tracks, True)

            self.assertTrue(tracks[0].targets[0].path.exists())

            # Cleanup with an empty list of expected tracks should
            # clean up the files we created
            main.cleanup(processed, [], True)

            self.assertEqual(list(processed.glob("*/*")), [])
