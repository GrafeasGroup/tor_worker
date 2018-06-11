import subprocess
import sys

# from celery.bin import control
from tor_core import CELERY_CONFIG_MODULE


def main():
    # Set default options
    argv = [
        'celery',
        '-A', CELERY_CONFIG_MODULE,
        'inspect',
    ]

    # override any options given after the fact
    argv_orig = list(sys.argv)
    argv_orig.pop(0)

    subprocess.call(argv + argv_orig)
    # ctl = control.control(app=None)
    # ctl.execute_from_commandline(argv=(argv + argv_orig))


if __name__ == '__main__':
    main()
