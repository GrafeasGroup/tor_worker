import pytest  # noqa

from tor_worker.tasks.moderator import update_post_flair

from ..generators import RedditGenerator

import unittest
from unittest.mock import patch, MagicMock


class UpdatePostFlairTest(unittest.TestCase, RedditGenerator):

    @patch('tor_worker.tasks.moderator.update_post_flair.reddit')
    def test_available_flair(self, mock_reddit):
        post = self.generate_submission()
        mock_reddit.submission = MagicMock(return_value=post)

        update_post_flair(submission_id='abc123', flair='Unclaimed')

        mock_reddit.submission.assert_called_once()
        post.flair.choices.assert_called_once_with()
        post.flair.select.assert_called_once()

    @patch('tor_worker.tasks.moderator.update_post_flair.reddit')
    def test_unavailable_flair(self, mock_reddit):
        post = self.generate_submission()
        mock_reddit.submission = MagicMock(return_value=post)

        with pytest.raises(NotImplementedError):
            update_post_flair(submission_id='abc123', flair='foo')

        mock_reddit.submission.assert_called_once()
        post.flair.choices.assert_called_once_with()
        post.flair.select.assert_not_called()
