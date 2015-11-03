import sys

from riley.commands import Insert, List, ListPodcasts


class ManagementUtility:
    subcommands = {
        'list': List,
        'insert': Insert,
        'podcasts': ListPodcasts,
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
