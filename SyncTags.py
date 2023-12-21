import PlexAdapter
from CoreUtilities import load_yamls


def sync_all_metadata(config_folder):
    actor_dbs, safe_sections, video_tags = load_yamls(config_folder)

    for safe_section in safe_sections:
        section = safe_section['spec']['name']
        if section.isnumeric():
            params = {'section_id': section}
        else:
            params = {'section_name': section}
        print(f'scanning section {section}')
        PlexAdapter.scan_library(**params)
        print(f'unmatching all in section {section}')
        PlexAdapter.unmatch_all_in_section(**params)
        if safe_section['spec']['reset_titles'] == 'True':
            print('resetting titles in section:', section)
            PlexAdapter.reset_all_titles_in_section(**params)

    for video_tag in video_tags:
        video = PlexAdapter.get_video_by_location(video_tag['metadata']['location'])
        if video_tag['kind'] == 'ShowTag':
            actors = build_show_actors(video_tag)
        else:
            actors = video_tag['spec']['actors']
        set_actors(video, actors, actor_dbs[video_tag['metadata']['actor_db']])
        set_common_conditionals(video, video_tag['spec'])

        if video_tag['kind'] == 'ShowTag' and 'seasons' in video_tag['spec']:
            for i, season_tag in enumerate(video_tag['spec']['seasons']):
                season = video.season(i+1)
                set_common_conditionals(season, season_tag)
                for j, episode_tag in enumerate(season_tag['episodes']):
                    episode = season.episode(j+1)
                    if episode_tag and 'actors' in episode_tag:
                        set_actors(episode, episode_tag['actors'], actor_dbs[video_tag['metadata']['actor_db']])
                    else:
                        unset_actors(episode)
                    set_common_conditionals(episode, episode_tag)


def set_common_conditionals(video, video_tag):
    if video_tag:
        if video_tag and 'poster' in video_tag:
            PlexAdapter.set_poster(video, video_tag['poster'])
        else:
            PlexAdapter.unset_poster(video)
        if video_tag and 'summary' in video_tag:
            video.editSummary(video_tag['summary'])
        else:
            video.editSummary('', locked=False)
        if video_tag and 'release' in video_tag:
            video.editOriginallyAvailable(video_tag['release'])
        if video_tag and 'title' in video_tag:
            video.editTitle(video_tag['title'])
        if video_tag and 'sort_title' in video_tag:
            video.editSortTitle(video_tag['sort_title'])


def set_actors(video, actors, actor_db):
    unset_actors(video)
    for actor in reversed(actors):
        thumbnail = actor_db['spec']['actor_thumbs'][actor]
        PlexAdapter.set_actor(video, actor, thumbnail)


def unset_actors(video):
    video.editTags('actor', video.roles, remove=True)


def build_show_actors(show_tag):
    show_actors = {}
    if 'seasons' in show_tag['spec']:
        for season_tag in show_tag['spec']['seasons']:
            for episode_tag in season_tag['episodes']:
                if episode_tag and 'actors' in episode_tag:
                    for actor in episode_tag['actors']:
                        if actor in show_actors:
                            show_actors[actor] += 1
                        else:
                            show_actors[actor] = 1
    l_actors = []
    counter = 0
    while len(l_actors) < len(show_actors):
        counter += 1
        for actor, count in show_actors.items():
            if counter == count:
                l_actors.append(actor)
    l_actors.reverse()
    return l_actors


if __name__ == '__main__':
    sync_all_metadata('/Volumes/home/Plex/HomeVideos/CustomMetadata/configs')
