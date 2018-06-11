"""
# Queue Naming

Here we define the queues based on the import signature. The queues are named
along the following lines:

## User-based queues

If a task requires one specific user, we add it to an aptly-named queue. Tasks
such as checking the inbox of a particular user, would require that user to be
logged in, so we place it in a queue named `u_{username}`.

**Example:**

/u/TranscribersOfReddit will monitor the `u_transcribersofreddit` queue

## Role-based queues

If a task requires a specific role, t will be added to a queue with the
following formula:

Take the most-restrictive role as `role` (e.g., `role = 'tor_mod'`). The queue
will be named `f_{role}`. The prefix 'f' stands for feature so it does not
confuse others with subreddit names (e.g., /r/tor_mod -> `r_tor_mod`)

## Generic queue

If something does not have any particular requirements (e.g., no rate-limiting
or concurrency issues to work around), we put it in the 'r_anyone' queue. All
tasks not explicitly declared below are put in that queue.
"""

from typing import (
    Dict,
    Any,
)
import logging
import os

from tor_worker import __version__
from tor_core import __BROKER_URL__

from tor.celeryconfig import Config as TorConfig

from celery import Celery, signals


class Config:
    timezone = 'UTC'
    enable_utc = True
    task_default_queue = 'r_anyone'
    beat_schedule: Dict[str, Dict[str, Any]] = {
    }
    task_routes = tuple()


@signals.after_setup_task_logger.connect
def setup_logging(logger, *args, **kwargs):
    """
    Sets up Bugsnag and Sentry logging
    """
    import bugsnag

    bs_api_key = os.environ.get('BUGSNAG_API_KEY', None)
    if bs_api_key:
        bugsnag.configure(api_key=bs_api_key,
                          app_version=__version__)

        bs = bugsnag.handler.BugsnagHandler()
        bs.setLevel(logging.ERROR)
        logging.getLogger('').addHandler(bs)
        logger.debug('Added Bugsnag error reporting handler')
    else:
        logger.warning('Missing BUGSNAG_API_KEY environment variable. '
                       'Bugsnag setup was skipped.')


cfg = Config()

for obj in [TorConfig]:
    for key, value in obj.beat_schedule.items():
        cfg.beat_schedule[key] = value

    cfg.task_routes += obj.task_routes

cfg.beat_schedule = {}
app = Celery('tor', broker=__BROKER_URL__)
app.config_from_object(cfg)

task_packages = ','.split(os.getenv('TOR_BOT_PACKAGES',
                                    'tor,tor_archivist,tor_ocr'))
task_packages = [name.strip() for name in task_packages if name.strip()]
app.autodiscover_tasks(force=True, packages=task_packages)
