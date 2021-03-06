from time import struct_time

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
            Episode(podcast, 1, 2, 3, 4, '2012-05-06 07:08:09', True),
            Episode(podcast, 6, 7, 8, 9, '2012-06-07 07:08:09', False),
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
    assert episodes[0].published == struct_time((
        2012, 5, 6, 7, 8, 9, 6, 127, -1))
    assert episodes[0].downloaded == True
    assert episodes[1].guid == 6
    assert episodes[1].title == 7
    assert episodes[1].link == 8
    assert episodes[1].media_href == 9
    assert episodes[1].published == struct_time((
        2012, 6, 7, 7, 8, 9, 3, 159, -1))
    assert episodes[1].downloaded == False

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
    episodes.append(Episode(podcast, 11, 12, 13, 14, '2012-12-12 12:12:12', True))
    assert len(episodes) == 3
    assert not podcast.modified
    assert episodes.modified
    assert not episodes[0].modified
    assert not episodes[1].modified
    assert not episodes[2].modified


def test_calculate_time_based_score():
    podcast = Podcast('name', 'feed', DummyEpisodeStorage())
    episode = Episode(podcast, 0, "a", "b", "c", '2016-03-03 10:00:00', False)
    score = episode.score
    episode.published = '2016-03-04 10:00:00'
    new_score = episode.score
    assert new_score - score == 1
    score = episode.score
    episode.published = '2016-04-04 11:00:00'
    new_score = episode.score
    assert new_score - score == 31


def test_score_already_downloaded_episode():
    podcast = Podcast('name', 'feed', DummyEpisodeStorage())
    episode = Episode(podcast, 0, "a", "b", "c", '2016-03-03 10:00:00', True)
    score = episode.score
    assert score == 0


def test_score_podcast_priority():
    ep_storage = DummyEpisodeStorage()

    p1 = Podcast('name', 'feed', ep_storage)
    e1 = Episode(p1, 1, 'a', 'b', 'c', '2016-03-15 00:00:00', False)
    e2 = Episode(p1, 2, 'a', 'b', 'c', '2016-03-30 00:00:00', False)
    assert p1.priority == 5

    p2 = Podcast('name', 'feed', ep_storage, 6)
    e3 = Episode(p2, 3, 'a', 'b', 'c', '2016-03-20 00:00:00', False)

    assert p2.score > p1.score
    # The second podcast has higher rank
    assert e2.published > e3.published > e1.published
    # Episode 3 was published between 2 and 1
    assert e3.score > e2.score > e1.score
    # Episode 3 still gets a higher score due to its podcast's score
