from collections import OrderedDict
import csv
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

    def get_episode_history_file_path(self, podcast_name):
        return os.path.join(
            self.user_data_dir_path, '%s_history.csv' % podcast_name)

    def init_episode_history_file(self, podcast_name):
        with open(self.get_episode_history_file_path(podcast_name), 'w') as f:
            writer = csv.writer(f)
            writer.writerow(
                ['guid', 'title', 'link', 'media_href', 'downloaded'])

    def get_episode_history(self, podcast_name):
        path = self.get_episode_history_file_path(podcast_name)
        if not os.path.exists(path):
            self.init_episode_history_file(podcast_name)
        with open(path) as f:
            reader = csv.reader(f)
            return [row for row in reader][1:]

    def extend_episode_history(self, podcast_name, episodes):
        path = self.get_episode_history_file_path(podcast_name)
        if not os.path.exists(path):
            self.init_episode_history_file(podcast_name)
        with open(path, 'a') as f:
            writer = csv.writer(f)
            for episode in episodes:
                writer.writerow(episode)

    def save_episode_history(self, podcast_name, episodes):
        path = self.get_episode_history_file_path(podcast_name)
        self.init_episode_history_file(podcast_name)
        with open(path, 'a') as f:
            writer = csv.writer(f)
            for e in episodes:
                writer.writerow(
                    [e.guid, e.title, e.link, e.media_href, e.downloaded])


class Podcast:
    def __init__(self, name, feed):
        self.name = name
        self.feed = feed

    def save(self):
        storage = Storage()
        data = storage.get_config_data()
        data['podcasts'][self.name] = self.feed
        storage.save_config_data(data)

    @property
    def episodes(self):
        return EpisodeList(self)

    def extend_episodes(self, episodes):
        return Storage().extend_episode_history(self.name, episodes)

    @classmethod
    def objects(cls):
        return OrderedDict(
            (name, cls(name, feed)) for name, feed in
            Storage().get_config_data()['podcasts'].items())


class EpisodeList(list):
    def __init__(self, podcast):
        super().__init__()
        self.podcast = podcast
        self.extend(Episode(
            guid=e[0], title=e[1], link=e[2], media_href=e[3], downloaded=False
        ) for e in Storage().get_episode_history(self.podcast.name))

    def save(self):
        Storage().save_episode_history(self.podcast.name, self)


class Episode:
    def __init__(self, guid, title, link, media_href, downloaded):
        self.guid = guid
        self.title = title
        self.link = link
        self.media_href = media_href
        self.downloaded = downloaded
