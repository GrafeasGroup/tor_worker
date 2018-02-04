import pytest  # noqa

from tor_worker.tasks.moderator import process_admin_command

import unittest
# from unittest.mock import patch


class ProcessAdminCommandTest(unittest.TestCase):

    @pytest.mark.skip(reason='Not yet implemented')
    def test_routing_blacklist(self):

        process_admin_command(subject='!blacklist',
                              author='me',
                              body='you')
