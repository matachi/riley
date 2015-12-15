from riley.models import Podcast, Episode
from riley.storage import FileStorage, FileEpisodeStorage

config = """podcasts:
    kalle: http://anka.se"""


history = """guid,title,link,media_href,downloaded
abc,def,ghi,jkl,mno"""


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
    assert len(podcast.episodes) == 1
    episode = podcast.episodes[0]
    assert episode.guid == 'abc'
    assert episode.title == 'def'
    assert episode.link == 'ghi'
    assert episode.media_href == 'jkl'
    assert episode.downloaded == 'mno'


def test_save_podcast(tmpdir, monkeypatch):
    file_storage = FileStorage()
    monkeypatch.setattr(
        'riley.storage.user_data_dir', lambda x, y: tmpdir.strpath)

    podcast = Podcast('abc', 'def', FileEpisodeStorage())
    podcast.episodes.append(Episode(podcast, 1, 2, 3, 4, 5))

    file_storage.save_podcast(podcast)

    config_path = tmpdir.join('config.yml')
    assert config_path.read() == 'podcasts:\n  abc: def\n'
    history_path = tmpdir.join('abc_history.csv')
    assert history_path.read() == 'guid,title,link,media_href,downloaded\n' \
                                  '1,2,3,4,5\n'
