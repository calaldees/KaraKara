import os

from ._base import ProcessMediaTestManager


def test_scan_grouping(TEST1_VIDEO_FILES, TEST2_AUDIO_FILES):
    with ProcessMediaTestManager(TEST1_VIDEO_FILES | TEST2_AUDIO_FILES - {'test2.txt'}) as scan:
        scan.scan_media()
        meta = scan.meta
        assert set(meta['test1.json']['scan'].keys()) == {'test1.mp4', 'test1.srt', 'test1.txt'}, \
            'test1 source files were not grouped effectively'
        assert set(meta['test2.json']['scan'].keys()) == {'test2.ogg', 'test2.png', 'test2.ssa'}, \
            'test2 source files were not grouped effectively'

        # If a file is renamed - it is searched and re-associated with the original group even if it's name does not match anymore
        subtitle_hash = meta['test1.json']['scan']['test1.srt']['hash']
        os.rename(os.path.join(scan.path_source, 'test1.srt'), os.path.join(scan.path_source, 'testX.srt'))
        scan.scan_media()
        meta = scan.meta
        assert meta['test1.json']['scan']['testX.srt']['hash'] == subtitle_hash, \
            'File was renamed, but he hash should be the same'

        # Modify the re-associated file - the file should have it's hash updated and not be disassociated
        subtitle_file = os.path.join(scan.path_source, 'testX.srt')
        with open(subtitle_file, 'r') as subtitle_filehandle:
            subtitles = subtitle_filehandle.read()
        os.remove(subtitle_file)
        with open(subtitle_file, 'w') as subtitle_filehandle:
            subtitle_filehandle.write(subtitles.replace('Red', 'Red2'))
        scan.scan_media()
        meta = scan.meta
        assert meta['test1.json']['scan']['testX.srt']['hash'] != subtitle_hash, \
            'File hash should have changed as the contents were modified'

        # Create a new file to be grouped with 'test2' - 'test1' should remain unchanged
        with open(os.path.join(scan.path_source, 'test2.txt'), 'w') as tags_filehandle:
            tags_filehandle.write('category:test2\n')
            tags_filehandle.write('title:test2\n')
        scan.scan_media()
        meta = scan.meta
        assert set(meta['test1.json']['scan'].keys()) == {'test1.mp4', 'testX.srt', 'test1.txt'}
        assert set(meta['test2.json']['scan'].keys()) == {'test2.ogg', 'test2.txt', 'test2.ssa', 'test2.png'}, \
            'test2.txt should have been grouped with test2'


def test_scan_yaml_overrides():
    """
    TODO
    """
    pass
