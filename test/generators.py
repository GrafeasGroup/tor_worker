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
