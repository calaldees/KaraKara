import pytest
import subprocess
from io import BytesIO
from pathlib import Path
from functools import partial

from PIL import Image

from calaldees.color import color_distance, color_close as _color_close
color_close = partial(_color_close, threshold=30)

import processmedia_libs.subtitle_processor as subtitle_processor
from ._base import MockEncodeExternalCalls

COLOR_SUBTITLE_CURRENT = (255, 255, 0)
COLOR_SUBTITLE_NEXT = (255, 255, 255)

COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_MAGENTA = (255, 0, 255)

SAMPLE_COORDINATE = (100, 100)


# Utils ------------------------------------------------------------------------

#import pytesseract
#def read_subtitle_text(image, color):
#    return pytesseract.image_to_string(extract_image_color(image, color)).strip()


def extract_image_color(source, color, threshold=60):
    target = Image.new('L', source.size)
    for x in range(source.size[0]):
        for y in range(source.size[1]):
            distance = color_distance(color, source.getpixel((x, y)), threshold=threshold)
            target.putpixel((x, y), distance if distance is not None else 255)
    return target


def get_frame_from_video(url, time="00:00:10", ffmpeg_cmd='ffmpeg'):
    """
    ffmpeg | pipe stdout -> PIL.Image (from stringbuffer)

    time string format - hh:mm:ss[.xxx]

    Gets Image progressively - Larger times read linearly from the beginning of the file
    """
    cmd = f"""{ffmpeg_cmd} -loglevel quiet -i "{url}" -ss {time} -vframes 1 -f image2 pipe: """
    return Image.open(BytesIO(subprocess.check_output(cmd, stderr=subprocess.PIPE, shell=True)))


# Tests ------------------------------------------------------------------------

def test_encode_video_simple(ProcessMediaTestManager, TEST1_VIDEO_FILES, external_tools):
    """
    Test normal video + subtitles encode flow
    Thumbnail images and preview videos should be generated
    """
    with ProcessMediaTestManager(TEST1_VIDEO_FILES) as scan:
        scan.scan_media()

        # encode (should trigger heartbeat update)
        heartbeat_mtime = scan.heartbeat_mtime
        assert heartbeat_mtime
        scan.encode_media()
        assert heartbeat_mtime < scan.heartbeat_mtime

        processed_files = scan.get('test1').processed_files

        # Main Video - use OCR to read subtiles and check them
        video_file = processed_files['video'].file
        video_details = external_tools.probe_media(video_file)

        image = get_frame_from_video(video_file, 5)
        assert color_close(COLOR_RED, image.getpixel(SAMPLE_COORDINATE))
        #assert 'Red' == read_subtitle_text(image, COLOR_SUBTITLE_CURRENT)
        #assert 'Green' == read_subtitle_text(image, COLOR_SUBTITLE_NEXT)

        image = get_frame_from_video(video_file, 15)
        assert color_close(COLOR_GREEN, image.getpixel(SAMPLE_COORDINATE))
        #assert 'Green' == read_subtitle_text(image, COLOR_SUBTITLE_CURRENT)
        #assert 'Blue' == read_subtitle_text(image, COLOR_SUBTITLE_NEXT)

        image = get_frame_from_video(video_file, 25)
        assert color_close(COLOR_BLUE, image.getpixel(SAMPLE_COORDINATE))
        #assert 'Blue' == read_subtitle_text(image, COLOR_SUBTITLE_CURRENT)
        #assert not read_subtitle_text(image, COLOR_SUBTITLE_NEXT)

        # Preview Video (can't check subtitles as the res is too small)
        for ProcessedFileType_key in ('preview_av1', 'preview_h265'):
            preview_file = processed_files[ProcessedFileType_key].file

            image = get_frame_from_video(preview_file, 5)
            assert color_close(COLOR_RED, image.getpixel(SAMPLE_COORDINATE))

            image = get_frame_from_video(preview_file, 15)
            assert color_close(COLOR_GREEN, image.getpixel(SAMPLE_COORDINATE))

            image = get_frame_from_video(preview_file, 25)
            assert color_close(COLOR_BLUE, image.getpixel(SAMPLE_COORDINATE))

            preview_details = external_tools.probe_media(preview_file)
            assert abs(video_details['duration'] - preview_details['duration']) < 0.5, 'Main video and Preview video should be the same duration'
            assert video_details['width'] > preview_details['width'], 'Main video should be greater than preview video size'

        # Assert Thumbnail images
        # We sample at '20% 40% 60% %80' - in out 30 second video that is 'RED, GREEN, GREEN, BLUE'
        for image_num, color in enumerate((COLOR_RED, COLOR_GREEN, COLOR_GREEN, COLOR_BLUE)):
            assert color_close(color, Image.open(processed_files[f'image{image_num+1}_webp'].file).getpixel(SAMPLE_COORDINATE))

        # Assert subtitles
        assert processed_files[f'subtitle'].file.stat().st_size > 0, 'subtitle file was created and has content'



