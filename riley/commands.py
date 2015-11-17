import argparse
import os
import sys
import feedparser
from riley import download
from riley.models import Podcast, Storage


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
        print(Storage().user_data_dir_path)


class ListPodcasts(BaseCommand):
    help = 'Print a list of podcasts.'

    def handle(self):
        for podcast in Podcast.objects().values():
            print(podcast.name, podcast.feed)


class Insert(BaseCommand):
    help = 'Add a podcast.'

    def add_arguments(self, parser):
        parser.add_argument(
            'name', metavar='name', type=str, help='podcast name')
        parser.add_argument(
            'url', metavar='url', type=str, help='podcast feed URL')

    def handle(self, name, url):
        if name not in Podcast.objects().keys():
            Podcast(name, url).save()
        else:
            sys.exit("The name '%s' is already registered." % name)


class ListEpisodes(BaseCommand):
    help = 'Print a list of episodes.'

    def handle(self):
        for podcast in Podcast.objects().values():
            for episode in podcast.episodes:
                print(episode.title, episode.media_href)


class FetchEpisodes(BaseCommand):
    help = 'Fetch episodes.'

    def handle(self):
        for podcast in Podcast.objects().values():
            feed = feedparser.parse(podcast.feed)
            episodes = []
            for entry in feed.entries:
                if len(entry.enclosures) == 0:
                    continue
                media_href = entry.enclosures[0].href
                episodes.append(
                    (entry.guid, entry.title, entry.link, media_href, False))
            podcast.extend_episodes(episodes)


class DownloadEpisodes(BaseCommand):
    help = 'Download episodes.'

    def add_arguments(self, parser):
        parser.add_argument(
            'podcast_name', metavar='podcast', type=str, help='podcast name')
        parser.add_argument(
            'episodes', metavar='episodes', type=str,
            help='episodes to download')

    def handle(self, podcast_name, episodes):
        if podcast_name is not None:
            episode_indices_to_download = set()
            elements = episodes.split(',')
            for element in elements:
                if element.isnumeric():
                    # It's a single number
                    episode_indices_to_download.add(int(element))
                elif '-' in element:
                    start, finish = map(int, element.split('-'))
                    episode_indices_to_download.update(range(start, finish + 1))
            episodes = Podcast.objects()[podcast_name].episodes
            for index in episode_indices_to_download:
                download.download(episodes[index].media_href, os.getcwd())
        else:
            for podcast in Podcast.objects().values():
                for episode in podcast.episodes:
                    download.download(episode.media_href, os.getcwd())
                    break
