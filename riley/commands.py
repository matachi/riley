import argparse
import os
import sys
from itertools import chain

import feedparser
from riley import download
from riley.models import Podcast, Episode
from riley.storage import AbstractFileStorage, FileStorage, FileEpisodeStorage


class BaseCommand:
    # Metadata about the command
    help = ''

    def create_parser(self, prog_name, subcommand):
        parser = argparse.ArgumentParser(
            prog='%s %s' % (prog_name, subcommand),
            description=self.help or None)
        self.add_arguments(parser)
        return parser

    def add_arguments(self, parser):
        pass

    def execute(self, argv):
        parser = self.create_parser(os.path.basename(argv[0]), argv[1])
        options = vars(parser.parse_args(argv[2:]))
        self.handle(**options)

    def handle(self, *args, **options):
        raise NotImplementedError(
            'Subclasses of BaseCommand must provide a handle() method.')


class WhereIsConfig(BaseCommand):
    help = 'Print the path to the config directory.'

    def handle(self):
        print(AbstractFileStorage()._user_data_dir_path)


class ListPodcasts(BaseCommand):
    help = 'Print a list of podcasts.'

    def handle(self):
        for podcast in FileStorage().get_podcasts().values():
            try:
                print(podcast.name, podcast.feed)
            except BrokenPipeError:
                return


class Insert(BaseCommand):
    help = 'Add a podcast.'

    def add_arguments(self, parser):
        parser.add_argument(
            'name', metavar='name', type=str, help='podcast name')
        parser.add_argument(
            'url', metavar='url', type=str, help='podcast feed URL')

    def handle(self, name, url):
        file_storage = FileStorage()
        if name not in file_storage.get_podcasts():
            file_storage.save_podcast(Podcast(name, url, FileEpisodeStorage()))
        else:
            sys.exit("The name '%s' is already registered." % name)


class ListEpisodes(BaseCommand):
    help = 'Print a list of episodes.'

    def add_arguments(self, parser):
        parser.add_argument(
            'podcast_name', metavar='podcast', type=str, nargs='?',
            help='podcast name')

    def handle(self, podcast_name=None):
        if podcast_name is not None:
            episodes = FileStorage().get_podcasts()[podcast_name].episodes
        else:
            episodes = []
            for podcast in FileStorage().get_podcasts().values():
                episodes.extend(podcast.episodes)
            episodes.sort(key=lambda e: e.published, reverse=True)
        for episode in episodes:
            try:
                print(episode.title, episode.media_href)
            except BrokenPipeError:
                return


class FetchEpisodes(BaseCommand):
    help = 'Fetch episodes.'

    def handle(self):
        for podcast in FileStorage().get_podcasts().values():
            feed = feedparser.parse(podcast.feed)
            episodes = []
            for entry in feed.entries:
                enclosures = getattr(entry, 'enclosures', [])
                if len(enclosures) == 0:
                    continue
                # Use an empty string when no link is available
                link = getattr(entry, 'link', '')
                media_href = entry.enclosures[0].href
                episodes.append(
                    Episode(podcast, entry.guid, entry.title, link, media_href,
                            entry.published_parsed, False))
            for episode in episodes:
                if episode not in podcast.episodes:
                    podcast.episodes.append(episode)
            FileEpisodeStorage().save_episodes(podcast)


class DownloadEpisodes(BaseCommand):
    help = 'Download episodes.'

    def add_arguments(self, parser):
        parser.add_argument(
            'podcast_name', metavar='podcast', type=str, nargs='?',
            help='podcast name')
        parser.add_argument(
            'episode_ranges', metavar='episodes', type=str, nargs='?',
            help='episodes to download')

    def handle(self, podcast_name, episode_ranges):
        file_storage = FileStorage()

        podcasts = file_storage.get_podcasts()
        if podcast_name is not None:
            episode_indices_to_download = self.get_indices(episode_ranges)
            if podcast_name in podcasts:
                podcast = podcasts[podcast_name]
            else:
                list_of_podcasts = '\n'.join(
                    '* %s' % name for name in podcasts.keys())
                sys.exit('\n'.join([
                    "A podcast with the name '%s' does not exist." % podcast_name,
                    "",
                    "Try one of these instead:",
                    "",
                    list_of_podcasts
                ]))
            if episode_indices_to_download[-1] < len(podcast.episodes):
                episodes = [podcast.episodes[i] for i in episode_indices_to_download]
            else:
                last = episode_indices_to_download[-1]
                sys.exit('\n'.join([
                    "The podcast does not have an episode with index '%d'." % last,
                    "",
                    "The valid range is: [%d, %d]" % (0, len(podcast.episodes) - 1),
                ]))
        else:
            episodes = chain.from_iterable(
                podcast.episodes for podcast in podcasts.values())

        download_directory = file_storage.get_config()['storage']
        for episode in episodes:
            download.download(episode.media_href, download_directory,
                              episode.published)
            episode.downloaded = True
            FileStorage().save_podcast(episode.podcast)

    @staticmethod
    def get_indices(string):
        """

        >>> DownloadEpisodes.get_indices('1')
        [1]
        >>> DownloadEpisodes.get_indices('1,3,5')
        [1, 3, 5]
        >>> DownloadEpisodes.get_indices('1,3-5,7')
        [1, 3, 4, 5, 7]
        >>> DownloadEpisodes.get_indices('1,7,1-2,1-3')
        [1, 2, 3, 7]

        :param str string: Sring with elements.
        :return: List of indices.
        """
        episode_indices_to_download = set()
        elements = string.split(',')
        for element in elements:
            if element.isnumeric():
                # It's a single number
                episode_indices_to_download.add(int(element))
            elif '-' in element:
                start, finish = map(int, element.split('-'))
                episode_indices_to_download.update(range(start, finish + 1))
        return list(episode_indices_to_download)
