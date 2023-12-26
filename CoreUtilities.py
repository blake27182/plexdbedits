from jsonschema import validate
import yaml
import os


def load_yamls(config_folder):
    actor_dbs = {}
    safe_sections = {}
    video_tags = []
    file_list = []
    plex_config = {}
    if os.path.isdir(config_folder):
        for x in os.listdir(config_folder):
            if not x.startswith('.'):
                file_list.append(os.path.join(config_folder, x))
    else:
        file_list = [config_folder]
    for file in file_list:
        print(f'loading yaml {file}')
        with open(file, 'r') as fr:
            listed_data = yaml.load_all(fr, Loader=yaml.loader.BaseLoader)
            for data in listed_data:
                lint_yaml(data)
                if data['kind'] == 'ActorDB':
                    actor_dbs[data['metadata']['name']] = data
                elif data['kind'] == 'SafeSection':
                    safe_sections[data['metadata']['id']] = data
                elif data['kind'] in ('MovieTag', 'ShowTag'):
                    video_tags.append(data)
                elif data['kind'] == 'PlexConfig':
                    plex_config = data['spec']
    return actor_dbs, safe_sections, video_tags, plex_config


def lint_yaml(yaml_obj):
    show_schema = """
type: object
properties:
  kind:
    type: string
  metadata:
    properties:
      location:
        type: string
      section_id:
        type: string
  spec:
    type: object
    required:
      - title
"""
    if 'kind' in yaml_obj:
        if yaml_obj['kind'] == 'ShowTag':
            try:
                validate(yaml_obj, yaml.load(show_schema, Loader=yaml.loader.BaseLoader))
            except Exception as e:
                print(f'failed validation: {yaml_obj}')
                raise e
