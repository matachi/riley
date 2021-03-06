from time import strptime, struct_time
from unittest.mock import MagicMock

import yaml
from riley.models import Podcast, Episode
from riley.storage import FileStorage, FileEpisodeStorage

config = """podcasts:
    kalle:
        feed: http://anka.se
        priority: 5"""


history = """guid,title,link,media_href,published,downloaded
abc,def,ghi,jkl,2012-12-12 12:12:12,True"""


def test_file_storage(tmpdir, monkeypatch):
    config_path = tmpdir.join('config.yml')
    config_path.write(config)
    history_path = tmpdir.join('kalle_history.csv')
    history_path.write(history)

    file_storage = FileStorage()
    monkeypatch.setattr(
        'riley.storage.user_data_dir', lambda x, y: tmpdir.strpath)

    podcasts = file_storage.get_podcasts()

    assert len(podcasts), 1
    podcast = podcasts['kalle']
    assert podcast.name == 'kalle'
    assert podcast.feed == 'http://anka.se'
    assert podcast.priority == 5
    assert len(podcast.episodes) == 1
    episode = podcast.episodes[0]
    assert episode.guid == 'abc'
    assert episode.title == 'def'
    assert episode.link == 'ghi'
    assert episode.media_href == 'jkl'
    assert episode.published == struct_time((
        2012, 12, 12, 12, 12, 12, 2, 347, -1))
    assert episode.downloaded == True


def test_save_podcast(tmpdir, monkeypatch):
    file_storage = FileStorage()
    monkeypatch.setattr(
        'riley.storage.user_data_dir', lambda x, y: tmpdir.strpath)

    podcast = Podcast('abc', 'def', FileEpisodeStorage())
    podcast.episodes.append(Episode(
        podcast, 1, 2, 3, 4,
        strptime('2015-11-12 01:02:03', '%Y-%m-%d %H:%M:%S'), True))

    file_storage.save_podcast(podcast)

    config_path = tmpdir.join('config.yml')
    data = yaml.load(config_path.read())
    assert len(data) == 2
    assert data['podcasts'] == {'abc': {'feed': 'def', 'priority': 5}}
    history_path = tmpdir.join('abc_history.csv')
    assert history_path.read() == \
        'guid,title,link,media_href,published,downloaded\n' \
        '1,2,3,4,2015-11-12 01:02:03,True\n'


def test_dont_save_podcast_if_not_modified(tmpdir, monkeypatch):
    monkeypatch.setattr(
        'riley.storage.user_data_dir', lambda x, y: tmpdir.strpath)

    podcast = Podcast('abc', 'def', MagicMock())

    file_storage = FileStorage()
    save_config_data = MagicMock(side_effect=file_storage._save_config_data)
    file_storage._save_config_data = save_config_data

    file_storage.save_podcast(podcast)
    # Wrote the podcats to disc
    assert file_storage._save_config_data.call_count == 1

    file_storage.save_podcast(podcast)
    # Since the podcast hasn't been modified it wasn't rewritten to disc
    assert file_storage._save_config_data.call_count == 1
