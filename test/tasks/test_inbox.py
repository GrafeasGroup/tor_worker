import pytest  # noqa

from tor_worker.tasks.moderator import check_inbox

from ..generators import RedditGenerator

import unittest
from unittest.mock import patch


class ProcessInboxMessagesTest(unittest.TestCase, RedditGenerator):
    """
    Tests the routing of certain inbox message types
    """

    @patch('tor_worker.tasks.moderator.send_bot_message.delay')
    @patch('tor_worker.tasks.moderator.process_admin_command.delay')
    @patch('tor_worker.tasks.moderator.send_to_slack.delay')
    @patch('tor_worker.tasks.moderator.process_comment.delay')
    @patch('tor_worker.tasks.moderator.check_inbox.reddit')
    def test_comment(self, mock_reddit, mock_process_comment,
                     mock_slack, mock_admin_cmd, mock_bot_message):
        item = self.generate_comment()
        mock_reddit.inbox = self.generate_inbox()
        mock_reddit.inbox.unread.return_value = [item]

        mock_bot_message.return_value = None
        mock_process_comment.return_value = None
        mock_slack.return_value = None
        mock_admin_cmd.return_value = None

        check_inbox()

        mock_bot_message.assert_not_called()
        mock_process_comment.assert_called_once()
        mock_slack.assert_not_called()
        mock_admin_cmd.assert_not_called()

        item.mark_read.assert_called_once()

    @patch('tor_worker.tasks.moderator.send_bot_message.delay')
    @patch('tor_worker.tasks.moderator.process_admin_command.delay')
    @patch('tor_worker.tasks.moderator.send_to_slack.delay')
    @patch('tor_worker.tasks.moderator.process_comment.delay')
    @patch('tor_worker.tasks.moderator.check_inbox.reddit')
    def test_mention(self, mock_reddit, mock_process_comment,
                     mock_slack, mock_admin_cmd, mock_bot_message):
        item = self.generate_comment()
        item.subject = 'username mention'
        item.body = 'Just letting you know, /u/me, it\'s pretty cool.'

        mock_reddit.inbox = self.generate_inbox()
        mock_reddit.inbox.unread.return_value = [item]

        mock_bot_message.return_value = None
        mock_process_comment.return_value = None
        mock_slack.return_value = None
        mock_admin_cmd.return_value = None

        check_inbox()

        mock_bot_message.assert_called_once()
        mock_process_comment.assert_not_called()
        mock_slack.assert_not_called()
        mock_admin_cmd.assert_not_called()

        item.mark_read.assert_called_once()

    @patch('tor_worker.tasks.moderator.send_bot_message.delay')
    @patch('tor_worker.tasks.moderator.process_admin_command.delay')
    @patch('tor_worker.tasks.moderator.send_to_slack.delay')
    @patch('tor_worker.tasks.moderator.process_comment.delay')
    @patch('tor_worker.tasks.moderator.check_inbox.reddit')
    def test_message(self, mock_reddit, mock_process_comment,
                     mock_slack, mock_admin_cmd, mock_bot_message):
        item = self.generate_message()
        item.subject = 'Yo! I like this subreddit'
        item.body = 'Just letting you know, it\'s pretty cool.'

        mock_reddit.inbox = self.generate_inbox()
        mock_reddit.inbox.unread.return_value = [item]

        mock_bot_message.return_value = None
        mock_process_comment.return_value = None
        mock_slack.return_value = None
        mock_admin_cmd.return_value = None

        check_inbox()

        mock_bot_message.assert_not_called()
        mock_process_comment.assert_not_called()
        mock_slack.assert_called_once()
        mock_admin_cmd.assert_not_called()

        item.mark_read.assert_called_once()

    @patch('tor_worker.tasks.moderator.send_bot_message.delay')
    @patch('tor_worker.tasks.moderator.process_admin_command.delay')
    @patch('tor_worker.tasks.moderator.send_to_slack.delay')
    @patch('tor_worker.tasks.moderator.process_comment.delay')
    @patch('tor_worker.tasks.moderator.check_inbox.reddit')
    def test_mod_message(self, mock_reddit, mock_process_comment,
                         mock_slack, mock_admin_cmd, mock_bot_message):
        item = self.generate_mod_message()
        item.subject = 'Important announcement!'

        mock_reddit.inbox = self.generate_inbox()
        mock_reddit.inbox.unread.return_value = [item]

        mock_bot_message.return_value = None
        mock_process_comment.return_value = None
        mock_slack.return_value = None
        mock_admin_cmd.return_value = None

        check_inbox()

        mock_bot_message.assert_not_called()
        mock_process_comment.assert_not_called()
        mock_slack.assert_called_once()
        mock_admin_cmd.assert_not_called()

        item.mark_read.assert_called_once()

    @patch('tor_worker.tasks.moderator.send_bot_message.delay')
    @patch('tor_worker.tasks.moderator.process_admin_command.delay')
    @patch('tor_worker.tasks.moderator.send_to_slack.delay')
    @patch('tor_worker.tasks.moderator.process_comment.delay')
    @patch('tor_worker.tasks.moderator.check_inbox.reddit')
    def test_admin_command(self, mock_reddit, mock_process_comment,
                           mock_slack, mock_admin_cmd, mock_bot_message):
        item = self.generate_message()
        item.subject = '!ignoreplebians'

        mock_reddit.inbox = self.generate_inbox()
        mock_reddit.inbox.unread.return_value = [item]

        mock_bot_message.return_value = None
        mock_process_comment.return_value = None
        mock_slack.return_value = None
        mock_admin_cmd.return_value = None

        check_inbox()

        mock_bot_message.assert_not_called()
        mock_process_comment.assert_not_called()
        mock_slack.assert_not_called()
        mock_admin_cmd.assert_called_once()

        item.mark_read.assert_called_once()