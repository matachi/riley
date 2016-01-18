from collections import OrderedDict
import csv
import os
from os.path import expanduser

from appdirs import user_data_dir
import yaml
from riley.models import Podcast, Episode


def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    # Source: http://stackoverflow.com/a/21912744/595990
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


def ordered_dump(data, stream=None, Dumper=yaml.Dumper, **kwds):
    # Source: http://stackoverflow.com/a/21912744/595990
    class OrderedDumper(Dumper):
        pass
    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)


class Storage:
    def get_config(self):
        raise NotImplementedError

    def get_podcasts(self):
        raise NotImplementedError

    def save_podcasts(self, podcasts):
        for podcast in podcasts:
            if podcast.modified:
                self.save_podcast(podcast)

    def save_podcast(self, podcast):
        raise NotImplementedError


class EpisodeStorage:
    def save_episodes(self, podcast):
        raise NotImplementedError


class AbstractFileStorage:
    appname = 'Riley'
    appauthor = 'Riley'

    @property
    def _user_data_dir_path(self):
        return user_data_dir(self.appname, self.appauthor)


class FileStorage(AbstractFileStorage, Storage):
    @staticmethod
    def _init_config_file(config_file_path):
        os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
        init_data = OrderedDict([
            ('storage', os.path.join(expanduser("~"), 'Videos', 'Riley')),
            ('podcasts', {}),
        ])
        with open(config_file_path, 'w') as f:
            f.write(ordered_dump(init_data, default_flow_style=False))

    @property
    def _config_file_path(self):
        dir_ = self._user_data_dir_path
        config_file_path = os.path.join(dir_, 'config.yml')
        if not os.path.exists(config_file_path):
            self._init_config_file(config_file_path)
        return config_file_path

    def get_config(self):
        with open(self._config_file_path, 'r') as f:
            return ordered_load(f.read())

    def _save_config_data(self, data):
        with open(self._config_file_path, 'w') as f:
            f.write(ordered_dump(data, default_flow_style=False))

    def get_podcasts(self):
        file_episode_storage = FileEpisodeStorage()
        return OrderedDict(
            (name, Podcast(name, feed, file_episode_storage))
            for name, feed in self.get_config()['podcasts'].items())

    def save_podcast(self, podcast):
        config_data = self.get_config()
        if podcast not in config_data or podcast.modified:
            config_data['podcasts'][podcast.name] = podcast.feed
            self._save_config_data(config_data)
            podcast.modified = False
        if podcast.episodes.modified:
            file_episode_storage = FileEpisodeStorage()
            file_episode_storage.save_episodes(podcast)
            podcast.episodes.modified = False


class FileEpisodeStorage(AbstractFileStorage, EpisodeStorage):
    def _get_episode_history_file_path(self, podcast):
        return os.path.join(
            self._user_data_dir_path, '%s_history.csv' % podcast.name)

    def _init_episode_history_file(self, podcast):
        with open(self._get_episode_history_file_path(podcast), 'w') as f:
            writer = csv.writer(f)
            writer.writerow(Episode.columns)

    def get_episodes(self, podcast):
        path = self._get_episode_history_file_path(podcast)
        if not os.path.exists(path):
            self._init_episode_history_file(podcast)
        with open(path) as f:
            reader = csv.reader(f)
            episodes = [
                Episode.from_tuple(podcast, e) for e in list(reader)[1:]]
            episodes.sort(key=lambda e: e.published, reverse=True)
            return episodes

    def save_episodes(self, podcast):
        self._init_episode_history_file(podcast)
        path = self._get_episode_history_file_path(podcast)
        with open(path, 'a') as f:
            writer = csv.writer(f)
            for e in podcast.episodes:
                writer.writerow(e.str_attributes())
