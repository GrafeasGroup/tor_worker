import random

from unittest.mock import MagicMock

import praw.models


class RedditGenerator(object):
    """
    A curry-able class for mixing in Reddit model generators
    """

    def generate_submission(self, name='post'):
        sub = MagicMock(name=name, spec=praw.models.Submission)
        sub.kind = 't3'
        sub.author = self.generate_redditor()
        sub.id = 'post'
        sub.shortlink = f'http://redd.it/abc123{sub.id}'
        sub.link_flair_text = 'Unclaimed'

        sub.mark_read = MagicMock(side_effect=None, return_value=None)

        sub.flair = MagicMock(
            spec=praw.models.reddit.submission.SubmissionFlair
        )

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
        sub.flair.choices = MagicMock(side_effect=flair_choices)
        sub.flair.select = MagicMock(return_values=None)

        return sub

    def generate_comment(self, name='comment'):
        comment = MagicMock(name=name, spec=praw.models.Comment)
        comment.kind = 't1'
        comment.author = self.generate_redditor()
        comment.subject = ''
        comment.submission = self.generate_submission()
        comment.id = 'cmnt'

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
        msg.id = 'modm'

        msg.mark_as_read = MagicMock(side_effect=None, return_value=None)

        return msg

    def generate_message(self, name='message'):
        msg = MagicMock(name=name, spec=praw.models.Message)
        msg.kind = 't4'
        msg.author = self.generate_redditor()
        msg.subject = ''
        msg.body = ''
        msg.id = 'mssg'

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
