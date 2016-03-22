import pytesseract
from PIL import Image

from libs.misc import color_distance
from processmedia_libs.external_tools import get_frame_from_video
from ._base import ScanManager, TEST1_VIDEO_FILES

COLOR_SUBTITLE_CURRENT = (255, 255, 0)
COLOR_SUBTITLE_NEXT = (255, 255, 255)


def test_encode_simple():
    with ScanManager(TEST1_VIDEO_FILES) as scan:
        scan.scan_media()
        scan.encode_media()
        processed_files = scan.processed_files('test1')
        video_file = processed_files['video'][0].absolute

        assert 'Red' == read_subtitle_text(video_file, 5, COLOR_SUBTITLE_CURRENT)
        assert 'Green' == read_subtitle_text(video_file, 5, COLOR_SUBTITLE_NEXT)

        assert 'Green' == read_subtitle_text(video_file, 15, COLOR_SUBTITLE_CURRENT)
        assert 'Blue' == read_subtitle_text(video_file, 15, COLOR_SUBTITLE_NEXT)

        assert 'Blue' == read_subtitle_text(video_file, 25, COLOR_SUBTITLE_CURRENT)
        assert not read_subtitle_text(video_file, 25, COLOR_SUBTITLE_NEXT)


def read_subtitle_text(video_file, time, color):
    return pytesseract.image_to_string(extract_image_color(get_frame_from_video(video_file, time), color)).strip()


def extract_image_color(source, color, threshold=50):
    target = Image.new('L', source.size)
    for x in range(source.size[0]):
        for y in range(source.size[1]):
            distance = color_distance(color, source.getpixel((x, y)), threshold=threshold)
            target.putpixel((x, y), distance if distance is not None else 255)
    return target
