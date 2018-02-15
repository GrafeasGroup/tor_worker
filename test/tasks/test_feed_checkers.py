import pytest  # noqa

from tor_worker.tasks.anyone import check_new_feed

import unittest
from unittest.mock import (
    ANY,
    patch,
    MagicMock,
)


def noop_callable(*args, **kwargs):
    def noop(*args, **kwargs):
        pass

    return noop


class FeedCheckerTest(unittest.TestCase):

    def reddit_post_json(self):
        return {
            'kind': 't3',
            'data': {
                'is_self': False,
                'locked': False,
                'archived': False,
                'author': 'me',
                'id': 'asdfljj2',
                'score': 1234,
                'domain': 'imgur.com',
                'title': 'Something evil this way comes',
                'permalink': '/r/TIL/comments/asdfljj2/'
                             'something_evil_this_way_comes/',
                'url': 'https://imgur.com/gallery/246Ld',
                'subreddit': 'TIL',
            },
        }

    def reddit_json(self):
        return {
            'kind': 'listing',
            'data': {
                'children': [
                    self.reddit_post_json(),
                    self.reddit_post_json(),
                    self.reddit_post_json(),
                ]
            }
        }

    @patch('tor_worker.tasks.anyone.Config')
    @patch('tor_worker.tasks.anyone.signature')
    @patch('tor_worker.tasks.anyone.check_new_feed.http.get')
    @patch('tor_worker.tasks.anyone.check_new_feed.redis', side_effect=None)
    def test_feed_reader(self, mock_redis, mock_http_get, mock_signature,
                         mock_config):
        sig = MagicMock(name='task_signature')
        mock_signature.return_value = sig
        mock_config.subreddit = MagicMock(name='Config.subreddit',
                                          return_value=mock_config)
        mock_response = MagicMock(name='http_response')
        mock_http_get.return_value = mock_response
        mock_response.json.return_value = self.reddit_json()

        # Is the post already processed?
        mock_redis.sismember.return_value = False

        # filters
        mock_config.filters.url_allowed.return_value = True
        mock_config.filters.score_allowed.return_value = True

        check_new_feed('TIL')

        mock_signature.assert_called_with('tor_worker.tasks.post_to_tor',
                                          kwargs=ANY)
        sig.apply_async.assert_called()
