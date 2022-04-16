import json
from pathlib import Path
import subprocess


def test_probe_media(path_source_reference, external_tools):
    filename_video = Path(path_source_reference, 'test1.mp4')
    assert json.dumps(external_tools.probe_media(filename_video), sort_keys=True) == '{"audio": {"bitrate": "2", "format": "aac", "sample_rate": "44100"}, "duration": 30.0, "height": 480, "width": 640}'


def test_get_image_from_video(path_source_reference):
    from .test_encode import get_frame_from_video
    from calaldees.color import color_close
    filename_video = Path(path_source_reference, 'test1.mp4')
    assert color_close((255, 0, 0), get_frame_from_video(filename_video, 0).getpixel((0,0)))
    assert color_close((0, 255, 0), get_frame_from_video(filename_video, '10').getpixel((0,0)))
    assert color_close((0, 0, 255), get_frame_from_video(filename_video, '00:00:20').getpixel((0,0)))


def test_ffmpeg_installed_with_extras():
    cmd = ('ffmpeg', '--help')
    cmd_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1)
    assert 'Hyper fast Audio and Video encoder' in cmd_result.stdout.decode('utf8')
    assert '--enable-libsvtav1' in cmd_result.stderr.decode('utf8')


def test_imagemagick(path_source_reference):
    source = Path(path_source_reference, 'test1_000.png')
    destination = Path(path_source_reference, 'test1_000.avif')
    cmd = ('convert', source, destination)
    cmd_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
    assert destination.is_file()
    destination.unlink()
