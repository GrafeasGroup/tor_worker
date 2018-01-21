from tor_worker.cli.base import add_base_args

def register_work_subcommand(subparser):
    parser = subparser.add_parser('work')
    parser.set_defaults(func=run_worker)
    add_base_args(parser)


def run_worker(options):
    pass
