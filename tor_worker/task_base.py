import os

import celery

import praw
import redis
from slackclient import SlackClient

from tor_worker import __version__, cached_property
from tor_worker.http import Http


class InvalidUser(Exception):
    pass


class Task(celery.Task):
    """
    Base class with lazy-loaded clients for external resources
    """
    @cached_property
    def reddit(self):  # pragma: no cover
        return praw.Reddit(
            check_for_updates=False,
            user_agent=f'praw:org.grafeas.tor_worker:v{__version__} '
            '(by the mods of /r/TranscribersOfReddit)',
        )

    @cached_property
    def redis(self):  # pragma: no cover
        return redis.StrictRedis()

    @cached_property
    def http(self):  # pragma: no cover
        return Http()

    @cached_property
    def slack(self):  # pragma: no cover
        return SlackClient(os.environ['SLACK_API_KEY'])

    autoretry_for = ()
    retry_backoff = True
    max_retries = 9

    track_started = True
