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
                                       body=_(bot_msg['mentioned']))

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

            elif item.subject[0] == '!':
                # TODO: Process admin command
                process_admin_command.delay(item.id)
                pass
            else:
                send_to_slack.delay(
                    f'Unhandled message by '
                    f'<https://reddit.com/user/{item.author.name}|'
                    f'u/{item.author.name}> -- '
                    f'*{item.subject}*:\n{item.body}'
                    '#general'
                )

        elif item.kind == 't3':  # Submission
            # TODO: Handle submissions?
            if item.author not in OUR_BOTS:
                # TODO: Flair post as [META]
                pass

        else:  # Other types (???)
            # TODO: Log the ``item`` that reached here for later analysis
            pass

        item.mark_read()


@app.task(bind=True, base=Task)
def process_admin_command(self, message_id):
    """
    WORK IN PROGRESS::
    """
    msg = self.reddit.message(message_id)

    # TODO
    msg


@app.task(bind=True, base=Task)
def update_post_flair(self, submission_id, flair):
    """
    WORK IN PROGRESS::
    """
    post = self.reddit.submission(submission_id)

    for choice in post.flair.choices():
        if choice['flair_text'] == flair:
            post.flair.select(
                flair_template_id=choice['flair_template_id']
            )
            return

    # TODO: alert the authorities that something has gone terribly wrong


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
