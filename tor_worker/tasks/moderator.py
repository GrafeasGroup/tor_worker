from tor_worker import OUR_BOTS
from tor_worker.user_interaction import (
    format_bot_response as _,
    responses as bot_msg,
)
from tor_worker.tasks.base import Task
from tor_worker.tasks.anyone import (
    process_comment,
    send_to_slack,
)

from celery import current_app as app
from praw.models import (
    Message,
    Comment,
    Submission,
)


@app.task(bind=True, base=Task)
def check_inbox(self):
    """
    Checks all unread messages in the inbox, routing the responses to other
    queues. This effectively transfers tasks from Reddit's inbox to our internal
    task queuing system, reducing the required API calls.
    """
    for item in reversed(list(self.reddit.inbox.unread(limit=None))):
        if isinstance(item, Comment):
            if 'username mention' in item.subject.lower():
                send_bot_message.delay(to=item.author.name,
                                       subject='Username Call',
                                       body=_(bot_msg['mentioned']))

            else:
                process_comment.delay(item.id)

        elif isinstance(item, Message):
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

            else:
                process_message.delay(item.id)

        elif isinstance(item, Submission):
            # TODO: Handle submissions?
            if item.author not in OUR_BOTS:
                # TODO: Flair post as [META]
                pass

        else:
            # TODO: Are there any other types?
            pass

        item.mark_read()


@app.task(bind=True, base=Task)
def process_message(self, message_id):
    """
    WORK IN PROGRESS::
    """
    msg = self.reddit.message(message_id)

    if msg.subject[0] == '!':
        # TODO: Process admin command
        pass
    # TODO


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
    if message_id:
        self.reddit.message(message_id).reply(body)
    elif to:
        self.reddit.redditor(to).message(subject, body)
    else:
        raise NotImplementedError(
            "Must give either a value for ``message_id`` or ``to``"
        )
