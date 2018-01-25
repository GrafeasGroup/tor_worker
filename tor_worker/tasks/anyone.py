from tor_worker import OUR_BOTS
from tor_worker.context import (
    is_code_of_conduct,
    is_claimed_post_response,
    is_claimable_post,
)
from tor_worker.moderation import process_mod_intervention
from tor_worker.tasks.base import (
    RedditTask,
    AnonymousTask,
)

import time

from celery.utils.log import get_task_logger
from celery import current_app as app
from slackclient import SlackClient


log = get_task_logger(__name__)


@app.task(bind=True, base=AnonymousTask)
def send_to_slack(self, message, channel):
    """
    """
    client = SlackClient(self.env.slack_api_key)

    client.api_call('chat.postMessage',
                    channel=channel,
                    text=message)


@app.task(bind=True, base=RedditTask)
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
        if 'i accept' in body:
            pass
        else:
            pass

    elif is_claimed_post_response(reply.parent):
        if 'done' in body:
            pass
        elif '!override' in body:
            pass
        else:
            pass

    elif is_claimable_post(reply.parent):
        if 'claim' in body:
            pass
        else:
            pass


@app.task(bind=True, base=AnonymousTask)
def check_new_feed(self):
    r = self.http.get('https://www.reddit.com/r/ProgrammerHumor/new.json')
    r.raise_for_status()
    feed = r.json()

    long_link = 'https://www.reddit.com{}'

    # TODO: Move this outside of the scope of this task
    AUTHORIZED_DOMAINS = [
        'i.imgur.com',
        'imgur.com',
        'i.imgflip.com',
        'i.redd.it',
        'v.redd.it',
    ]

    if feed['kind'].lower() != 'listing':
        raise 'Invalid payload'

    cross_posts = []

    for feed_item in feed['data']['children']:
        if feed_item['data']['is_self']:
            log.info('{} item is a self-post'.format(feed_item['data']['id']))
            continue
        if feed_item['data']['locked']:
            log.info('{} item is locked'.format(feed_item['data']['id']))
            continue
        if feed_item['data']['score'] < 10:
            log.info('{} item does not meet the necessary criteria'.format(
                feed_item['data']['id']))
            # Temporary disable for testing
            # continue
            pass
        if feed_item['data']['domain'] not in AUTHORIZED_DOMAINS:
            log.info('{} item is on an unsupported domain'.format(
                feed_item['data']['id']))
            continue

        cross_posts.append({
            'title': feed_item['data']['title'],
            'reddit': long_link.format(feed_item['data']['permalink']),
            'media': feed_item['data']['url'],
        })

    return cross_posts


@app.task(bind=True, ignore_result=True)
def test_system(self):
    log.info('starting task')
    time.sleep(10)
    log.info('done with task')
