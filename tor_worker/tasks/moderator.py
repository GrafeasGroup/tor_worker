from tor_worker.config import Config
from tor_worker.user_interaction import (
    format_bot_response as _,
    responses as bot_msg,
)
from tor_worker.tasks.base import Task, InvalidUser
from tor_worker.tasks.anyone import (
    process_comment,
    send_to_slack,
)

from celery import current_app as app


@app.task(bind=True, base=Task)
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
                send_bot_message.delay(to=item.author.name,
                                       subject='Username Call',
                                       body=_(bot_msg['mention']))

            else:
                process_comment.delay(item.id)

        elif item.kind == 't4':  # Message
            # Very rarely we may actually get a message from Reddit admins, in
            # which case there will be no author attribute
            if item.author is None:
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
                                            body=item.body)
            else:
                send_to_slack.delay(
                    f'Unhandled message by '
                    f'<https://reddit.com/user/{item.author.name}|'
                    f'u/{item.author.name}> -- '
                    f'*{item.subject}*:\n{item.body}'
                    '#general'
                )

        else:  # pragma: no cover
            # There shouldn't be any other types than Message and Comment,
            # but on the off-chance there is, we'll log what it is here.
            send_to_slack.delay(
                f'Unhandled, unknown inbox item: {type(item).__name__}',
                '#botstuffs'
            )

        item.mark_read()


@app.task(bind=True, base=Task)
def process_admin_command(self, author, subject, body):
    """
    WORK IN PROGRESS
    """
    raise NotImplementedError()


@app.task(bind=True, base=Task)
def update_post_flair(self, submission_id, flair):
    post = self.reddit.submission(submission_id)

    for choice in post.flair.choices():
        if choice['flair_text'].lower() == flair.lower():
            post.flair.select(
                flair_template_id=choice['flair_template_id']
            )
            return

    raise NotImplementedError(f"Unknown flair, {repr(flair)}, for post")


@app.task(bind=True, base=Task)
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


@app.task(bind=True, base=Task)
def post_to_tor(self, sub, title, link, domain):
    config = Config.subreddit(sub)
    max_title_length = 250
    if len(title) > max_title_length:
        title = title[:(max_title_length - 3)] + '...'

    post_type = config.templates.url_type(domain)
    post_template = config.templates.content(domain)

    submission = self.reddit.subreddit('TranscribersOfReddit').submit(
        title=f'{sub} | {post_type.title()} | "{title}"',
    )
    update_post_flair.delay(submission.id, 'Unclaimed')

    self.redis.incr()


@app.task(bind=True, base=Task)
def intro_bot_comment(self, submission_id, post_type, template):
    pass
