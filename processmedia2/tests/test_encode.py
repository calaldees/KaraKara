import os

import pytesseract
from PIL.ImageOps import invert
from PIL.ImageDraw import floodfill

from processmedia_libs.external_tools import get_frame_from_video
from ._base import ScanManager, TEST1_VIDEO_FILES


def test_encode_simple():
    with ScanManager(TEST1_VIDEO_FILES) as scan:
        scan.scan_media()
        scan.encode_media()
        processed_files = scan.processed_files('test1')
        video_file = processed_files['video'][0].absolute

        subtitles = read_subtitles(video_file, 5)
        assert 'Red' in subtitles
        assert 'Green' in subtitles
        assert 'Blue' not in subtitles

        subtitles = read_subtitles(video_file, 15)
        assert 'Red' not in subtitles
        assert 'Green' in subtitles
        assert 'Blue' in subtitles

        #subtitles = read_subtitles(video_file, 25)
        #assert 'Red' not in subtitles
        #assert 'Green' not in subtitles
        #assert 'Blue' in subtitles


def read_subtitles(video_file, time):
    """
    Tesseract is a very limited OCR system.
    It relys on the background for text to be white (sigh)
    So as our subtitles are on a black background if we:
      - Invert our image colors they will be on a white background
      - FloodFill the solid color background with white
    We should be left with more or less the text on a white background.
    """
    image = get_frame_from_video(video_file, time)
    image = invert(image)
    floodfill(image, (100, 100), (255, 255, 255))
    return pytesseract.image_to_string(image)
