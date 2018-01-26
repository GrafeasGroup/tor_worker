import pytest

from unittest.mock import MagicMock

from praw.models import Comment


def comment_faker(id):
    c = Comment(None, id=id)
    c.author = 'transcribersofreddit'
    c.body = 'lorem ipsum'

    return c


@pytest.fixture
def reddit():
    import praw
    reddit = MagicMock(spec=praw.Reddit)
    reddit.comment = \
        MagicMock(name='comment', side_effect=comment_faker)

    return reddit
