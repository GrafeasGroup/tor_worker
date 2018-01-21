from tor_worker.cli.base import (
    MyParser,
    add_base_args,
    add_logging_args,
)
from tor_worker.cli.work import register_work_subcommand


def add_subcommands(parser):
    sub = parser.add_subparsers()

    register_work_subcommand(sub)
    pass


def main():
    """Main entrypoint for worker-queue consumer CLI"""
    p = MyParser()
    add_base_args(p)
    add_logging_args(p)
    add_subcommands(p)

    options = p.parse_args()

    if options.func:
        options.func(options)
