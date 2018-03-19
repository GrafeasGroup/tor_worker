import pytest

from tor_worker.tasks.moderator import process_admin_command

from ..celery import (
    signature,
    reset_signatures,
    # assert_no_tasks_called,
    # assert_only_tasks_called,
)
from ..generators import (
    generate_message,
)

import unittest
from unittest.mock import patch, MagicMock


@pytest.mark.skip(reason='Not yet implemented')
class ProcessAdminCommandTest(unittest.TestCase):
    def setUp(self):
        reset_signatures()
        self.msg = generate_message()

    # @patch('tor_worker.tasks.moderator.signature', side_effect=signature)
    # def test_import_tasks(self, mock_signature):
    #     process_admin_command(subject='!ping',
    #                           author='me',
    #                           body='derp',
    #                           message_id=self.msg.id)

    @patch('tor_worker.tasks.moderator.Config')
    @patch('tor_worker.tasks.moderator.signature', side_effect=signature)
    def test_routing_blacklist(self, mock_signature, mock_config):
        mock_config.subreddit = MagicMock(name='Config.subreddit',
                                          return_value=mock_config)

        process_admin_command(subject='!blacklist',
                              author='me',
                              body='you',
                              message_id=self.msg.id)
