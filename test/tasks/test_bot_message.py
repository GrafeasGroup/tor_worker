import pytest  # noqa

from tor_worker.tasks.moderator import send_bot_message
from tor_worker.tasks.base import InvalidUser

from ..generators import RedditGenerator

import unittest
from unittest.mock import patch, MagicMock

import praw.models


class SendBotMessageTest(unittest.TestCase, RedditGenerator):
    """
    Tests for the ``send_bot_message`` task
    """

    @patch('tor_worker.tasks.moderator.send_bot_message.reddit')
    def test_reply_message(self, mock_reddit):
        user = self.generate_redditor()
        msg = self.generate_message()

        mock_reddit.user = MagicMock(spec=praw.models.User)
        mock_reddit.user.me = MagicMock(return_value=user)
        user.name = 'transcribersofreddit'

        mock_reddit.message = MagicMock(return_value=msg)

        send_bot_message(message_id='asdf',
                         body="It's time we met face-to-face")

        mock_reddit.user.me.assert_called_once()
        mock_reddit.message.assert_called_once()
        msg.reply.assert_called_once_with("It's time we met face-to-face")

    @patch('tor_worker.tasks.moderator.send_bot_message.reddit')
    def test_redditor_recipient(self, mock_reddit):
        user = self.generate_redditor()
        msg = self.generate_message()

        recipient = self.generate_redditor()
        recipient.name = 'me'
        mock_reddit.redditor = MagicMock(return_value=recipient)

        mock_reddit.user = MagicMock(spec=praw.models.User)
        mock_reddit.user.me = MagicMock(return_value=user)
        user.name = 'transcribersofreddit'

        mock_reddit.message = MagicMock(return_value=msg)

        send_bot_message(to='me', subject='Cryptic stuff happening...',
                         body="It's time we met face-to-face")

        mock_reddit.user.me.assert_called_once()
        mock_reddit.message.assert_not_called()
        msg.reply.assert_not_called()
        mock_reddit.redditor.assert_called_once()
        recipient.message.assert_called_once_with(
            'Cryptic stuff happening...',
            "It's time we met face-to-face"
        )

    @patch('tor_worker.tasks.moderator.send_bot_message.reddit')
    def test_no_input(self, mock_reddit):
        mock_reddit.user = MagicMock(spec=praw.models.User)
        user = self.generate_redditor()
        mock_reddit.user.me = MagicMock(return_value=user)
        user.name = 'transcribersofreddit'

        with pytest.raises(NotImplementedError):
            send_bot_message('')

        mock_reddit.user.me.assert_called_once()

    @patch('tor_worker.tasks.moderator.send_bot_message.reddit')
    def test_bad_task_runner(self, mock_reddit):
        mock_reddit.user = MagicMock(spec=praw.models.User)
        user = self.generate_redditor()
        mock_reddit.user.me = MagicMock(return_value=user)
        user.name = 'someotheruser'

        with pytest.raises(InvalidUser):
            send_bot_message(to='me', subject='Cryptic stuff happening...',
                             body="It's time we met face-to-face")

        mock_reddit.user.me.assert_called_once()
