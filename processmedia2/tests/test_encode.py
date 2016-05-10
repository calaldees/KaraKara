import pytest
import os

import pytesseract
from PIL import Image

from libs.misc import color_distance, color_close, flatten
from processmedia_libs.external_tools import probe_media, get_frame_from_video, CONFIG as ENCODE_CONFIG
from ._base import ProcessMediaTestManager, TEST1_VIDEO_FILES, TEST2_AUDIO_FILES

COLOR_SUBTITLE_CURRENT = (255, 255, 0)
COLOR_SUBTITLE_NEXT = (255, 255, 255)

COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_MAGENTA = (255, 0, 255)

SAMPLE_COORDINATE = (100, 100)


def test_encode_video_simple():
    """
    Test normal video + subtitles encode flow
    Thubnail images and preview videos should be generated
    """
    with ProcessMediaTestManager(TEST1_VIDEO_FILES) as scan:
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
        for image_num, color in enumerate((COLOR_RED, COLOR_GREEN, COLOR_GREEN, COLOR_BLUE)):
            assert color_close(color, Image.open(processed_files['image'][image_num].absolute).getpixel(SAMPLE_COORDINATE))

        video_details = probe_media(video_file)
        preview_details = probe_media(preview_file)
        assert abs(video_details['duration'] - preview_details['duration']) < 0.5, 'Main video and Preview video should be the same duration'
        assert preview_details['width'] == ENCODE_CONFIG['preview_width'], 'Preview video should match expected output size'
        assert video_details['width'] > ENCODE_CONFIG['preview_width'], 'Main video should be greater than preview video size'


def test_encode_incomplete():
    """
    Incomplete source set cannot be processed
    """
    with ProcessMediaTestManager(TEST2_AUDIO_FILES - {'test2.png'}) as scan:
        scan.scan_media()
        scan.encode_media()
        processed_files = scan.processed_files('test2')

        assert not processed_files


def test_encode_audio_simple():
    """
    Check audio + image encoding
    """
    with ProcessMediaTestManager(TEST2_AUDIO_FILES) as scan:
        scan.scan_media()
        scan.encode_media()
        processed_files = scan.processed_files('test2')

        video_file = processed_files['video'][0].absolute

        image = get_frame_from_video(video_file, 2)
        assert 'AA' == read_subtitle_text(image, COLOR_SUBTITLE_CURRENT)
        assert 'BB' == read_subtitle_text(image, COLOR_SUBTITLE_NEXT)

        image = get_frame_from_video(video_file, 7)
        assert 'BB' == read_subtitle_text(image, COLOR_SUBTITLE_CURRENT)
        assert '' == read_subtitle_text(image, COLOR_SUBTITLE_NEXT)

        image = get_frame_from_video(video_file, 12)
        assert '' == read_subtitle_text(image, COLOR_SUBTITLE_CURRENT)
        assert '' == read_subtitle_text(image, COLOR_SUBTITLE_NEXT)

        for image_num, color in enumerate((COLOR_MAGENTA,)*4):
            assert color_close(color, Image.open(processed_files['image'][image_num].absolute).getpixel(SAMPLE_COORDINATE))


def test_source_with_nosubs_will_still_create_empty_processed_srt_file():
    pytest.skip("TODO")


def test_skip_encoding_step_if_processed_file_present():
    pytest.skip("TODO")


def test_encode_video_not_multiple_of_2():
    pytest.skip("TODO")


def test_encode_image_not_multiple_of_2():
    pytest.skip("TODO")


def test_update_to_tag_file_does_not_reencode_video():
    with ProcessMediaTestManager(TEST1_VIDEO_FILES) as manager:
        manager.scan_media()
        # manager.gen_source_hash('test1')
        # processed_files = manager.processed_files('test1')
        # manager.mock_processed_files(
        #     processed_file.relative for processed_file in flatten(processed_files)
        # )
        # import pdb ; pdb.set_trace()
        # os.stat(os.path.join(manager.path_processed, processed_files['video'][0]))
        # 
        # # Modify the tags file
        # with open(os.path.join(manager.path_source, 'test1.txt'), 'a') as f:
        #     f.write('\n extra \n')
        # 
        # manager.encode_media()



# Utils ------------------------------------------------------------------------

def read_subtitle_text(image, color):
    return pytesseract.image_to_string(extract_image_color(image, color)).strip()


def extract_image_color(source, color, threshold=50):
    target = Image.new('L', source.size)
    for x in range(source.size[0]):
        for y in range(source.size[1]):
            distance = color_distance(color, source.getpixel((x, y)), threshold=threshold)
            target.putpixel((x, y), distance if distance is not None else 255)
    return target
