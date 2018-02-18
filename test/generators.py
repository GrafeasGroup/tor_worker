import base64
import random
import uuid

from unittest.mock import MagicMock

import loremipsum
import praw.models


class RedditGenerator(object):
    """
    A curry-able class for mixing in Reddit model generators
    """

    def generate_id(self):
        """
        Generates a random, reddit-compliant id. Note that it is picked at
        random and might collide with other real or generated reddit ids.
        """
        out = base64.b32encode(uuid.uuid4().bytes).decode().replace('=', '')
        return ''.join(random.choices(out, k=6)).lower()

    def generate_subreddit(self, name='subreddit', submission=None):
        sub = MagicMock(name=name, spec=praw.models.Subreddit)
        sub.kind = 't5'
        sub.id = self.generate_id()

        def submit_post(title, selftext=None, url=None, flair_id=None,
                        flair_text=None, resubmit=True, send_replies=True):
            out = submission if submission else self.generate_submission()
            out.title = title

            return out

        sub.submit.side_effect = submit_post

        return sub

    def generate_submission(self, name='post', author=None, reply=None):
        """
        Factory for creating a new Submission mock object.

        ''
        """
        sub = MagicMock(name=name, spec=praw.models.Submission)
        sub.kind = 't3'
        if not author:
            author = self.generate_redditor()
        sub.author = author
        sub.id = self.generate_id()
        sub.shortlink = f'http://redd.it/{sub.id}'
        sub.link_flair_text = 'Unclaimed'
        sub.title = ' '.join(random.choices(
            loremipsum.Generator().words,
            k=random.choice(range(1, 5))
        ))

        def make_comment(body):
            out = reply if reply else self.generate_comment(submission=sub)
            out.parent.return_value = sub
            out.submission = sub
            out.body = body

            return out

        def flair_choices(*args, **kwargs):
            template = {
                'flair_text': 'Foo',
                'flair_template_id': '680f43b8-1fec-11e3-80d1-12313b0b80bc',
                'flair_css_class': '',
                'flair_text_editable': False,
                'flair_position': 'left',
            }
            return [
                {**template,
                 **{'flair_text': 'Unclaimed',
                    'flair_template_id': '1'},
                 },
                {**template,
                 **{'flair_text': 'In Progress',
                    'flair_template_id': '2'},
                 },
                {**template,
                 **{'flair_text': 'Completed',
                    'flair_template_id': '3'},
                 },
                {**template,
                 **{'flair_text': 'Meta',
                    'flair_template_id': '4'},
                 },
            ]

        sub.reply.side_effect = make_comment
        sub.mark_read = MagicMock(side_effect=None)

        sub.flair = MagicMock(
            spec=praw.models.reddit.submission.SubmissionFlair
        )
        sub.flair.choices.side_effect = flair_choices
        sub.flair.select.return_value = None

        return sub

    def generate_comment(self, name='comment', submission=None, reply=None,
                         parent=None):
        comment = MagicMock(name=name, spec=praw.models.Comment)
        comment.kind = 't1'
        comment.author = self.generate_redditor()
        comment.subject = ''
        if not submission:
            submission = self.generate_submission()
        comment.submission = submission
        comment.id = self.generate_id()
        comment.body = ''
        if not parent:
            parent = submission
        comment.parent = MagicMock(return_value=parent)

        def make_comment(body):
            out = reply if reply else \
                self.generate_comment(name='reply',
                                      submission=submission,
                                      parent=comment)
            out.body = body
            out.parent = MagicMock(return_value=comment)
            return out

        comment.reply = MagicMock(side_effect=lambda s: make_comment(s))

        comment.mark_as_read = MagicMock(side_effect=None, return_value=None)

        return comment

    def generate_redditor(self):
        redditor = MagicMock(spec=praw.models.Redditor)
        redditor.name = 'me'
        # redditor.id = 'autr'
        return redditor

    def generate_hail(self, name='hail'):
        # Yep, this is an alias
        return self.generate_comment(name=name)

    def generate_mod_message(self, name='mod_message'):
        msg = MagicMock(name=name, spec=praw.models.Message)
        msg.kind = 't4'
        msg.author = None
        msg.subject = ''
        msg.body = ''
        msg.id = self.generate_id()

        msg.mark_as_read = MagicMock(side_effect=None, return_value=None)

        return msg

    def generate_message(self, name='message'):
        msg = MagicMock(name=name, spec=praw.models.Message)
        msg.kind = 't4'
        msg.author = self.generate_redditor()
        msg.subject = ''
        msg.body = ''
        msg.id = self.generate_id()

        msg.mark_as_read = MagicMock(side_effect=None, return_value=None)
        msg.reply = MagicMock(side_effect=None, return_value=None)

        return msg

    def generate_inbox(self, name='reddit.inbox', seed_data=False):
        box = MagicMock(name=name, spec=praw.models.Inbox)

        if seed_data:
            msgs = [
                self.generate_comment(),
                self.generate_hail(),
                self.generate_message(),
                self.generate_mod_message(),
            ]
            random.shuffle(msgs)
        else:
            msgs = []

        box.unread = MagicMock(side_effect=None, return_value=msgs)

        return box
