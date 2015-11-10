import argparse
import os
import sys
from urllib import request
import feedparser
from riley.models import Podcast


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
            for guid, title, url, media_href in podcast.episodes:
                print(title, media_href)


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
                    (entry.guid, entry.title, entry.link, media_href))
            podcast.extend_episodes(episodes)


class DownloadEpisodes(BaseCommand):
    help = 'Download episodes.'

    def handle(self):
        for podcast in Podcast.objects().values():
            for _, _, _, media_href in podcast.episodes:
                mp3file = request.urlopen(media_href)
                output = open('test.mp3', 'wb')
                output.write(mp3file.read())
                output.close()
                break
