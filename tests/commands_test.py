import os

from unittest.mock import MagicMock, call

from riley.commands import WhereIsConfig, DownloadEpisodes, ListPodcasts, \
    Insert, ListEpisodes
from riley.models import Episode


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
    history = """guid,title,link,media_href,downloaded
abc,def,ghi,jkl,mno"""

    config_path = tmpdir.join('config.yml')
    config_path.write(config)
    history_path = tmpdir.join('kalle_history.csv')
    history_path.write(history)

    monkeypatch.setattr(
        'riley.storage.user_data_dir', lambda x, y: tmpdir.strpath)

    ListEpisodes().handle()
    out, _err = capsys.readouterr()
    assert out == 'def jkl\n'


def test_download_episodes(monkeypatch):
    podcast_name = 'name'
    episodes = [Episode(i, i, i, i, i, i) for i in range(10)]

    podcast_object_mock = MagicMock()
    podcast_object_mock.episodes = episodes

    podcast_class_mock = MagicMock()
    podcast_class_mock.objects.return_value = {
        podcast_name: podcast_object_mock}

    download_class_mock = MagicMock()

    monkeypatch.setattr('riley.commands.Podcast', podcast_class_mock)
    monkeypatch.setattr('riley.commands.download', download_class_mock)

    DownloadEpisodes().handle(podcast_name, '1-1,3,5-7')

    assert download_class_mock.download.call_args_list == [
        call(1, os.getcwd()),
        call(3, os.getcwd()),
        call(5, os.getcwd()),
        call(6, os.getcwd()),
        call(7, os.getcwd()),
    ]
