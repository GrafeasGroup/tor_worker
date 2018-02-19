from tor_worker import OUR_BOTS
from tor_worker.config import Config
from tor_worker.context import (
    is_claimable_post,
    is_claimed_post_response,
    is_code_of_conduct,
)
from tor_worker.user_interaction import (
    format_bot_response as _,
    message_link,
    responses as bot_msg,
    post_comment,
)
from tor_worker.tasks.base import Task, InvalidUser
from tor_worker.tasks.anyone import send_to_slack

from celery.utils.log import get_task_logger
from celery import current_app as app
from praw.models import Comment

import re
import textwrap


log = get_task_logger(__name__)


MOD_SUPPORT_PHRASES = [
    re.compile('fuck', re.IGNORECASE),
    re.compile('unclaim', re.IGNORECASE),
    re.compile('undo', re.IGNORECASE),
    re.compile('(?:good|bad) bot', re.IGNORECASE),
]


@app.task(bind=True, ignore_result=True, base=Task)
def check_inbox(self):
    """
    Checks all unread messages in the inbox, routing the responses to other
    queues. This effectively transfers tasks from Reddit's inbox to our internal
    task queuing system, reducing the required API calls.
    """
    for item in reversed(list(self.reddit.inbox.unread(limit=None))):

        # NOTE: We compare the `kind` attribute due to testing issues with
        #   `isinstance()`. We can mock out the objects with MagicMock now and
        #   have fewer classes loaded in this context.

        if item.kind == 't1':  # Comment
            if 'username mention' in item.subject.lower():
                log.info(f'Username mention by /u/{item.author.name}')
                send_bot_message.delay(to=item.author.name,
                                       subject='Username Call',
                                       body=_(bot_msg['mention']))

            else:
                process_comment.delay(item.id)

        elif item.kind == 't4':  # Message
            # Very rarely we may actually get a message from Reddit admins, in
            # which case there will be no author attribute
            if item.author is None:
                log.info(f'Received message from the admins: {item.subject}')
                send_to_slack.delay(
                    f'*Incoming message without an author*\n\n'
                    f'*Subject:* {item.subject}\n'
                    f'*Body:*\n\n'
                    f'{item.body}',
                    '#general'
                )

            elif item.subject and item.subject[0] == '!':
                process_admin_command.delay(author=item.author.name,
                                            subject=item.subject,
                                            body=item.body,
                                            message_id=item.id)
            else:
                log.info(f'Received unhandled message from '
                         f'/u/{item.author.name}. Subject: '
                         f'{repr(item.subject)}')
                send_to_slack.delay(
                    f'Unhandled message by [/u/{item.author.name}]'
                    f'(https://reddit.com/user/{item.author.name})'
                    f'\n\n'
                    f'*Subject:* {item.subject}'
                    f'\n\n'
                    f'{item.body}'
                    '#general'
                )

        else:  # pragma: no cover

            # There shouldn't be any other types than Message and Comment,
            # but on the off-chance there is, we'll log what it is here.
            send_to_slack.delay(
                f'Unhandled, unknown inbox item: {type(item).__name__}',
                '#botstuffs'
            )
            log.warning(f'Unhandled, unknown inbox item: {type(item).__name__}')

        item.mark_read()


@app.task(bind=True, ignore_result=True, base=Task)
def process_admin_command(self, author, subject, body, message_id):
    """
    WORK IN PROGRESS
    """
    # TODO
    raise NotImplementedError()


@app.task(bind=True, ignore_result=True, base=Task)
def update_post_flair(self, submission_id, flair):
    """
    Updates the flair of the original post to the pre-existing flair template id
    given the string value of the flair. If there is no pre-existing styling for
    that flair choice, task will error out with ``NotImplementedError``.

    EXAMPLE:
        ``flair`` is "unclaimed", sets the post to "Unclaimed" with pre-existing
        styling
    """
    post = self.reddit.submission(submission_id)

    for choice in post.flair.choices():
        if choice['flair_text'].lower() == flair.lower():
            # NOTE: This is hacky if we have multiple styles for the same flair.
            #   That said, we shouldn't rely on visual style if we're being
            #   truly accessible...
            post.flair.select(
                flair_template_id=choice['flair_template_id']
            )
            return

    raise NotImplementedError(f"Unknown flair, {repr(flair)}, for post")


@app.task(bind=True, ignore_result=True, base=Task)
def send_bot_message(self, body, message_id=None, to=None,
                     subject='Just bot things...'):
    """
    Sends a message as /u/TranscribersOfReddit

    If this is intended to be a reply to an existing message:
    - fill out the ``message_id`` param with a ref to the previous message

    If no previous context:
    - fill out the ``to`` param with the author's username
    - fill out the ``subject`` param with the subject of the message

    One of these _must_ be done.
    """
    sender = self.reddit.user.me().name
    if sender != 'transcribersofreddit':
        raise InvalidUser(f'Attempting to send message as {sender}'
                          f'instead of the official ToR bot')

    if message_id:
        self.reddit.message(message_id).reply(body)
    elif to:
        self.reddit.redditor(to).message(subject, body)
    else:
        raise NotImplementedError(
            "Must give either a value for ``message_id`` or ``to``"
        )


def process_mod_intervention(comment: Comment):
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
def process_comment(self, comment_id):
    """
    Processes a notification of comment being made, routing to other tasks as
    is deemed necessary
    """
    reply = self.reddit.comment(comment_id)

    if reply.author.name in OUR_BOTS:
        return

    body = reply.body.lower()

    # This should just be a filter that doesn't stop further processing
    process_mod_intervention(reply)

    if is_code_of_conduct(reply.parent()):
        if re.search(r'\bi accept\b', body):  # pragma: no coverage
            # TODO: Fill out coc accept scenario and remove pragma directive
            pass
        else:  # pragma: no coverage
            # TODO: Fill out error scenario and remove pragma directive
            pass

    elif is_claimed_post_response(reply.parent()):
        if re.search(r'\b(?:done|deno)\b', body):  # pragma: no coverage
            # TODO: Fill out done scenario and remove pragma directive
            pass
        elif re.search(r'(?=<^|\W)!override\b', body):  # pragma: no coverage
            # TODO: Fill out override scenario and remove pragma directive
            pass
        else:  # pragma: no coverage
            # TODO: Fill out error scenario and remove pragma directive
            pass

    elif is_claimable_post(reply.parent()):
        if re.search(r'\bclaim\b', body):  # pragma: no coverage
            # TODO: Fill out claim scenario and remove pragma directive
            pass
        else:  # pragma: no coverage
            # TODO: Fill out error scenario and remove pragma directive
            pass


@app.task(bind=True, ignore_result=True, base=Task)
def post_to_tor(self, sub, title, link, domain):
    config = Config.subreddit(sub)
    title = textwrap.shorten(title, width=250, placeholder='...')

    post_type = config.templates.url_type(domain)
    post_template = config.templates.content(domain)
    footer = config.templates.footer

    submission = self.reddit.subreddit('TranscribersOfReddit').submit(
        title=f'{sub} | {post_type.title()} | "{title}"',
        url=link,
    )

    update_post_flair.delay(submission.id, 'Unclaimed')

    # Add completed post to tracker
    self.redis.sadd('complete_post_ids', submission.id)
    self.redis.incr('total_posted', amount=1)
    self.redis.incr('total_new', amount=1)

    # TODO: OCR job for this comment

    reply = bot_msg['intro_comment'].format(
        post_type=post_type,
        formatting=post_template,
        footer=footer,
        message_url=message_link(subject='General Questions'),
    )

    post_comment(repliable=submission, body=reply)

    return reply
