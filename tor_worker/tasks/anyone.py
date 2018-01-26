from tor_worker import OUR_BOTS
from tor_worker.context import (
    is_code_of_conduct,
    is_claimed_post_response,
    is_claimable_post,
)
from tor_worker.moderation import process_mod_intervention
from tor_worker.tasks.base import Task

from celery.utils.log import get_task_logger
from celery import current_app as app


log = get_task_logger(__name__)


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
