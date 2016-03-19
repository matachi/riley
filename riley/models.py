import math
import time


class HasBeenModified:
    def __init__(self):
        self.modified = False

    def __setattr__(self, key, value):
        if key != 'modified':
            if hasattr(self, key) and getattr(self, key) != value:
                self.modified = True
                self.modified_attr(key, value)
        super().__setattr__(key, value)

    def modified_attr(self, key, value):
        pass


class Podcast(HasBeenModified):

    score_const = 30 / math.log(6)

    def __init__(self, name, feed, episode_storage, priority=5):
        super(Podcast, self).__init__()
        self.name = name
        self.feed = feed
        self.priority = priority
        self._episode_storage = episode_storage

    @property
    def episodes(self):
        if not hasattr(self, '_episodes'):
            self._episodes = EpisodeList(
                self._episode_storage.get_episodes(self))
            delattr(self, '_episode_storage')
        return self._episodes

    @property
    def score(self):
        if hasattr(self, '_score'):
            return self._score
        if self.priority > 5:
            self._score = math.log(self.priority - 4) * self.score_const
        elif self.priority < 5:
            self._score = -math.log(abs(self.priority - 6)) * self.score_const
        else:
            self._score = 0
        return self.score


class EpisodeList(list, HasBeenModified):
    def __init__(self, list_):
        list.__init__(self, list_)
        HasBeenModified.__init__(self)

    def append(self, x):
        super().append(x)
        self.modified = True

    def __contains__(self, episode):
        return any(True for e in self if e.guid == episode.guid)


class Episode(HasBeenModified):
    columns = ['guid', 'title', 'link', 'media_href', 'published', 'downloaded']

    def __init__(self, podcast, guid, title, link, media_href, published,
                 downloaded):
        super(Episode, self).__init__()
        self.podcast = podcast
        self.guid = guid
        self.title = title
        self.link = link
        self.media_href = media_href
        self.published = published
        self.downloaded = self.to_bool(downloaded)

    @property
    def published(self):
        return self._published

    @published.setter
    def published(self, value):
        if hasattr(self, '_published'):
            self._published = None
        if isinstance(value, time.struct_time):
            self._published = value
        elif isinstance(value, str):
            self._published = time.strptime(value, '%Y-%m-%d %H:%M:%S')
        else:
            raise TypeError

    @property
    def score(self):
        if self.downloaded:
            return 0
        episode_score = time.mktime(self.published) / 60 / 60 / 24
        podcast_score = self.podcast.score
        return episode_score + podcast_score

    @classmethod
    def from_tuple(cls, podcast, tuple):
        return cls(podcast, *tuple)

    def str_attributes(self):
        return [
            self.guid,
            self.title,
            self.link,
            self.media_href,
            time.strftime('%Y-%m-%d %H:%M:%S', self.published),
            str(self.downloaded),
        ]

    def modified_attr(self, key, value):
        self.podcast.episodes.modified = True

    @staticmethod
    def to_bool(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if value == str(True):
                return True
            elif value == str(False):
                return False
        raise ValueError("Could not convert {} to bool.".format(value))
