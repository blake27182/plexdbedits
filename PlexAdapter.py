import os
from plexapi.server import PlexServer


base_thumbnail_path = 'http://localhost:8060'
base_local_thumb = '/Volumes/home/Plex/HomeVideos/CustomMetadata/Thumbnails'
by_disk_section_name = 'Home Videos by Disk'
by_disk_section_id = 13
hv_section_ids = [13, 14]


def get_server():
    return PlexServer(baseurl="http://192.168.1.190:32400", token=os.environ["PLEX_TOKEN"])


def unmatch_all_in_section(section_name=None, section_id=None):
    server = get_server()
    if section_name:
        results = server.library.section(section_name).all()
    elif section_id:
        results = server.library.sectionByID(section_id).all()
    else:
        raise Exception('must provide either section name or id')
    for item in results:
        item.unmatch()


def reset_all_titles_in_section(section_name=None, section_id=None):
    server = get_server()
    if section_name:
        results = server.library.section(section_name).all()
    elif section_id:
        results = server.library.sectionByID(section_id).all()
    else:
        raise Exception('must provide either section name or id')
    for item in results:
        title = os.path.basename(item.locations[0]).split('.')[0]
        item.editTitle(title)


def set_actor(video, actor_name, thumbnail):
    """Creates a new actor entry in the tags table, making it available to assign new roles.

    :param video: Movie or Show or Season or Episode object to assign actor to
    :param actor_name: str: name of actor
    :param thumbnail: str: file name and extension of the thumbnail
    :return:
    """
    edits = {
        'actor[0].tag.tag': actor_name,
        'actor[0].locked': 1
    }
    if thumbnail:
        edits['actor[0].tag.thumb'] = base_thumbnail_path + '/Actors/' + thumbnail
    video.edit(**edits)


def set_poster(video, poster):
    video.uploadPoster(filepath=base_local_thumb + '/Posters/' + poster)
    video.lockPoster()
    # print('setting poster', poster, 'on', video, video.posters()[0].ratingKey)


def unset_poster(video):
    for poster in video.posters():
        if not poster.ratingKey.startswith('upload'):
            video.setPoster(poster)
            break
    video.unlockPoster()
    # print('unset poster for', video)


def get_video_by_location(full_path):
    server = get_server()
    results = server.library.all()
    for result in results:
        try:
            if full_path in result.locations:
                # if kind == 'show':
                return result
        except AttributeError:
            continue
    raise Exception(f'cannot find video by location: {full_path} : {results}')


def scan_library(section_name=None, section_id=None):
    server = get_server()
    if section_name:
        section = server.library.section(section_name)
    elif section_id:
        section = server.library.sectionByID(section_id)
    else:
        raise Exception('must provide either section id or name')
    section.update()
