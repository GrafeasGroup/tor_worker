import pytest  # noqa

from praw.models import Comment

from tor_worker.context import *

"""
Tests for tor_worker.context.*
"""


def test_context_code_of_conduct():
    author = 'transcribersofreddit'

    good_messages = [
        'Hi there! Please read and accept our Code of Conduct so that we can get you started with transcribing. Please read the Code of Conduct below, then respond to this comment with `I accept`.\n\nAfter you respond, I\'ll process your claim as normal.\n\n---\n\n',  # noqa
    ]

    bad_messages = [
        'This post is still unclaimed! Please claim it first or message the mods to take care of this.',  # noqa
        'Awesome, thanks for your help! I\'ll update your flair to reflect your new count.',  # noqa
        'The post is yours! Best of luck and thanks for helping!\n\nPlease respond with "done" when complete so we can check this one off the list!',  # noqa
        'I\'m sorry, but it looks like someone else has already claimed this post! You can check in with them to see if they need any help, but otherwise I suggest sticking around to see if another post pops up here in a little bit.',  # noqa
        'This post has already been completed! Perhaps you can find a new one on the front page?',  # noqa
    ]

    for m in good_messages:
        c = Comment(None, id='abc123')
        c.body = m
        c.author = author

        assert is_code_of_conduct(c), \
            f'Didn\'t think "{m[0:20]}[...]" should be a CoC comment'

    for m in bad_messages:
        c = Comment(None, id='abc123')
        c.body = m
        c.author = author

        assert not is_code_of_conduct(c), \
            f'Thought "{m[0:20]}[...]" should be a CoC comment'


def test_context_unclaimed():
    author = 'transcribersofreddit'

    good_messages = [
        'This post is still unclaimed! Please claim it first or message the mods to take care of this.',  # noqa
    ]

    bad_messages = [
        'Hi there! Please read and accept our Code of Conduct so that we can get you started with transcribing. Please read the Code of Conduct below, then respond to this comment with `I accept`.\n\nAfter you respond, I\'ll process your claim as normal.\n\n---\n\n',  # noqa
        'Awesome, thanks for your help! I\'ll update your flair to reflect your new count.',  # noqa
        'The post is yours! Best of luck and thanks for helping!\n\nPlease respond with "done" when complete so we can check this one off the list!',  # noqa
        'I\'m sorry, but it looks like someone else has already claimed this post! You can check in with them to see if they need any help, but otherwise I suggest sticking around to see if another post pops up here in a little bit.',  # noqa
        'This post has already been completed! Perhaps you can find a new one on the front page?',  # noqa
    ]

    for m in good_messages:
        c = Comment(None, id='abc123')
        c.body = m
        c.author = author

        assert is_claimable_post(c), \
            f'Didn\'t think "{m[0:20]}[...]" should be an unclaimed comment'

    for m in bad_messages:
        c = Comment(None, id='abc123')
        c.body = m
        c.author = author

        assert not is_claimable_post(c), \
            f'Thought "{m[0:20]}[...]" should be an unclaimed comment'


def test_context_claimed():
    author = 'transcribersofreddit'

    good_messages = [
        'The post is yours! Best of luck and thanks for helping!\n\nPlease respond with "done" when complete so we can check this one off the list!',  # noqa
        'I\'m sorry, but it looks like someone else has already claimed this post! You can check in with them to see if they need any help, but otherwise I suggest sticking around to see if another post pops up here in a little bit.',  # noqa
    ]

    bad_messages = [
        'This post is still unclaimed! Please claim it first or message the mods to take care of this.',  # noqa
        'Hi there! Please read and accept our Code of Conduct so that we can get you started with transcribing. Please read the Code of Conduct below, then respond to this comment with `I accept`.\n\nAfter you respond, I\'ll process your claim as normal.\n\n---\n\n',  # noqa
        'Awesome, thanks for your help! I\'ll update your flair to reflect your new count.',  # noqa
        'This post has already been completed! Perhaps you can find a new one on the front page?',  # noqa
    ]

    for m in good_messages:
        c = Comment(None, id='abc123')
        c.body = m
        c.author = author

        assert is_claimed_post_response(c), \
            f'Didn\'t think "{m[0:20]}[...]" should be a claimed comment'

    for m in bad_messages:
        c = Comment(None, id='abc123')
        c.body = m
        c.author = author

        assert not is_claimed_post_response(c), \
            f'Thought "{m[0:20]}[...]" should be a claimed comment'
