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
    def __init__(self, name, feed, episode_storage):
        super(Podcast, self).__init__()
        self.name = name
        self.feed = feed
        self._episode_storage = episode_storage

    @property
    def episodes(self):
        if not hasattr(self, '_episodes'):
            self._episodes = EpisodeList(
                self._episode_storage.get_episodes(self))
            delattr(self, '_episode_storage')
        return self._episodes


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
        if isinstance(published, time.struct_time):
            self.published = published
        elif isinstance(published, str):
            self.published = time.strptime(published, '%Y-%m-%d %H:%M:%S')
        else:
            raise TypeError
        self.downloaded = downloaded

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
            self.downloaded
        ]

    def modified_attr(self, key, value):
        self.podcast.episodes.modified = True
