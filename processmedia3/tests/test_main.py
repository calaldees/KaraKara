import json
import logging
import tempfile
from functools import partialmethod
from pathlib import Path
import unittest
from datetime import datetime

import main
from lib.kktypes import SourceType, TargetType
from tqdm import tqdm

# disable progress bars in unit tests
tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)  # type: ignore


class TestE2E(unittest.TestCase):
    def test_e2e(self):
        logging.basicConfig(level=logging.DEBUG)
        self.maxDiff = 2000

        main.TARGET_TYPES = [
            TargetType.VIDEO_H264,
            TargetType.PREVIEW_H264,
            TargetType.IMAGE_WEBP,
            TargetType.SUBTITLES_VTT,
        ]

        with tempfile.TemporaryDirectory() as processed_str:
            processed = Path(processed_str)

            # Scan should detect source files for two tracks
            tracks = main.scan(Path("./tests/source"), processed, None, {})

            self.assertEqual("Test1", tracks[0].id)
            self.assertEqual(
                {SourceType.TAGS, SourceType.VIDEO, SourceType.SUBTITLES},
                {s.type for s in tracks[0].sources},
            )
            self.assertEqual(TargetType.VIDEO_H264, tracks[0].targets[0].type)
            self.assertEqual("DrH2SWWHaOW", tracks[0].targets[0].path.stem)
            self.assertEqual("Test2", tracks[1].id)

            # Encode should generate output video
            main.encode(tracks)

            self.assertTrue(tracks[0].targets[0].path.exists())

            # Export should generate tracks.json
            main.export(processed, tracks)

            self.assertTrue((processed / "tracks.json").exists())
            tracks_json = json.loads((processed / "tracks.json").read_text())
            self.assertEqual(2, len(tracks_json))

            for k, v in {
                "attachments": {
                    "image": [{"mime": "image/webp", "path": "x/xgkyBqtLHXj.webp"}],
                    "preview": [{"mime": "video/mp4", "path": "7/7px2MuJ4wc8.mp4"}],
                    "subtitle": [{"mime": "text/vtt", "path": "8/8wBGB457jKT.vtt"}],
                    "video": [{"mime": "video/mp4", "path": "d/DrH2SWWHaOW.mp4"}],
                },
                "duration": 30.0,
                "id": "Test1",
                "lyrics": ["Red", "Green", "Blue"],
                "tags": {
                    "aspect_ratio": ["4:3"],
                    "source_type": ["video"],
                    "subs": ["soft"],
                    "artist": ["Artipie"],
                    "category": ["anime"],
                    "contributor": ["ここにいくつかのテキストです。"],
                    "duration": ["0m30s"],
                    "from": ["test series T"],
                    "title": ["Test1"],
                },
            }.items():
                self.assertEqual(v, tracks_json["Test1"][k])
            for k, v in {
                "attachments": {
                    "image": [{"mime": "image/webp", "path": "r/Rck_Khyvlnb.webp"}],
                    "preview": [{"mime": "video/mp4", "path": "l/LxKPtoHpqwi.mp4"}],
                    "subtitle": [{"mime": "text/vtt", "path": "s/saL9lNN0XFx.vtt"}],
                    "video": [{"mime": "video/mp4", "path": "v/vgO9puzSJ60.mp4"}],
                },
                "duration": 15.0,
                "id": "Test2",
                "lyrics": ["AA", "EE"],
                "tags": {
                    "aspect_ratio": ["8:5"],
                    "source_type": ["image"],
                    "subs": ["soft"],
                    "artist": ["Mr Monkey"],
                    "category": ["anime"],
                    "contributor": ["contributor", "ここにいくつかのテキストです。"],
                    "duration": ["0m15s"],
                    "from": ["gundam"],
                    "gundam": ["gundam seed"],
                    "title": ["Test2"],
                },
            }.items():
                self.assertEqual(v, tracks_json["Test2"][k])

            # Cleanup should leave expected tracks alone
            main.cleanup(processed, tracks, True)

            self.assertTrue(tracks[0].targets[0].path.exists())

            # Cleanup with an empty list of expected tracks should
            # clean up the files we created
            main.cleanup(processed, [], True)

            self.assertEqual([], list(processed.glob("*/*")))


if __name__ == "__main__":
    unittest.main()
