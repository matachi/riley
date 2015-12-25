from itertools import chain
import os
from unittest.mock import MagicMock, call
import time

from riley.commands import WhereIsConfig, DownloadEpisodes, ListPodcasts, \
    Insert, ListEpisodes, FetchEpisodes


def test_where_is_config(capsys, monkeypatch):
    monkeypatch.setattr(
        'riley.commands.AbstractFileStorage._user_data_dir_path', 'abc')
    WhereIsConfig().handle()
    out, _err = capsys.readouterr()
    assert out == 'abc\n'


def test_list_podcasts(capsys, tmpdir, monkeypatch):
    config = """podcasts:
    kalle: http://anka.se
    banka: http://example.com"""
    config_path = tmpdir.join('config.yml')
    config_path.write(config)

    monkeypatch.setattr(
        'riley.storage.user_data_dir', lambda x, y: tmpdir.strpath)

    ListPodcasts().handle()
    out, _err = capsys.readouterr()
    assert out == 'kalle http://anka.se\nbanka http://example.com\n'


def test_insert(tmpdir, monkeypatch):
    monkeypatch.setattr(
        'riley.storage.user_data_dir', lambda x, y: tmpdir.strpath)
    Insert().handle('yolo', 'leet')
    assert tmpdir.join('config.yml').read() == 'podcasts:\n  yolo: leet\n'


def test_list_episodes(capsys, tmpdir, monkeypatch):
    config = """podcasts:
    kalle: http://anka.se"""
    history = """guid,title,link,media_href,published,downloaded
abc,def,ghi,jkl,2012-12-12 10:10:10,mno"""

    config_path = tmpdir.join('config.yml')
    config_path.write(config)
    history_path = tmpdir.join('kalle_history.csv')
    history_path.write(history)

    monkeypatch.setattr(
        'riley.storage.user_data_dir', lambda x, y: tmpdir.strpath)

    ListEpisodes().handle()
    out, _err = capsys.readouterr()
    assert out == 'def jkl\n'


def test_fetch_episodes(tmpdir, monkeypatch):
    # The episode data we expect to find in the history file
    expected_data = [[
        '123',
        'episode 1',
        'http://example.com/episode/3',
        'http://example.com/media.ogg',
        '2015-12-12 12:12:12',
        False
    ], [
        '124',
        'a new hope',
        'http://example.com/episode/4',
        'http://example.com/media-final.ogg',
        '2015-12-12 12:12:12',
        False
    ]]

    # Prepare config files
    config = """podcasts:
    kalle: http://anka.se"""
    config_path = tmpdir.join('config.yml')
    config_path.write(config)
    # Insert one of the episodes into the history file
    history = """guid,title,link,media_href,published,downloaded
{},{},{},{},{},{}""".format(*expected_data[0])
    history_path = tmpdir.join('kalle_history.csv')
    history_path.write(history)
    monkeypatch.setattr(
        'riley.storage.user_data_dir', lambda x, y: tmpdir.strpath)

    # Prepare the feedparser, which will return a feed containing both episodes
    feedparser, feed, entry1, entry2, enclosure1, enclosure2 = [
        MagicMock() for _ in range(6)]
    feedparser.parse.return_value = feed
    feed.entries = [entry1, entry2]
    entry1.enclosures = [enclosure1]
    entry2.enclosures = [enclosure2]
    enclosure1.href = expected_data[0][3]
    enclosure2.href = expected_data[1][3]
    entry1.guid = expected_data[0][0]
    entry2.guid = expected_data[1][0]
    entry1.title = expected_data[0][1]
    entry2.title = expected_data[1][1]
    entry1.link = expected_data[0][2]
    entry2.link = expected_data[1][2]
    entry1.published_parsed = time.struct_time(
        (2015, 12, 12, 12, 12, 12, 5, 346, -1))
    entry2.published_parsed = time.struct_time(
        (2015, 12, 12, 12, 12, 12, 5, 346, -1))
    monkeypatch.setattr('riley.commands.feedparser', feedparser)

    # Fetch new episodes
    FetchEpisodes().handle()

    # There should be two episodes in the file, since one was a duplicate (it
    # had already been fetched previously)
    expected_read = """guid,title,link,media_href,published,downloaded
{},{},{},{},{},{}
{},{},{},{},{},{}\n""".format(*chain(*expected_data))
    assert history_path.read() == expected_read


def test_download_episodes(tmpdir, monkeypatch):
    config = """podcasts:
    kalle: http://anka.se"""
    history = """guid,title,link,media_href,published,downloaded
abc,def,ghi,jkl,2012-12-12 10:10:10,False"""

    config_path = tmpdir.join('config.yml')
    config_path.write(config)
    history_path = tmpdir.join('kalle_history.csv')
    history_path.write(history)
    monkeypatch.setattr(
        'riley.storage.user_data_dir', lambda x, y: tmpdir.strpath)

    download_class_mock = MagicMock()
    monkeypatch.setattr('riley.commands.download', download_class_mock)

    DownloadEpisodes().handle('kalle', '0')

    assert download_class_mock.download.call_args_list == [
        call('jkl', os.getcwd()),
    ]
    expected_read = """guid,title,link,media_href,published,downloaded
abc,def,ghi,jkl,2012-12-12 10:10:10,True\n"""
    assert history_path.read() == expected_read
