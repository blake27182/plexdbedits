import datetime
import os

from plexapi import library
from plexapi.server import PlexServer

import PlexAdapter
import ffmpeg


def main():
    in_file = ffmpeg.input('/Volumes/home/Plex/HomeVideos/DiskCopies/Ray/Costco/1 Summer of 1993.mkv', ss='59:00')
    out_options = {
        't': '1:00',
        'map': '0',
        'tag:v': 'hvc1',
        'c': 'copy',
        # 'c:v': 'hevc_videotoolbox',
        # 'q:v': '80',

    }
    (
        in_file
        .output('/Users/blakewilliams/Downloads/out.mkv', **out_options)
        .overwrite_output()
        .run()
    )


def get_datetime(t_string):
    valid_formats = [
        '%H:%M:%S',
        '%M:%S',
        '%S',
        '%H:%M:%S.%f',
        '%M:%S.%f',
        '%S.%f',
    ]
    for t_format in valid_formats:
        try:
            return datetime.datetime.strptime(t_string, t_format)
        except ValueError:
            continue
    raise ValueError(f'Invalid time format: {t_string}')


def main2():
    print(get_datetime('18:1:1'))


if __name__ == '__main__':
    main()
