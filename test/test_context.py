import pytest  # noqa

from .generators import (
    generate_comment,
    generate_submission,
)

from tor_worker.context import (
    is_code_of_conduct,
    is_claimed_post_response,
    is_claimable_post,
)

import unittest


class IsCodeOfConductTest(unittest.TestCase):

    def setUp(self):
        self.comment = generate_comment(author='transcribersofreddit')

    def test_good_messages(self):
        self.comment.submission = generate_submission(flair='Unclaimed')
        self.comment.body = 'Hi there! Please read and accept our Code of ' \
            'Conduct so that we can get you started with transcribing. ' \
            'Please read the Code of Conduct below, then respond to this ' \
            'comment with `I accept`.\n\nAfter you respond, I\'ll process ' \
            'your claim as normal.\n\n---\n\n'
        assert is_code_of_conduct(self.comment)

    def test_bad_messages(self):
        self.comment.submission = generate_submission(flair='Unclaimed')
        self.comment.body = 'This post is still unclaimed! Please claim it ' \
            'first or message the mods to take care of this.'
        assert not is_code_of_conduct(self.comment)

        self.comment.submission = generate_submission(flair='Completed!')
        self.comment.body = 'Awesome, thanks for your help! I\'ll update ' \
            'your flair to reflect your new count.'
        assert not is_code_of_conduct(self.comment)

        self.comment.submission = generate_submission(flair='In Progress')
        self.comment.body = 'The post is yours! Best of luck and thanks ' \
            'for helping!\n\nPlease respond with "done" when complete so we ' \
            'can check this one off the list!'
        assert not is_code_of_conduct(self.comment)

        self.comment.submission = generate_submission(flair='In Progress')
        self.comment.body = 'I\'m sorry, but it looks like someone else has ' \
            'already claimed this post! You can check in with them to see if ' \
            'they need any help, but otherwise I suggest sticking around to ' \
            'see if another post pops up here in a little bit.'
        assert not is_code_of_conduct(self.comment)

        self.comment.submission = generate_submission(flair='Completed!')
        self.comment.body = 'This post has already been completed! Perhaps ' \
            'you can find a new one on the front page?'
        assert not is_code_of_conduct(self.comment)


class IsUnclaimedTest(unittest.TestCase):
    def setUp(self):
        self.comment = generate_comment(author='transcribersofreddit')

    def test_good_messages(self):
        self.comment.submission = generate_submission(flair='Unclaimed')
        self.comment.body = 'This post is still unclaimed! Please claim ' \
            'it first or message the mods to take care of this.'
        assert is_claimable_post(self.comment)

    def test_bad_messages(self):
        self.comment.submission = generate_submission(flair='In Progress')
        self.comment.body = 'The post is yours! Best of luck and thanks for ' \
            'helping!\n\nPlease respond with "done" when complete so we can ' \
            'check this one off the list!'
        assert not is_claimable_post(self.comment)

        self.comment.submission = generate_submission(flair='Completed!')
        self.comment.body = 'This post has already been completed! Perhaps ' \
            'you can find a new one on the front page?'
        assert not is_claimable_post(self.comment)

        self.comment.submission = generate_submission(flair='In Progress')
        self.comment.body = 'I\'m sorry, but it looks like someone else has ' \
            'already claimed this post! You can check in with them to see if ' \
            'they need any help, but otherwise I suggest sticking around to ' \
            'see if another post pops up here in a little bit.'
        assert not is_claimable_post(self.comment)

        self.comment.submission = generate_submission(flair='Completed!')
        self.comment.body = 'Awesome, thanks for your help! I\'ll update ' \
            'your flair to reflect your new count.'
        assert not is_claimable_post(self.comment)

        self.comment.submission = generate_submission(flair='Unclaimed')
        self.comment.body = 'Hi there! Please read and accept our Code of ' \
            'Conduct so that we can get you started with transcribing. ' \
            'Please read the Code of Conduct below, then respond to this ' \
            'comment with `I accept`.\n\nAfter you respond, I\'ll process ' \
            'your claim as normal.\n\n---\n\n'
        assert not is_claimable_post(self.comment)


class IsClaimedTest(unittest.TestCase):
    def setUp(self):
        self.comment = generate_comment(author='transcribersofreddit')

    def test_good_messages(self):
        self.comment.submission = generate_submission(flair='In Progress')
        self.comment.body = 'The post is yours! Best of luck and thanks for ' \
            'helping!\n\nPlease respond with "done" when complete so we can ' \
            'check this one off the list!'
        assert is_claimed_post_response(self.comment)

        self.comment.submission = generate_submission(flair='In Progress')
        self.comment.body = 'I\'m sorry, but it looks like someone else has ' \
            'already claimed this post! You can check in with them to see ' \
            'if they need any help, but otherwise I suggest sticking around ' \
            'to see if another post pops up here in a little bit.'
        assert is_claimed_post_response(self.comment)

    def test_bad_messages(self):
        self.comment.submission = generate_submission(flair='Completed!')
        self.comment.body = 'Awesome, thanks for your help! I\'ll update ' \
            'your flair to reflect your new count.'
        assert not is_claimed_post_response(self.comment)

        self.comment.submission = generate_submission(flair='Unclaimed')
        self.comment.body = 'This post is still unclaimed! Please claim it ' \
            'first or message the mods to take care of this.'
        assert not is_claimed_post_response(self.comment)

        self.comment.submission = generate_submission(flair='Unclaimed')
        self.comment.body = 'Hi there! Please read and accept our Code of ' \
            'Conduct so that we can get you started with transcribing. ' \
            'Please read the Code of Conduct below, then respond to this ' \
            'comment with `I accept`.\n\nAfter you respond, I\'ll process ' \
            'your claim as normal.\n\n---\n\n'
        assert not is_claimed_post_response(self.comment)

        self.comment.submission = generate_submission(flair='Completed!')
        self.comment.body = 'This post has already been completed! Perhaps ' \
            'you can find a new one on the front page?'
        assert not is_claimed_post_response(self.comment)
