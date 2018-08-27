import json

from processmedia_libs.external_tools import ProcessMediaFilesWithExternalTools


def test_probe_media():
    raise NotImplementedError()
    external_tools = ProcessMediaFilesWithExternalTools()
    assert json.dumps(external_tools.probe_media('tests/source/test1.mp4'), sort_keys=True) == '{"audio": {"bitrate": "2", "format": "aac", "sample_rate": "44100"}, "duration": 30.02, "height": 480, "width": 640}'


def test_get_image_from_video():
    raise NotImplementedError()
    #>>> color_close((255, 0, 0), get_frame_from_video('tests/source/test1.mp4', 0).getpixel((0,0)))
    #True
    #>>> color_close((0, 255, 0), get_frame_from_video('tests/source/test1.mp4', '10').getpixel((0,0)))
    #True
    #>>> color_close((0, 0, 255), get_frame_from_video('tests/source/test1.mp4', '00:00:20').getpixel((0,0)))
    #True
