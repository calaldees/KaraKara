import pytest
import os

import pytesseract
from PIL import Image

from calaldees.misc import color_distance, color_close, flatten
from processmedia_libs.external_tools import probe_media, get_frame_from_video, CONFIG as ENCODE_CONFIG
import processmedia_libs.subtitle_processor as subtitle_processor
from ._base import ProcessMediaTestManager, TEST1_VIDEO_FILES, TEST2_AUDIO_FILES, MockEncodeExternalCalls

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
        processed_files = scan.get('test1').processed_files

        # Main Video - use OCR to read subtiles and check them
        video_file = processed_files['video'].absolute

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
        preview_file = processed_files['preview'].absolute

        image = get_frame_from_video(preview_file, 5)
        assert color_close(COLOR_RED, image.getpixel(SAMPLE_COORDINATE))

        image = get_frame_from_video(preview_file, 15)
        assert color_close(COLOR_GREEN, image.getpixel(SAMPLE_COORDINATE))

        image = get_frame_from_video(preview_file, 25)
        assert color_close(COLOR_BLUE, image.getpixel(SAMPLE_COORDINATE))

        # Assert Thumbnail images
        # We sample at '20% 40% 60% %80' - in out 30 second video that is 'RED, GREEN, GREEN, BLUE'
        for image_num, color in enumerate((COLOR_RED, COLOR_GREEN, COLOR_GREEN, COLOR_BLUE)):
            assert color_close(color, Image.open(processed_files['image{}'.format(image_num+1)].absolute).getpixel(SAMPLE_COORDINATE))

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
        processed_files = scan.get('test2').processed_files

        assert not processed_files


def test_encode_audio_simple():
    """
    Check audio + image encoding
    """
    with ProcessMediaTestManager(TEST2_AUDIO_FILES) as scan:
        scan.scan_media()
        scan.encode_media()
        processed_files = scan.get('test2').processed_files

        video_file = processed_files['video'].absolute

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
            assert color_close(color, Image.open(processed_files['image{}'.format(image_num+1)].absolute).getpixel(SAMPLE_COORDINATE))


def test_source_with_nosubs_will_still_create_empty_processed_srt_file():
    with ProcessMediaTestManager(TEST1_VIDEO_FILES) as manager:
        manager.scan_media()
        os.remove(os.path.join(manager.path_source, 'test1.srt'))

        # As the subs source file does not exists -> this should fail to encode
        with MockEncodeExternalCalls() as patches:
            manager.encode_media()
            assert patches['encode_video'].call_count == 0
            assert patches['encode_audio'].call_count == 0
            assert patches['encode_preview_video'].call_count == 0
            assert patches['extract_image'].call_count == 0

        manager.scan_media()  # this should update the source collection and remove the meta reference to the srt file
        with MockEncodeExternalCalls() as patches:
            manager.encode_media()
            assert patches['encode_video'].call_count == 1
            assert patches['encode_audio'].call_count == 1
            assert patches['encode_preview_video'].call_count == 1
            assert patches['extract_image'].call_count == 4

        # A subtile file should still be derived
        os.path.exists(manager.get('test1').processed_files['srt'].absolute)


def test_skip_encoding_step_if_processed_file_present():
    with ProcessMediaTestManager(TEST1_VIDEO_FILES) as manager:

        manager.scan_media()
        with MockEncodeExternalCalls() as patches:
            manager.encode_media()
            assert patches['encode_video'].call_count == 1
            assert patches['encode_audio'].call_count == 1
            assert patches['encode_preview_video'].call_count == 1
            assert patches['extract_image'].call_count == 4

        manager.scan_media()
        with MockEncodeExternalCalls() as patches:
            manager.encode_media()
            assert patches['encode_video'].call_count == 0
            assert patches['encode_audio'].call_count == 0
            assert patches['encode_preview_video'].call_count == 0
            assert patches['extract_image'].call_count == 0


def test_encode_video_not_multiple_of_2():
    pytest.skip("TODO")


def test_encode_image_not_multiple_of_2():
    pytest.skip("TODO")


def test_encode_with_already_existing_files_still_extracts_duration():
    """
    The scan picks up the source files for the first time
    However, in this case, the processed files already exists! We expect the processed files to be relinked
    During the relinking process we will need to probe the duration, width, height from the source.
    Assert the probe is run and the meta contains a duration
    """
    with ProcessMediaTestManager(TEST1_VIDEO_FILES) as manager:
        manager.scan_media()

        manager.mock_processed_files(
            processed_file.relative
            for m in manager.meta_manager.meta_items
            for processed_file in m.processed_files.values()
        )

        with MockEncodeExternalCalls() as patches:
            manager.encode_media()
            assert patches['probe_media'].call_count == 1, 'Even though the processed files exists, the source media should have been probed'

        assert manager.meta['test1.json']['processed']['duration'] == 1, 'The relinked meta should have probed a duration'


def test_update_to_tag_file_does_not_reencode_video():
    with ProcessMediaTestManager(TEST1_VIDEO_FILES) as manager:

        manager.scan_media()
        manager.encode_media(mock=True)

        hash_dict_before = manager.get('test1').source_hashs

        # Modify the tags file ---------
        tags_file_absolute = os.path.join(manager.path_source, 'test1.txt')
        os.remove(tags_file_absolute)
        with open(tags_file_absolute, 'w') as f:
            f.write('the tags file has changed')

        manager.scan_media()
        with MockEncodeExternalCalls() as patches:
            manager.encode_media()
            assert patches['encode_video'].call_count == 0
            assert patches['encode_audio'].call_count == 0
            assert patches['encode_preview_video'].call_count == 0
            assert patches['extract_image'].call_count == 0

        hash_dict_tag_changed = manager.get('test1').source_hashs
        assert hash_dict_before['media'] == hash_dict_tag_changed['media']
        assert hash_dict_before['data'] != hash_dict_tag_changed['data']
        assert hash_dict_before['full'] != hash_dict_tag_changed['full']

        # Modify the subs file ----------
        subs_file_absolute = os.path.join(manager.path_source, 'test1.srt')
        os.remove(subs_file_absolute)
        with open(subs_file_absolute, 'w', encoding='utf-8') as subfile:
            subfile.write(
                subtitle_processor.create_srt((
                    subtitle_processor.Subtitle(subtitle_processor.time(0,0,0,0), subtitle_processor.time(0,1,0,0), 'first'),
                ))
            )

        manager.scan_media()
        with MockEncodeExternalCalls() as patches:
            manager.encode_media()
            assert patches['encode_video'].call_count == 1
            assert patches['encode_audio'].call_count == 1
            assert patches['encode_preview_video'].call_count == 1
            assert patches['extract_image'].call_count == 4

        hash_dict_subs_changed = manager.get('test1').source_hashs
        assert hash_dict_tag_changed['media'] != hash_dict_subs_changed['media']
        assert hash_dict_tag_changed['data'] != hash_dict_subs_changed['data']
        assert hash_dict_tag_changed['full'] != hash_dict_subs_changed['full']


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
