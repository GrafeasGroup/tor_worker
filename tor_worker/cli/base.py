import argparse
import logging
import os
import sys

from tor_worker import __version__

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('ERROR: {msg}\n\n'.format(msg=message))
        self.print_help()
        sys.exit(2)


def add_logging_args(parser):
    """
    Adds CLI flags for modifying how verbose the output stream of
    messages should be.
    """
    s = parser.add_mutually_exclusive_group()
    s.add_argument('-V', dest='verbosity', default=0, action='count',
                   help="Squawks more output the more V's are added: `-V`"
                        " or `-VV`")
    s.add_argument('--verbose', dest='verbosity', action='store_const',
                   const=1, help='Prints more output to help with debugging')
    s.add_argument('-q', dest='quiet', default=0, action='count',
                   help="Silences output the more q's are added: `-qqq`"
                        "or `-qq`")
    s.add_argument('--quiet', dest='quiet', action='store_const', const=1,
                   help='Silences output to only display warnings and errors')


def add_base_args(parser):
    """Basic CLI flags on every sub-command"""
    parser.add_argument('--version', '-v', action='version',
                        help='Prints the program version and exits',
                        version='tor-worker ' + __version__)


def setup_logger(options):
    """
    Creates the default logging format and level, based on CLI flags for verbosity
    """
    logging.basicConfig(format='[%(levelname)s] %(funcName)s | %(message)s')
    log = logging.getLogger('tor_worker')

    if options.verbosity > 0:
        log.setLevel(logging.DEBUG)
    elif options.verbosity == 0 and options.quiet == 0:  # default
        log.setLevel(logging.INFO)
    elif options.quiet == 1:
        log.setLevel(logging.WARNING)
    elif options.quiet == 2:
        log.setLevel(logging.ERROR)
    elif options.quiet == 3:
        log.setLevel(logging.CRITICAL)
    elif options.quiet > 3:  # squash all output
        log.setLevel(logging.CRITICAL + 1)
    else:
        # Yes, we want to blow up if it gets here
        raise NotImplementedError('Inaccessible code block reached')

    return log
