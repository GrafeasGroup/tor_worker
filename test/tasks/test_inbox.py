import pytest  # noqa

from tor_worker.tasks.moderator import check_inbox

from ..generators import (
    generate_comment,
    generate_message,
    generate_inbox,
)

import unittest
from unittest.mock import patch


class ProcessInboxMessagesTest(unittest.TestCase):
    """
    Tests the routing of certain inbox message types
    """

    @patch('tor_worker.tasks.moderator.send_bot_message.delay',
           side_effect=None)
    @patch('tor_worker.tasks.moderator.process_admin_command.delay',
           side_effect=None)
    @patch('tor_worker.tasks.moderator.send_to_slack.delay', side_effect=None)
    @patch('tor_worker.tasks.moderator.process_comment.delay', side_effect=None)
    @patch('tor_worker.tasks.moderator.check_inbox.reddit')
    def test_comment(self, mock_reddit, mock_process_comment,
                     mock_slack, mock_admin_cmd, mock_bot_message):
        item = generate_comment()
        mock_reddit.inbox = generate_inbox()
        mock_reddit.inbox.unread.return_value = [item]

        check_inbox()

        mock_bot_message.assert_not_called()
        mock_process_comment.assert_called_once()
        mock_slack.assert_not_called()
        mock_admin_cmd.assert_not_called()

        item.mark_read.assert_called_once()

    @patch('tor_worker.tasks.moderator.send_bot_message.delay',
           side_effect=None)
    @patch('tor_worker.tasks.moderator.process_admin_command.delay',
           side_effect=None)
    @patch('tor_worker.tasks.moderator.send_to_slack.delay', side_effect=None)
    @patch('tor_worker.tasks.moderator.process_comment.delay', side_effect=None)
    @patch('tor_worker.tasks.moderator.check_inbox.reddit')
    def test_mention(self, mock_reddit, mock_process_comment,
                     mock_slack, mock_admin_cmd, mock_bot_message):
        item = generate_comment(
            subject='username mention',
            body='Just letting you know, /u/me, it\'s pretty cool.',
        )

        mock_reddit.inbox = generate_inbox()
        mock_reddit.inbox.unread.return_value = [item]

        check_inbox()

        mock_bot_message.assert_called_once()
        mock_process_comment.assert_not_called()
        mock_slack.assert_not_called()
        mock_admin_cmd.assert_not_called()

        item.mark_read.assert_called_once()

    @patch('tor_worker.tasks.moderator.send_bot_message.delay',
           side_effect=None)
    @patch('tor_worker.tasks.moderator.process_admin_command.delay',
           side_effect=None)
    @patch('tor_worker.tasks.moderator.send_to_slack.delay', side_effect=None)
    @patch('tor_worker.tasks.moderator.process_comment.delay', side_effect=None)
    @patch('tor_worker.tasks.moderator.check_inbox.reddit')
    def test_message(self, mock_reddit, mock_process_comment,
                     mock_slack, mock_admin_cmd, mock_bot_message):
        item = generate_message(
            subject='Yo! I like this subreddit',
            body='Just letting you know, it\'s pretty cool.'
        )

        mock_reddit.inbox = generate_inbox()
        mock_reddit.inbox.unread.return_value = [item]

        check_inbox()

        mock_bot_message.assert_not_called()
        mock_process_comment.assert_not_called()
        mock_slack.assert_called_once()
        mock_admin_cmd.assert_not_called()

        item.mark_read.assert_called_once()

    @patch('tor_worker.tasks.moderator.send_bot_message.delay',
           side_effect=None)
    @patch('tor_worker.tasks.moderator.process_admin_command.delay',
           side_effect=None)
    @patch('tor_worker.tasks.moderator.send_to_slack.delay', side_effect=None)
    @patch('tor_worker.tasks.moderator.process_comment.delay', side_effect=None)
    @patch('tor_worker.tasks.moderator.check_inbox.reddit')
    def test_mod_message(self, mock_reddit, mock_process_comment,
                         mock_slack, mock_admin_cmd, mock_bot_message):
        item = generate_message(
            author=None,
            subject='Important announcement!',
            body='Hehe, just kidding',
        )

        mock_reddit.inbox = generate_inbox()
        mock_reddit.inbox.unread.return_value = [item]

        check_inbox()

        mock_bot_message.assert_not_called()
        mock_process_comment.assert_not_called()
        mock_slack.assert_called_once()
        mock_admin_cmd.assert_not_called()

        item.mark_read.assert_called_once()

    @patch('tor_worker.tasks.moderator.send_bot_message.delay',
           side_effect=None)
    @patch('tor_worker.tasks.moderator.process_admin_command.delay',
           side_effect=None)
    @patch('tor_worker.tasks.moderator.send_to_slack.delay', side_effect=None)
    @patch('tor_worker.tasks.moderator.process_comment.delay', side_effect=None)
    @patch('tor_worker.tasks.moderator.check_inbox.reddit')
    def test_admin_command(self, mock_reddit, mock_process_comment,
                           mock_slack, mock_admin_cmd, mock_bot_message):
        item = generate_message(
            subject='!ignoreplebians'
        )

        mock_reddit.inbox = generate_inbox()
        mock_reddit.inbox.unread.return_value = [item]

        check_inbox()

        mock_bot_message.assert_not_called()
        mock_process_comment.assert_not_called()
        mock_slack.assert_not_called()
        mock_admin_cmd.assert_called_once()

        item.mark_read.assert_called_once()
