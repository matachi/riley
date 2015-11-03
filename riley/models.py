from collections import OrderedDict
import os

from appdirs import user_data_dir
import yaml


class Storage:
    appname = 'Riley'
    appauthor = 'Riley'

    @property
    def user_data_dir_path(self):
        return user_data_dir(self.appname, self.appauthor)

    @property
    def config_file_path(self):
        dir_ = self.user_data_dir_path
        config_file_path = os.path.join(dir_, 'config.yml')
        if not os.path.exists(config_file_path):
            self.init_config_file(config_file_path)
        return config_file_path

    @staticmethod
    def init_config_file(config_file_path):
        os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
        init_data = {
            'podcasts': {}
        }
        with open(config_file_path, 'w') as f:
            f.write(yaml.dump(init_data, default_flow_style=False))

    def get_config_data(self):
        with open(self.config_file_path, 'r') as f:
            return yaml.load(f.read())

    def save_config_data(self, data):
        with open(self.config_file_path, 'w') as f:
            f.write(yaml.dump(data, default_flow_style=False))


class Podcast(object):
    def __init__(self, name, feed):
        self.name = name
        self.feed = feed

    def save(self):
        storage = Storage()
        data = storage.get_config_data()
        data['podcasts'][self.name] = self.feed
        storage.save_config_data(data)

    @classmethod
    def objects(cls):
        return OrderedDict(
            (name, cls(name, feed)) for name, feed in
            Storage().get_config_data()['podcasts'].items())
