import pytest  # noqa
import os

from tor_worker.tasks.anyone import send_to_slack

from slackclient import SlackClient

import unittest
from unittest.mock import patch


class SendToSlackTest(unittest.TestCase):

    def setUp(self):
        os.environ['SLACK_API_KEY'] = 'notavalidkey'

    @patch('tor_worker.tasks.base.SlackClient', spec=SlackClient)
    @patch('tor_worker.tasks.anyone.send_to_slack.slack', spec=SlackClient)
    def test_send_to_slack(self, mock_client, mock_slack):
        send_to_slack('foo', 'bar')

        mock_client.api_call.assert_called_once_with(
            'chat.postMessage',
            channel='bar',
            text='foo'
        )
