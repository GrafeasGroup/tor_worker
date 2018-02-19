import pytest  # noqa

from tor_worker.tasks.moderator import post_to_tor
from tor_worker.user_interaction import (
    post_comment,
    format_bot_response as _,
)
from tor_worker import __version__

from ..generators import (
    generate_comment,
    generate_submission,
    generate_subreddit,
)

import loremipsum
import unittest
from unittest.mock import patch, ANY


class PostToTorTaskTest(unittest.TestCase):

    @patch('tor_worker.tasks.moderator.update_post_flair.delay',
           side_effect=None)
    @patch('tor_worker.tasks.moderator.post_comment',
           side_effect=None)
    @patch('tor_worker.tasks.moderator.Config')
    @patch('tor_worker.tasks.moderator.post_to_tor.reddit')
    @patch('tor_worker.tasks.moderator.post_to_tor.redis')
    def test_new_post(self, mock_redis, mock_reddit, mock_config,
                      mock_post_comment, mock_update_flair):
        comment = generate_comment()
        post = generate_submission(reply=comment)
        sub = generate_subreddit(submission=post)
        mock_reddit.subreddit.return_value = sub
        mock_config.templates.url_type.return_value = 'other'
        mock_config.subreddit.return_value = mock_config

        def stub_post_comment(repliable, body):
            comment.body = _(body)
            return comment

        mock_post_comment.side_effect = stub_post_comment

        reddit_link = 'https://www.reddit.com/r/todayilearned/comments/' \
            '7y9tcj/til_that_when_a_man_had_a_heart_attack_at_a/'

        post_to_tor('subreddit', 'title goes here', reddit_link, 'example.com')

        mock_redis.sadd.assert_any_call('complete_post_ids', ANY)
        mock_redis.incr.assert_any_call('total_posted', amount=1)
        mock_redis.incr.assert_any_call('total_new', amount=1)

        sub.submit.assert_called_once()
        mock_post_comment.assert_called_once()
        mock_update_flair.assert_called_once()

        assert f'subreddit | Other | "title goes here"' == post.title
        assert __version__ in comment.body.lower()

    def test_post_comment_pagination(self):
        comment = generate_comment()
        post = generate_submission(reply=comment)

        # Tons of text that needs paginating
        body = '\n\n'.join(
            [' '.join(loremipsum.get_sentences(20)) for _ in range(50)]
        )
        # Also mock up having a _really_ long line
        body += '\n\n'
        body += ' '.join(loremipsum.get_sentences(1000))

        # TADA!! The main event:
        last_comment = post_comment(repliable=post, body=body)

        # Make sure we replied to the previous comment instead of having them
        # all reply as top-level comments
        comment.reply.assert_called_once()
        post.reply.assert_called_once()

        assert last_comment.kind == 't1', 'Return type is not Comment'

        # Find depth of comments
        ptr = last_comment
        num_comments = 0
        for i in range(100):
            num_comments = i

            if ptr.kind != 't1':
                break
            else:
                ptr = ptr.parent()

        assert num_comments > 1, "Comments did not need to be paginated"
