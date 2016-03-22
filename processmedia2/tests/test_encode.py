import pytesseract
from PIL import Image

from libs.misc import color_distance, color_close
from processmedia_libs.external_tools import get_frame_from_video
from ._base import ScanManager, TEST1_VIDEO_FILES

COLOR_SUBTITLE_CURRENT = (255, 255, 0)
COLOR_SUBTITLE_NEXT = (255, 255, 255)

COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)

SAMPLE_COORDINATE = (100, 100)


def test_encode_simple():
    with ScanManager(TEST1_VIDEO_FILES) as scan:
        scan.scan_media()
        scan.encode_media()
        processed_files = scan.processed_files('test1')
        video_file = processed_files['video'][0].absolute

        image = get_frame_from_video(video_file, 5)
        assert color_close(COLOR_RED, image.getpixel(SAMPLE_COORDINATE))
        assert 'Red' == read_subtitle_text(image, COLOR_SUBTITLE_CURRENT)
        assert 'Green' == read_subtitle_text(image, COLOR_SUBTITLE_NEXT)

        image = get_frame_from_video(video_file, 15)
        assert color_close(COLOR_GREEN, image.getpixel(SAMPLE_COORDINATE))
        assert 'Green' == read_subtitle_text(image, COLOR_SUBTITLE_CURRENT)
        assert 'Blue' == read_subtitle_text(image, COLOR_SUBTITLE_NEXT)

        image = get_frame_from_video(video_file, 25)
        assert color_close(COLOR_BLUE, image.getpixel(SAMPLE_COORDINATE))
        assert 'Blue' == read_subtitle_text(image, COLOR_SUBTITLE_CURRENT)
        assert not read_subtitle_text(image, COLOR_SUBTITLE_NEXT)


def read_subtitle_text(image, color):
    return pytesseract.image_to_string(extract_image_color(image, color)).strip()


def extract_image_color(source, color, threshold=50):
    target = Image.new('L', source.size)
    for x in range(source.size[0]):
        for y in range(source.size[1]):
            distance = color_distance(color, source.getpixel((x, y)), threshold=threshold)
            target.putpixel((x, y), distance if distance is not None else 255)
    return target
