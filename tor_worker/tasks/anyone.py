from tor_worker.config import Config
from tor_worker.tasks.base import Task

from celery.utils.log import get_task_logger
from celery import (
    current_app as app,
    signature
)


log = get_task_logger(__name__)


@app.task(bind=True, ignore_result=True, base=Task)
def send_to_slack(self, message, channel):
    self.slack.api_call('chat.postMessage',
                        channel=channel,
                        text=message)


@app.task(bind=True, ignore_result=True, base=Task)
def check_new_feeds(self):  # pragma: no coverage
    config = Config()

    for sub in config.subreddits:
        check_new_feed.delay(sub)


@app.task(bind=True, rate_limit='50/m', base=Task)
def check_new_feed(self, subreddit):
    # Using `signature` here so we don't have a recursive import loop
    post_to_tor = signature('tor_worker.tasks.moderator.post_to_tor')

    config = Config.subreddit(subreddit)

    r = self.http.get(f'https://www.reddit.com/r/{subreddit}/new.json')
    r.raise_for_status()
    feed = r.json()

    if feed['kind'].lower() != 'listing':  # pragma: no coverage
        raise 'Invalid payload for listing'

    cross_posts = 0

    for feed_item in feed['data']['children']:
        if feed_item['kind'].lower() != 't3':  # pragma: no coverage
            # Only allow t3 (submission) types
            log.warning(f'Unsupported kind in /new feed with {repr(feed_item)}')
            continue
        if feed_item['data']['is_self']:
            # Self-posts don't need to be transcribed. Duh!
            continue
        if feed_item['data']['locked'] or feed_item['data']['archived']:
            # No way to comment with a transcription if post is read-only
            continue
        if feed_item['data']['author'] is None:
            # Author gone means deleted, and we don't want to cross-post then
            continue
        if self.redis.sismember('post_ids', feed_item['data']['id']):
            # Post is already processed, but may not be completed
            continue
        if not config.filters.score_allowed(feed_item['data']['score']):
            # Must meet subreddit-specific settings on score threshold
            continue
        if not config.filters.url_allowed(feed_item['data']['domain']):
            # Must be on one of the whitelisted domains (if any given)
            continue

        post_to_tor.apply_async(
            kwargs={
                'sub': feed_item['data']['subreddit'],
                'title': feed_item['data']['title'],
                'link': feed_item['data']['permalink'],
                'domain': feed_item['data']['domain'],
            }
        )
        cross_posts += 1

    log.info(f'Found {cross_posts} posts for /r/{subreddit}')


@app.task(bind=True, ignore_result=True, base=Task)
def test_system(self):  # pragma: no coverage
    import time
    import random

    log.info('starting task')
    time.sleep(random.choice(range(10)))
    log.info('done with task')
