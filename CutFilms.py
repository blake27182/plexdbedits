import os
import ffmpeg
import datetime

from CoreUtilities import load_yamls


def cut_films(config_folder, overwrite=True, testing=True):
    if overwrite:
        print('############### OVERWRITE ENABLED ###############')
    actor_dbs, safe_sections, video_tags = load_yamls(config_folder)

    for video_tag in video_tags:
        if video_tag['kind'] == 'ShowTag' and 'sources' in video_tag['spec']:
            sources = video_tag['spec']['sources']
            start = get_datetime('0')
            source = sources[0]
            for i, season_tag in enumerate(video_tag['spec']['seasons']):
                for j, episode_tag in enumerate(season_tag['episodes']):
                    error_tag = f'{video_tag["kind"]}:{video_tag["spec"]["title"]}-season:{i+1}-episode:{j+1}'
                    duration = None
                    # required args
                    if 'end' in episode_tag:
                        end = get_datetime(episode_tag['end'], error_tag=error_tag)
                    elif 'cut' in episode_tag:
                        end = get_datetime(episode_tag['cut'], error_tag=error_tag)
                    else:
                        continue
                    # optional args
                    if 'source' in episode_tag:
                        source = sources[episode_tag['source']]
                        start = get_datetime('0')
                    if 'start' in episode_tag:
                        start = get_datetime(episode_tag['start'], error_tag=error_tag)
                    if 'duration' in episode_tag:
                        duration = get_datetime(episode_tag['duration'], error_tag=error_tag)
                    if end:
                        duration = end - start
                    if duration and duration < datetime.timedelta(0):
                        raise Exception(f'negative duration at {error_tag}')

                    out_dir = os.path.join(
                        video_tag["metadata"]['location'],
                        f'Season {i+1:0>2}'
                    )
                    out_file = f's{i+1:0>2}e{j+1:0>2}.mkv'
                    full_out_path = os.path.join(out_dir, out_file)
                    out_dir_list = out_dir.split('/')

                    # create directories on path and write the file
                    for d in range(len(out_dir_list)+1):
                        if d <= 1:
                            continue
                        part_path = "/".join(out_dir_list[0:d])
                        # print(out_dir_list, d, part_path, out_dir_list[0:d])          # debugging
                        if not os.path.exists(part_path):
                            if testing:
                                print(f'would create directory: {part_path}')
                            else:
                                os.mkdir(part_path)
                    if testing:
                        print(f'would create file from {source} starting at {str(start.time())} '
                              f'with duration {str(duration) if duration else "EOF"} outputting to {full_out_path}')
                    else:
                        if os.path.exists(full_out_path) and not overwrite:
                            print(f'skipping {full_out_path} as it already exists')
                            continue
                        else:
                            print(f'creating file from {source} starting at {str(start.time())} '
                                  f'with duration {str(duration) if duration else "EOF"} outputting to {full_out_path}')
                        out_options = {
                            'map': '0',
                            'c': 'copy',
                            'loglevel': 'quiet'
                        }
                        if duration:
                            out_options['t'] = str(duration)
                        (
                            ffmpeg
                            .input(source, ss=str(start.time()))
                            .output(full_out_path, **out_options)
                            .overwrite_output()
                            .run()
                        )

                    start = end if end else get_datetime('0')


def get_datetime(t_string, error_tag=None):
    valid_formats = [
        '%H:%M:%S',
        '%M:%S',
        '%S',
        '%H:%M:%S.%f',
        '%M:%S.%f',
        '%S.%f',
    ]
    if t_string == 'EOF':
        return None
    for t_format in valid_formats:
        try:
            return datetime.datetime.strptime(str(t_string), t_format)
        except ValueError:
            continue
    raise ValueError(f'Invalid time format: {t_string} in tag {error_tag}')


if __name__ == '__main__':
    cut_films('/Volumes/home/Plex/HomeVideos/CustomMetadata/configs', overwrite=True, testing=False)
