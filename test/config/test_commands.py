import pytest  # noqa

from tor_worker.config import CommandSet, Config

import unittest
from unittest.mock import patch


def noop(author, body, message_id):
    pass


def dummy_json_loader(path):
    if path.endswith('settings.json'):
        return {
            'environment': 'testing',
            'gifs': {
                'no': ['https://no.example.com/'],
                'thumbs_up': ['https://thumbs_up.example.com/'],
            },
        }
    elif path.endswith('subreddits.json'):
        return {
            'me_irl': {},
            'ProgrammingHumor': {},
        }
    elif path.endswith('globals.json'):
        return {
            'environment': 'testing',
            'moderators': [
                'tor_mod'
            ],
        }
    else:
        raise NotImplementedError(path)


class CommandSetTest(unittest.TestCase):
    def setUp(self):
        self.command = CommandSet(settings={
            'notAuthorizedResponses': [
                'Nope, sorry!',
            ],
            'commands': {
                'blacklist': {
                    'description': '',
                    'allowedNames': [],
                    'pythonFunction': 'noop',
                },
                'ping': {
                    'description': '',
                    'allowedNames': ['me'],
                    'pythonFunction': 'noop',
                },
                'reload': {
                    'description': '',
                    'allowedNames': [],
                    'pythonFunction': 'noop',
                },
                'update': {
                    'description': '',
                    # No `allowedNames` key.
                    'pythonFunction': 'noop',
                },
            }
        })

    @patch('tor_worker.config.helpers.assert_valid_directory',
           side_effect=None)
    @patch('tor_worker.config.helpers.load_json',
           side_effect=dummy_json_loader)
    def test_no_such_command(self, mock_json, mock_valid_dir):
        config = Config()
        assert config.globals.is_moderator('tor_mod')
        assert not config.globals.is_moderator('me')

        assert not self.command.allows('somerandomcommand').by_user('me'),\
            'User "me" is allowed to use the command "somerandomcommand"'
        assert not self.command.allows('somerandomcommand').by_user('tor_mod'),\
            'User "tor_mod" is allowed to use the command "somerandomcommand"'

    @patch('tor_worker.config.helpers.assert_valid_directory',
           side_effect=None)
    @patch('tor_worker.config.helpers.load_json',
           side_effect=dummy_json_loader)
    def test_not_authorized(self, mock_json, mock_valid_dir):
        config = Config()
        assert not config.globals.is_moderator('me')
        assert config.globals.is_moderator('tor_mod')

        assert not self.command.allows('reload').by_user('me'),\
            'User "me" is allowed to use the command "reload"'
        assert self.command.allows('reload').by_user('tor_mod'),\
            'User "tor_mod" is not allowed to use the command "reload"'

    @patch('tor_worker.config.helpers.assert_valid_directory',
           side_effect=None)
    @patch('tor_worker.config.helpers.load_json',
           side_effect=dummy_json_loader)
    def test_no_users_defined(self, mock_json, mock_valid_dir):
        config = Config()
        assert config.globals.is_moderator('tor_mod')
        assert not config.globals.is_moderator('me')

        assert not self.command.allows('update').by_user('me'),\
            'User "me" is allowed to use the command "update"'
        assert self.command.allows('update').by_user('tor_mod'),\
            'User "tor_mod" is not allowed to use the command "update"'

    @patch('tor_worker.config.helpers.assert_valid_directory',
           side_effect=None)
    @patch('tor_worker.config.helpers.load_json',
           side_effect=dummy_json_loader)
    def test_user_is_allowed(self, mock_json, mock_valid_dir):
        config = Config()
        assert config.globals.is_moderator('tor_mod')
        assert not config.globals.is_moderator('me')

        assert self.command.allows('ping').by_user('me'),\
            'User "me" is not allowed to use the command "update"'
        assert self.command.allows('ping').by_user('tor_mod'),\
            'User "tor_mod" is not allowed to use the command "update"'
