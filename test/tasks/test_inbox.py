import pytest  # noqa

from tor_worker.tasks.moderator import check_inbox

from ..generators import RedditGenerator

import unittest
from unittest.mock import patch


class ProcessCommentInboxMessageTest(unittest.TestCase, RedditGenerator):
    """
    """

    @pytest.mark.skip(reason='Unfinished')
    @patch('tor_worker.tasks.moderator.check_inbox.reddit')
    def test_comment(self, mock_reddit):
        mock_reddit.inbox = self.generate_inbox()

        check_inbox()
