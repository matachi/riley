from riley.models import HasBeenModified, Podcast, Episode
from riley.storage import EpisodeStorage


class Child(HasBeenModified):
    def __init__(self):
        super().__init__()
        self.var = 'test'


def test_has_been_modified():
    child = Child()
    assert not child.modified
    # Do some write operation
    child.var = 123
    assert child.modified
    child.modified = False
    assert not child.modified
    # Change to the same value
    child.var = 123
    assert not child.modified


class DummyEpisodeStorage(EpisodeStorage):
    def save_episodes(self, podcast):
        pass

    def get_episodes(self, podcast):
        return [
            Episode(podcast, 1, 2, 3, 4, 5),
            Episode(podcast, 6, 7, 8, 9, 10),
        ]


def test_podcast_and_episode():
    episode_storage = DummyEpisodeStorage()
    name = 'name'
    feed = 'http://example.com/feed.xml'

    podcast = Podcast(name, feed, episode_storage)
    assert podcast.name == name
    assert podcast.feed == feed
    assert podcast._episode_storage is episode_storage

    assert hasattr(podcast, '_episode_storage')
    assert not hasattr(podcast, '_episodes')
    episodes = podcast.episodes
    assert not hasattr(podcast, '_episode_storage')
    assert hasattr(podcast, '_episodes')

    assert episodes[0].guid == 1
    assert episodes[0].title == 2
    assert episodes[0].link == 3
    assert episodes[0].media_href == 4
    assert episodes[0].downloaded == 5
    assert episodes[1].guid == 6
    assert episodes[1].title == 7
    assert episodes[1].link == 8
    assert episodes[1].media_href == 9
    assert episodes[1].downloaded == 10

    assert not podcast.modified
    assert not episodes.modified
    assert not episodes[0].modified
    assert not episodes[1].modified
    episodes[0].guid = 11
    assert not podcast.modified
    assert episodes.modified
    assert episodes[0].modified
    assert not episodes[1].modified

    episodes.modified = False
    episodes[0].modified = False

    assert not podcast.modified
    assert not episodes.modified
    assert not episodes[0].modified
    assert not episodes[1].modified
    assert len(episodes) == 2
    episodes.append(Episode(podcast, 11, 12, 13, 14, 15))
    assert len(episodes) == 3
    assert not podcast.modified
    assert episodes.modified
    assert not episodes[0].modified
    assert not episodes[1].modified
    assert not episodes[2].modified
