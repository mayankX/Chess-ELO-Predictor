__author__ = 'Mayank Tiwari'

import yaml
from mongoengine import connect


def load_config(config_file):
    with open(config_file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def init_database(profile, config):
    collectionName = config['collection_name']

    mongoConfiguration = config[profile]['mongo']
    mongoAuth = mongoConfiguration['auth']
    host = mongoConfiguration['host']
    port = mongoConfiguration['port']
    if mongoAuth is None or mongoAuth == 'None':
        return connect(collectionName, host=host, port=port)
    else:
        connect(
            collectionName, host=host, port=port,
            username=mongoConfiguration['username'], password=mongoConfiguration['password'],
            authentication_source=mongoConfiguration['authentication_source']
        )
