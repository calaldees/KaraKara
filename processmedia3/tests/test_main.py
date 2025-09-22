import json
import logging
import tempfile
from functools import partialmethod
from pathlib import Path
import unittest

import main
from lib.source import SourceType
from lib.kktypes import TargetType
from lib.file_abstraction import AbstractFolder_from_str
from tqdm import tqdm

# disable progress bars in unit tests
tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)  # type: ignore


class TestE2E(unittest.TestCase):
    def test_e2e(self) -> None:
        logging.basicConfig(level=logging.DEBUG)
        self.maxDiff = 2000

        main.TARGET_TYPES = [
            TargetType.VIDEO_AV1,
            TargetType.IMAGE_AVIF,
            TargetType.SUBTITLES_VTT,
        ]

        with tempfile.TemporaryDirectory() as processed_str:
            processed = Path(processed_str)

            # Scan should detect source files for two tracks
            tracks = main.scan(AbstractFolder_from_str("./tests/source"), processed, '', {})

            self.assertEqual("Test1", tracks[0].id)
            self.assertEqual(
                {SourceType.TAGS, SourceType.VIDEO, SourceType.SUBTITLES},
                {s.type for s in tracks[0].sources},
            )
            self.assertEqual(TargetType.VIDEO_AV1, tracks[0].targets[0].type)
            self.assertEqual('QbcWNbOP07G', tracks[0].targets[0].path.stem)
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
                    "image": [{"variant": None, "mime": "image/avif", "path": "a/AFJz1z_uAoG.avif"}],
                    "subtitle": [{"variant": None, "mime": "text/vtt", "path": "g/gHe0erd2h5b.vtt"}],
                    'video': [{"variant": None, 'mime': 'video/webm; codecs=av01.0.05M.08,opus', 'path': 'q/QbcWNbOP07G.webm'}]
                },
                "duration": 30.0,
                "id": "Test1",
                "tags": {
                    "aspect_ratio": ["4:3"],
                    "source_type": ["video"],
                    "subs": ["soft"],
                    "artist": ["Artipie"],
                    "category": ["anime"],
                    "contributor": ["ここにいくつかのテキストです。"],
                    "from": ["test series T"],
                    "title": ["Test1"],
                },
            }.items():
                self.assertEqual(v, tracks_json["Test1"][k])
            for k, v in {
                "attachments": {
                    "image": [{"variant": None, "mime": "image/avif", "path": "g/g0hYJlNw99D.avif"}],
                    "subtitle": [{"variant": None, "mime": "text/vtt", "path": "6/6u2Zuq6Cuho.vtt"}],
                    "video": [{"variant": None, 'mime': 'video/webm; codecs=av01.0.05M.08,opus', 'path': 'k/kQiTVqqX7if.webm'}],
                },
                "duration": 15.0,
                "id": "Test2",
                "tags": {
                    "aspect_ratio": ["8:5"],
                    "source_type": ["image"],
                    "subs": ["soft"],
                    "artist": ["Mr Monkey"],
                    "category": ["anime"],
                    "contributor": ["contributor", "ここにいくつかのテキストです。"],
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
