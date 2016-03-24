import pytesseract
from PIL import Image

from libs.misc import color_distance, color_close
from processmedia_libs.external_tools import get_frame_from_video
from ._base import ScanManager, TEST1_VIDEO_FILES, TEST2_AUDIO_FILES

COLOR_SUBTITLE_CURRENT = (255, 255, 0)
COLOR_SUBTITLE_NEXT = (255, 255, 255)

COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)

SAMPLE_COORDINATE = (100, 100)


def test_encode_video_simple():
    with ScanManager(TEST1_VIDEO_FILES) as scan:
        scan.scan_media()
        scan.encode_media()
        processed_files = scan.processed_files('test1')

        # Main Video - use OCR to read subtiles and check them
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

        # Preview Video (can't check subtitles as the res is too small)
        preview_file = processed_files['preview'][0].absolute

        image = get_frame_from_video(preview_file, 5)
        assert color_close(COLOR_RED, image.getpixel(SAMPLE_COORDINATE))

        image = get_frame_from_video(preview_file, 15)
        assert color_close(COLOR_GREEN, image.getpixel(SAMPLE_COORDINATE))

        image = get_frame_from_video(preview_file, 25)
        assert color_close(COLOR_BLUE, image.getpixel(SAMPLE_COORDINATE))

        # Assert Thumbnail images
        # We sample at '20% 40% 60% %80' - in out 30 second video that is 'RED, GREEN, GREEN, BLUE'
        assert color_close(COLOR_RED, Image.open(processed_files['image'][0].absolute).getpixel(SAMPLE_COORDINATE))
        assert color_close(COLOR_GREEN, Image.open(processed_files['image'][1].absolute).getpixel(SAMPLE_COORDINATE))
        assert color_close(COLOR_GREEN, Image.open(processed_files['image'][2].absolute).getpixel(SAMPLE_COORDINATE))
        assert color_close(COLOR_BLUE, Image.open(processed_files['image'][3].absolute).getpixel(SAMPLE_COORDINATE))


def test_encode_audio_simple():
    with ScanManager(TEST2_AUDIO_FILES) as scan:
        scan.scan_media()
        scan.encode_media()
        processed_files = scan.processed_files('test2')

        # Main Video
        video_file = processed_files['video'][0].absolute
        assert video_file


def read_subtitle_text(image, color):
    return pytesseract.image_to_string(extract_image_color(image, color)).strip()


def extract_image_color(source, color, threshold=50):
    target = Image.new('L', source.size)
    for x in range(source.size[0]):
        for y in range(source.size[1]):
            distance = color_distance(color, source.getpixel((x, y)), threshold=threshold)
            target.putpixel((x, y), distance if distance is not None else 255)
    return target
