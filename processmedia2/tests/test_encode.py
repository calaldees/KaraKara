from ._base import ScanManager, TEST1_VIDEO_FILES


def test_encode_simple():
    with ScanManager(TEST1_VIDEO_FILES) as scan:
        scan.scan_media()
        #scan.encode_media()
        #meta = scan.meta
        #import pdb ; pdb.set_trace()
