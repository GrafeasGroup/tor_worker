from tor_worker import OUR_BOTS
from tor_worker.context import (
    is_code_of_conduct,
    is_claimed_post_response,
    is_claimable_post,
)
from tor_worker.tasks.base import Task

import re

from celery.utils.log import get_task_logger
from celery import current_app as app
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
        if re.search(r'\bi accept\b', body):
            pass
        else:
            pass

    elif is_claimed_post_response(reply.parent):
        if re.search(r'\b(?:done|deno)\b', body):
            pass
        elif re.search(r'(?=<^|\W)!override\b', body):
            pass
        else:
            pass

    elif is_claimable_post(reply.parent):
        if re.search(r'\bclaim\b', body):
            pass
        else:
            pass


@app.task(bind=True, rate_limit='50/m', base=Task)
def check_new_feed(self, subreddit):
    r = self.http.get(f'https://www.reddit.com/r/{subreddit}/new.json')
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
            log.debug('{} item is a self-post'.format(feed_item['data']['id']))
            continue
        if feed_item['data']['locked']:
            log.debug('{} item is locked'.format(feed_item['data']['id']))
            continue
        if feed_item['data']['score'] < 10:
            log.debug('{} item does not meet the necessary criteria'.format(
                feed_item['data']['id']))
            # Temporary disable for testing
            # continue
            pass
        if feed_item['data']['domain'] not in AUTHORIZED_DOMAINS:
            log.debug('{} item is on an unsupported domain'.format(
                feed_item['data']['id']))
            continue

        # TODO: check if post is already added

        cross_posts.append({
            'title': feed_item['data']['title'],
            'reddit': long_link.format(feed_item['data']['permalink']),
            'media': feed_item['data']['url'],
        })

    log.info('Found %d posts for /r/%s' % (len(cross_posts), subreddit))
    return cross_posts


@app.task(bind=True, ignore_result=True, base=Task)
def check_new_feeds(self):
    subreddits = [
        'DnDGreentext',
        'gametales',
        'blind',
        'DescriptionPlease',
        'rpghorrorstories',
        'TheChurchOfRogers',
        'kierra',
        'BestOfReports',
        'ScottishPeopleTwitter',
        'TrashyText',
        'ihavesex',
        # ... more, but too lazy to hardcode for now

        'ProgrammerHumor',
        'me_irl',
    ]

    for sub in subreddits:
        check_new_feed.delay(sub)


@app.task(bind=True, ignore_result=True, base=Task)
def test_system(self):
    import time

    log.info('starting task')
    time.sleep(10)
    log.info('done with task')
