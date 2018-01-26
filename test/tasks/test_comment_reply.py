import pytest  # noqa

from tor_worker.tasks.anyone import process_comment

import unittest
from unittest.mock import patch, Mock

from praw.models import Comment, Submission


class ProcessConductCommentTest(unittest.TestCase):
    """
    Given that the parent comment is about the code of conduct...
    """

    def setUp(self):
        # self.submission = Submission(None, _data={'id': 'xyzpdq'})
        # self.submission._comments = []
        # self.submission.link_flair_text = 'Unclaimed'
        self.comment = Comment(None, id='abcdef')
        self.comment.author = 'me'
        self.comment.body = 'I accept. I volunteer as tribute!'
        self.comment.parent = Comment(None, id='123456')
        self.comment.parent.author = 'transcribersofreddit'
        self.comment.parent.body = 'You have to sign the code of conduct ' \
            'before you can claim anything, you dunce.'
        # self.submission._comments.append(self.comment)

    @patch('tor_worker.tasks.anyone.process_comment.reddit')
    def test_agree(self, mock_reddit):
        self.comment.body = 'I accept. I volunteer as tribute!'
        mock_reddit.comment = Mock(name='comment', return_value=self.comment)
        process_comment('abcdef')

        # TODO: more to come when actual functionality is built-out

    @patch('tor_worker.tasks.anyone.process_comment.reddit')
    def test_disagree(self, mock_reddit):
        self.comment.body = 'Nah, go screw yourself.'
        mock_reddit.comment = Mock(name='comment', return_value=self.comment)
        process_comment('abcdef')

        # TODO: more to come when actual functionality is built-out


class ProcessClaimableCommentTest(unittest.TestCase):
    """
    Given that the parent comment indicates the post is unclaimed...
    """

    def setUp(self):
        self.comment = Comment(None, id='abcdef')
        self.comment.author = 'me'
        self.comment.body = 'I claim it! I volunteer as tribute!'
        self.comment.parent = Comment(None, id='123456')
        self.comment.parent.author = 'transcribersofreddit'
        self.comment.parent.body = 'This post is unclaimed.'

    @patch('tor_worker.tasks.anyone.process_comment.reddit')
    def test_claim(self, mock_reddit):
        self.comment.body = 'I claim this land in the name of France!'
        mock_reddit.comment = Mock(name='comment', return_value=self.comment)
        process_comment('abcdef')

        # TODO: more to come when actual functionality is built-out

    @patch('tor_worker.tasks.anyone.process_comment.reddit')
    def test_refuse(self, mock_reddit):
        self.comment.body = 'Nah, I can do it later'
        mock_reddit.comment = Mock(name='comment', return_value=self.comment)
        process_comment('abcdef')

        # TODO: more to come when actual functionality is built-out
