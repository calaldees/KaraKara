#!/usr/bin/env python
import re
import os
import glob
import argparse

from sh import mediainfo


def videos_with_variable_framerate(media_root):
    source_files = glob.glob(media_root + "/*/source/*")

    def variable_framerate(media):
        info = mediainfo(media)
        return re.search(r"Frame rate mode\s+:\s+Variable", str(info)) != None

    return filter(variable_framerate, source_files)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to find the video sources with variable frame rates. Requires mediainfo install')
    parser.add_argument("--media-root", default=os.getcwd(), dest="media_root")

    args = parser.parse_args()

    print videos_with_variable_framerate(args.media_root)
