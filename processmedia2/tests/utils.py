import subprocess
from io import BytesIO
from PIL import Image


def color_close(target, actual, threshold=20):
    """
    >>> color_close((0,0,0), (0,0,0))
    True
    >>> color_close((0,0,255), (1,18,255))
    True
    >>> color_close((255,0,0), (0,0,255))
    False

    """
    return sum(abs(a - b) for a, b in zip(target, actual)) < threshold


def get_frame_from_video(url, time="00:00:10"):
    """
    FFMpeg | pipe stdout -> PIL.Image (from stringbuffer)

    time string format - hh:mm:ss[.xxx]

    Gets Image progressivly - Largers times read linearly from the beggining of the file

    >>> color_close((255, 0, 0), get_frame_from_video('tests/source/test1.avi', 0).getpixel((0,0)))
    True
    >>> color_close((0, 255, 0), get_frame_from_video('tests/source/test1.avi', '10').getpixel((0,0)))
    True
    >>> color_close((0, 0, 255), get_frame_from_video('tests/source/test1.avi', '00:00:20').getpixel((0,0)))
    True
    """
    cmd = """avconv -loglevel quiet -i "{url}" -ss {time} -vframes 1 -f image2 pipe: """.format(url=url, time=time)
    return Image.open(BytesIO(subprocess.check_output(cmd, stderr=subprocess.PIPE, shell=True)))
