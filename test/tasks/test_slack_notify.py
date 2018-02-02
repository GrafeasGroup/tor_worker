import pytest  # noqa

from tor_worker.tasks.anyone import send_to_slack

import unittest
from unittest.mock import patch, MagicMock


class SendToSlackTest(unittest.TestCase):

    def setUp(self):
        pass

    @patch('tor_worker.tasks.anyone.send_to_slack.slack')
    def test_send_to_slack(self, mock_slack):
        mock_slack.api_call = MagicMock(name='slack.api_call')
        mock_slack.api_call.return_value = None

        send_to_slack('foo', 'bar')

        mock_slack.api_call.assert_called_once_with('chat.postMessage',
                                                    channel='bar',
                                                    text='foo')
