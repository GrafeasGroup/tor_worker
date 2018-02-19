import pytest  # noqa

from tor_worker.tasks.anyone import (
    check_new_feed,
    monitor_own_new_feed,
)

import unittest
from unittest.mock import patch, MagicMock

from ..generators import (
    generate_reddit_id,
    generate_post_feed_item,
)


def noop_callable(*args, **kwargs):
    def noop(*args, **kwargs):
        pass

    return noop


class FeedCheckerTest(unittest.TestCase):

    def submission(self, *args, **kwargs):
        return generate_post_feed_item(*args, **kwargs)

    @patch('tor_worker.tasks.anyone.Config')
    @patch('tor_worker.tasks.anyone.signature')
    @patch('tor_worker.tasks.anyone.check_new_feed.http.get')
    @patch('tor_worker.tasks.anyone.check_new_feed.redis', side_effect=None)
    def test_feed_reader(self, mock_redis, mock_http_get, mock_signature,
                         mock_config):
        post_to_tor = MagicMock(name='task_signature')
        mock_signature.return_value = post_to_tor
        mock_config.subreddit = MagicMock(name='Config.subreddit',
                                          return_value=mock_config)
        mock_response = MagicMock(name='http_response')
        mock_http_get.return_value = mock_response

        img_link = f'https://www.imgur.com/{generate_reddit_id()}'

        subreddit = 'ProgrammingHumor'

        pre_processed_id = generate_reddit_id()
        out = {
            'kind': 'listing',
            'data': {
                'children': [
                    # Skip: self-post
                    generate_post_feed_item(subreddit=subreddit,
                                            selftext='hello'),
                    # Skip: locked post
                    generate_post_feed_item(subreddit=subreddit, locked=True,
                                            link=img_link),
                    # Skip: archived post
                    generate_post_feed_item(subreddit=subreddit, archived=True,
                                            link=img_link),
                    # Skip: low scoring post
                    generate_post_feed_item(subreddit=subreddit, score=1,
                                            link=img_link),
                    # Skip: deleted post
                    generate_post_feed_item(subreddit=subreddit, author=None,
                                            link=img_link),
                    # Skip: non-whitelisted domain
                    generate_post_feed_item(subreddit=subreddit,
                                            link='https://www.4chan.com/b/'),
                    # Skip: already-processed post id
                    generate_post_feed_item(subreddit=subreddit,
                                            id=pre_processed_id, link=img_link),
                    # Good
                    generate_post_feed_item(subreddit=subreddit, link=img_link),
                ]
            }
        }
        mock_response.json.return_value = out

        mock_redis.sismember.side_effect = \
            lambda q, i: q == 'post_ids' and i == pre_processed_id
        mock_config.filters.url_allowed.side_effect = \
            lambda u: u.startswith('www.imgur.com')
        mock_config.filters.score_allowed.side_effect = lambda s: s > 10

        # Is the post already processed?
        mock_redis.sismember.return_value = False

        # filters
        mock_config.filters.url_allowed.return_value = True
        mock_config.filters.score_allowed.return_value = True

        check_new_feed(subreddit)

        mock_signature.assert_called_once_with(
            'tor_worker.tasks.moderator.post_to_tor')
        post_to_tor.apply_async.assert_called_once()

    @pytest.mark.skip(reason='broken')
    @patch('tor_worker.tasks.anyone.signature')
    @patch('tor_worker.tasks.anyone.monitor_own_new_feed.http.get')
    def test_self_monitoring_feed(self, mock_http_get, mock_signature):
        mock_update_post_flair = MagicMock(name='update_post_flair')

        def sig(name, *args, **kwargs):
            item = None
            if name == 'tor_worker.tasks.moderator.update_post_flair':
                item = mock_update_post_flair

            if not item:
                raise NotImplementedError()

            item.apply_async.side_effect = None

            return item

        mock_signature.side_effect = sig
        mock_response = MagicMock(name='http_response')
        mock_http_get.return_value = mock_response

        fake_link = f'https://www.reddit.com/r/TodayILearned/' \
            f'/comments/{generate_reddit_id()}/fizz_buzz'

        out = {
            'kind': 'listing',
            'data': {
                'children': [
                    self.submission(link=fake_link, flair=None,
                                    author='transcribersofreddit'),
                    self.submission(link=fake_link,
                                    author='transcribersofreddit'),
                    self.submission(link=fake_link, flair=None),
                    self.submission(link=fake_link),
                    self.submission(flair=None, author='transcribersofreddit'),
                    self.submission(flair=None),
                    self.submission(),
                ]
            }
        }
        mock_response.json.return_value = out

        monitor_own_new_feed()

        assert mock_update_post_flair.call_count == 2
