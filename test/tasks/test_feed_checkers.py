import pytest  # noqa

from tor_worker.tasks.anyone import check_new_feed

import unittest
from unittest.mock import patch, MagicMock


def noop_callable(*args, **kwargs):
    def noop(*args, **kwargs):
        pass

    return noop


class FeedCheckerTest(unittest.TestCase):

    def submission(self):
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

    @patch('tor_worker.tasks.anyone.log', side_effect=None)
    @patch('tor_worker.tasks.anyone.Config')
    @patch('tor_worker.tasks.anyone.signature')
    @patch('tor_worker.tasks.anyone.check_new_feed.http.get')
    @patch('tor_worker.tasks.anyone.check_new_feed.redis', side_effect=None)
    def test_feed_reader(self, mock_redis, mock_http_get, mock_signature,
                         mock_config, mock_log):
        post_to_tor = MagicMock(name='task_signature')
        mock_signature.return_value = post_to_tor
        mock_config.subreddit = MagicMock(name='Config.subreddit',
                                          return_value=mock_config)
        mock_response = MagicMock(name='http_response')
        mock_http_get.return_value = mock_response

        out = {
            'kind': 'listing',
            'data': {
                'children': [
                    self.submission(),
                    self.submission(),
                    self.submission(),
                    self.submission(),
                    self.submission(),
                    self.submission(),
                    self.submission(),
                    self.submission(),
                    # self.submission(),
                    # self.submission(),
                ]
            }
        }
        mock_response.json.return_value = out

        # Post 1234 has already been processed
        mock_redis.sismember.side_effect = \
            lambda q, i: q == 'post_ids' and i == '1234'
        # Only imgur is an allowed domain
        mock_config.filters.url_allowed.side_effect = \
            lambda u: u.startswith('imgur')
        # Minimum score threshold is 10
        mock_config.filters.score_allowed.side_effect = lambda s: s > 10

        # Any one of these are skip conditions
        out['data']['children'][0]['data']['is_self'] = True
        out['data']['children'][1]['data']['locked'] = True
        out['data']['children'][2]['data']['archived'] = True
        out['data']['children'][3]['data']['score'] = 1
        out['data']['children'][4]['data']['author'] = None
        out['data']['children'][5]['data']['domain'] = '4chan.com'
        out['data']['children'][6]['data']['id'] = '1234'

        # Is the post already processed?
        mock_redis.sismember.return_value = False

        # filters
        mock_config.filters.url_allowed.return_value = True
        mock_config.filters.score_allowed.return_value = True

        check_new_feed('TIL')

        mock_signature.assert_called_once_with(
            'tor_worker.tasks.moderator.post_to_tor')
        post_to_tor.apply_async.assert_called_once()
