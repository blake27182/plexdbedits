from jsonschema import validate
import yaml
import os


def load_yamls(config_folder):
    actor_dbs = {}
    safe_sections = []
    video_tags = []
    for file in os.listdir(config_folder):
        with open(os.path.join(config_folder, file), 'r') as fr:
            listed_data = yaml.load_all(fr, Loader=yaml.loader.BaseLoader)
            for data in listed_data:
                lint_yaml(data)
                if data['kind'] == 'ActorDB':
                    actor_dbs[data['metadata']['name']] = data
                elif data['kind'] == 'SafeSection':
                    safe_sections.append(data)
                elif data['kind'] in ('MovieTag', 'ShowTag'):
                    video_tags.append(data)
    return actor_dbs, safe_sections, video_tags


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
  spec:
    type: object
    required:
      - title
"""
    if 'kind' in yaml_obj:
        if yaml_obj['kind'] == 'ShowTag':
            validate(yaml_obj, yaml.load(show_schema, Loader=yaml.loader.BaseLoader))
