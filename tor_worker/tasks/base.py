import os

import celery

import praw
import requests
import redis
from slackclient import SlackClient

from tor_worker import __version__


_missing = object()


# @see https://stackoverflow.com/a/17487613/1236035
class cached_property(object):  # pragma: no cover
    """A decorator that converts a function into a lazy property.  The
    function wrapped is called the first time to retrieve the result
    and then that calculated result is used the next time you access
    the value::

        class Foo(object):

            @cached_property
            def foo(self):
                # calculate something important here
                return 42

    The class has to have a `__dict__` in order for this property to
    work.
    """

    # implementation detail: this property is implemented as non-data
    # descriptor. non-data descriptors are only invoked if there is no
    # entry with the same name in the instance's __dict__. this allows
    # us to completely get rid of the access function call overhead. If
    # one chooses to invoke __get__ by hand the property will still work
    # as expected because the lookup logic is replicated in __get__ for
    # manual invocation.

    def __init__(self, func, name=None, doc=None):
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __get__(self, obj, _type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, _missing)
        if value is _missing:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value


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
        conn = redis.StrictRedis()

        return conn

    @cached_property
    def http(self):  # pragma: no cover
        http = requests.Session()
        http.headers.update({
            'User-Agent': f'python:org.grafeas.tor_worker:v{__version__} '
                          '(by the mods of /r/TranscribersOfReddit)',
        })
        return http

    @cached_property
    def slack(self):  # pragma: no cover
        if os.getenv('SLACK_API_KEY'):
            return SlackClient(os.getenv('SLACK_API_KEY'))

    autoretry_for = ()
    retry_backoff = True
    max_retries = 9

    track_started = True
