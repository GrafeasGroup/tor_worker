from tor_worker import OUR_BOTS
from tor_worker.config import Config
from tor_worker.context import (
    is_code_of_conduct,
    is_claimed_post_response,
    is_claimable_post,
)
from tor_worker.tasks.base import Task

import re

from celery.utils.log import get_task_logger
from celery import (
    current_app as app,
    signature
)
from praw.models import Comment


log = get_task_logger(__name__)

MOD_SUPPORT_PHRASES = [
    re.compile('fuck', re.IGNORECASE),
    re.compile('unclaim', re.IGNORECASE),
    re.compile('undo', re.IGNORECASE),
    re.compile('(?:good|bad) bot', re.IGNORECASE),
]


def process_mod_intervention(comment: Comment, reddit):
    """
    Triggers an alert in Slack with a link to the comment if there is something
    offensive or in need of moderator intervention
    """
    phrases = []
    for regex in MOD_SUPPORT_PHRASES:
        matches = regex.search(comment.body)
        if not matches:
            continue

        phrases.append(matches.group())

    if len(phrases) == 0:
        # Nothing offensive here, why did this function get triggered?
        return

    # Wrap each phrase in double-quotes (") and commas in between
    phrases = '"' + '", "'.join(phrases) + '"'

    title = 'Mod Intervention Needed'
    message = f'Detected use of {phrases} <{comment.submission.shortlink}>'

    # TODO: send message to slack
    send_to_slack.delay(
        f':rotating_light::rotating_light: {title} '
        f':rotating_light::rotating_light:\n\n'
        f'{message}',
        '#general'
    )


@app.task(bind=True, ignore_result=True, base=Task)
def send_to_slack(self, message, channel):
    self.slack.api_call('chat.postMessage',
                        channel=channel,
                        text=message)


@app.task(bind=True, ignore_result=True, base=Task)
def process_comment(self, comment_id):
    """
    Processes a notification of comment being made, routing to other tasks as
    is deemed necessary
    """
    reply = self.reddit.comment(comment_id)

    if reply.author.name in OUR_BOTS:
        return

    body = reply.body.lower()
    process_mod_intervention(reply, self.reddit)

    if is_code_of_conduct(reply.parent):
        if re.search(r'\bi accept\b', body):  # pragma: no coverage
            # TODO: Fill out coc accept scenario and remove pragma directive
            pass
        else:  # pragma: no coverage
            # TODO: Fill out error scenario and remove pragma directive
            pass

    elif is_claimed_post_response(reply.parent):
        if re.search(r'\b(?:done|deno)\b', body):  # pragma: no coverage
            # TODO: Fill out done scenario and remove pragma directive
            pass
        elif re.search(r'(?=<^|\W)!override\b', body):  # pragma: no coverage
            # TODO: Fill out override scenario and remove pragma directive
            pass
        else:  # pragma: no coverage
            # TODO: Fill out error scenario and remove pragma directive
            pass

    elif is_claimable_post(reply.parent):
        if re.search(r'\bclaim\b', body):  # pragma: no coverage
            # TODO: Fill out claim scenario and remove pragma directive
            pass
        else:  # pragma: no coverage
            # TODO: Fill out error scenario and remove pragma directive
            pass


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
