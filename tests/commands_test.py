import os

from unittest.mock import MagicMock, call

from riley.commands import DownloadEpisodes
from riley.models import Episode


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