def test_encode_incomplete(ProcessMediaTestManager, TEST2_AUDIO_FILES):
    """
    Incomplete source set cannot be processed
    """
    with ProcessMediaTestManager(TEST2_AUDIO_FILES - {'test2.png'}) as scan:
        scan.scan_media()
        scan.encode_media()
        processed_files = scan.get('test2').processed_files

        for f in processed_files.values():
            assert not f.file.exists()


def test_encode_audio_simple(ProcessMediaTestManager, TEST2_AUDIO_FILES):
    """
    Check audio + image encoding
    """
    with ProcessMediaTestManager(TEST2_AUDIO_FILES) as scan:
        scan.scan_media()
        scan.encode_media()
        processed_files = scan.get('test2').processed_files

        video_file = processed_files['video'].file

        image = get_frame_from_video(video_file, 2)
        #assert 'AA'.lower() == read_subtitle_text(image, COLOR_SUBTITLE_CURRENT).lower()
        #assert 'EE'.lower() == read_subtitle_text(image, COLOR_SUBTITLE_NEXT).lower()

        image = get_frame_from_video(video_file, 7)
        #assert 'EE'.lower() == read_subtitle_text(image, COLOR_SUBTITLE_CURRENT).lower()
        #assert '' == read_subtitle_text(image, COLOR_SUBTITLE_NEXT)

        image = get_frame_from_video(video_file, 12)
        #assert '' == read_subtitle_text(image, COLOR_SUBTITLE_CURRENT)
        #assert '' == read_subtitle_text(image, COLOR_SUBTITLE_NEXT)

        for image_num, color in enumerate((COLOR_MAGENTA,)*4):
            assert color_close(color, Image.open(processed_files[f'image{image_num+1}_webp'].file).getpixel(SAMPLE_COORDINATE))


def test_skip_encoding_step_if_processed_file_present(ProcessMediaTestManager, TEST1_VIDEO_FILES):
    with ProcessMediaTestManager(TEST1_VIDEO_FILES) as manager:

        manager.scan_media()
        with MockEncodeExternalCalls() as patches:
            manager.encode_media()
            assert patches['encode_video'].call_count == 3
            assert patches['extract_image'].call_count == 4
            assert patches['compress_image'].call_count == 8

        manager.scan_media()
        with MockEncodeExternalCalls() as patches:
            manager.encode_media()
            assert patches['encode_video'].call_count == 0
            assert patches['extract_image'].call_count == 0
            assert patches['compress_image'].call_count == 0


def test_encode_with_already_existing_files_still_extracts_duration(ProcessMediaTestManager, TEST1_VIDEO_FILES):
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

        assert manager.meta['test1.json']['source_details']['duration'] == 1, 'The relinked meta should have probed a duration'


def test_update_to_tag_file_does_not_reencode_video(ProcessMediaTestManager, TEST1_VIDEO_FILES):
    with ProcessMediaTestManager(TEST1_VIDEO_FILES) as manager:

        manager.scan_media()
        manager.encode_media(mock=True)

        hash_dict_before = manager.get('test1').source_hashs

        # Modify the tags file ---------
        with Path(manager.path_source, 'test1.txt').open('w') as f:
            f.write('the tags file has changed')

        manager.scan_media()
        with MockEncodeExternalCalls() as patches:
            manager.encode_media()
            assert patches['encode_video'].call_count == 0
            assert patches['extract_image'].call_count == 0
            assert patches['compress_image'].call_count == 0

        hash_dict_tag_changed = manager.get('test1').source_hashs
        assert hash_dict_before == hash_dict_tag_changed
        #assert hash_dict_before['media'] == hash_dict_tag_changed['media']
        #assert hash_dict_before['data'] != hash_dict_tag_changed['data']
        #assert hash_dict_before['full'] != hash_dict_tag_changed['full']

        # TODO: modify source file and assert re-encode?
