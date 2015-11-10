#!/usr/bin/env python3
import sys
from riley.commands import ListPodcasts, FetchEpisodes, ListEpisodes, Insert, \
    DownloadEpisodes, WhereIsConfig


class ManagementUtility:
    subcommands = {
        'list': ListEpisodes,
        'insert': Insert,
        'podcasts': ListPodcasts,
        'fetch': FetchEpisodes,
        'download': DownloadEpisodes,
        'config': WhereIsConfig,
    }

    def execute(self, argv):
        if len(argv) > 1:
            subcommand = argv[1]
        else:
            subcommand = 'list'
            argv += ['list']
        try:
            command = self.subcommands[subcommand]()
        except AttributeError:
            sys.exit('%s is not a valid subcommand.' % subcommand)
        command.execute(argv)


def main():
    ManagementUtility().execute(sys.argv)


if __name__ == '__main__':
    main()
