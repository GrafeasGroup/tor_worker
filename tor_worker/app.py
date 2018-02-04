import logging
import os

from tor_worker import __BROKER_URL__, __version__

from celery import Celery, signals


app = Celery('tor_worker', broker=__BROKER_URL__)
app.conf.timezone = 'UTC'
app.conf.enable_utc = True
app.conf.task_default_queue = 'default'

app.conf.beat_schedule = {
    # 'check_inbox': {
    #     'task': 'tor_worker.tasks.moderator.check_inbox',
    #     'schedule': 90,
    # },
    'check-subreddit-feeds': {
        'task': 'tor_worker.tasks.anyone.check_new_feeds',
        'schedule': 30,  # seconds
    },
    # 'test-system': {
    #     'task': 'tor_worker.tasks.anyone.test_system',
    #     'schedule': 15,
    # },
}

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
or concurrency issues to work around), we put it in the 'default' queue. All
tasks not explicitly declared below are put in that queue.
"""
app.conf.task_routes = ([
    ('tor_worker.tasks.moderator.check_inbox', {
        'queue': 'u_transcribersofreddit'
    }),
    ('tor_worker.tasks.moderator.process_message', {
        'queue': 'u_transcribersofreddit'
    }),
    ('tor_worker.tasks.moderator.send_bot_message', {
        'queue': 'u_transcribersofreddit'
    }),
    ('tor_worker.tasks.moderator.*', {
        'queue': 'f_tor_mod'
    }),
],)


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


# All of the below imports are 'useless', per static analysis, but required for
# celery to register all of the tasks in the system
import tor_worker.tasks.moderator  # noqa
import tor_worker.tasks.anyone  # noqa
