import pytest  # noqa

from tor_worker.tasks.moderator import (
    process_comment,
    process_mod_intervention,
)

from ..generators import (
    generate_redditor,
    generate_comment,
    generate_submission,
)

import unittest
from unittest.mock import patch, MagicMock


class ProcessConductCommentTest(unittest.TestCase):
    """
    Given that the parent comment is about the code of conduct...
    """

    def setUp(self):
        submission = generate_submission(flair='Unclaimed')
        parent = generate_comment(
            body='You have to sign the code of conduct before you can '
                 'claim anything, you dunce.',
            author='transcribersofreddit',
            submission=submission,
        )
        target = parent.reply('I accept. I volunteer as tribute!')

        self.comment = target

    @patch('tor_worker.tasks.moderator.claim_post.delay', side_effect=None)
    @patch('tor_worker.tasks.moderator.accept_code_of_conduct.delay',
           side_effect=None)
    @patch('tor_worker.tasks.moderator.process_comment.reddit')
    @patch('tor_worker.tasks.moderator.process_mod_intervention',
           side_effect=None)
    def test_agree(self, mod_intervention, mock_reddit, mock_accept_coc,
                   mock_claim):
        mock_reddit.comment = MagicMock(name='comment',
                                        return_value=self.comment)

        self.comment.body = 'I accept the consequences'
        process_comment(self.comment.id)

        mock_accept_coc.assert_called_once_with(self.comment.author.name)
        mock_claim.assert_called_once_with(self.comment.id, verify=False,
                                           first_claim=True)
        mock_reddit.comment.assert_called_with(self.comment.id)
        mod_intervention.assert_called_once()

    @patch('tor_worker.tasks.moderator.claim_post.delay', side_effect=None)
    @patch('tor_worker.tasks.moderator.accept_code_of_conduct.delay',
           side_effect=None)
    @patch('tor_worker.tasks.moderator.unhandled_comment.delay',
           side_effect=None)
    @patch('tor_worker.tasks.moderator.process_comment.reddit')
    @patch('tor_worker.tasks.moderator.process_mod_intervention',
           side_effect=None)
    def test_disagree(self, mod_intervention, mock_reddit, mock_dunno,
                      mock_accept_coc, mock_claim):
        mock_reddit.comment = MagicMock(name='comment',
                                        return_value=self.comment)

        self.comment.body = 'Nah, go screw yourself.'
        process_comment(self.comment.id)

        mock_dunno.assert_called_once()
        mock_accept_coc.assert_not_called()
        mock_claim.assert_not_called()
        mock_reddit.comment.assert_called_with(self.comment.id)
        mod_intervention.assert_called_once()


class ProcessClaimableCommentTest(unittest.TestCase):
    """
    Given that the parent comment indicates the post is unclaimed...
    """

    def setUp(self):
        submission = generate_submission(flair='Unclaimed')
        parent = generate_comment(
            body='This post is unclaimed',
            author='transcribersofreddit',
            submission=submission,
        )
        target = parent.reply('I claim it! I volunteer as tribute!')

        self.comment = target

    @patch('tor_worker.tasks.moderator.unhandled_comment.delay',
           side_effect=None)
    @patch('tor_worker.tasks.moderator.claim_post.delay', side_effect=None)
    @patch('tor_worker.tasks.moderator.process_comment.reddit')
    @patch('tor_worker.tasks.moderator.process_mod_intervention',
           side_effect=None)
    def test_other_bot_commented(self, mod_intervention, mock_reddit,
                                 mock_claim, mock_dunno):
        mock_reddit.comment = MagicMock(name='comment',
                                        return_value=self.comment)

        self.comment.author = generate_redditor(username='transcribot')
        process_comment(self.comment.id)

        mock_claim.assert_not_called()
        mock_reddit.comment.assert_called_with(self.comment.id)
        mod_intervention.assert_not_called()

    @patch('tor_worker.tasks.moderator.unhandled_comment.delay',
           side_effect=None)
    @patch('tor_worker.tasks.moderator.claim_post.delay', side_effect=None)
    @patch('tor_worker.tasks.moderator.process_comment.reddit')
    @patch('tor_worker.tasks.moderator.process_mod_intervention',
           side_effect=None)
    def test_claim(self, mod_intervention, mock_reddit, mock_claim, mock_dunno):
        mock_reddit.comment = MagicMock(name='comment',
                                        return_value=self.comment)

        self.comment.body = 'I claim this land in the name of France!'
        process_comment(self.comment.id)

        mock_claim.assert_called_once_with(self.comment.id)
        mock_reddit.comment.assert_called_with(self.comment.id)
        mod_intervention.assert_called_once()

    @patch('tor_worker.tasks.moderator.unhandled_comment.delay',
           side_effect=None)
    @patch('tor_worker.tasks.moderator.claim_post.delay', side_effect=None)
    @patch('tor_worker.tasks.moderator.process_comment.reddit')
    @patch('tor_worker.tasks.moderator.process_mod_intervention',
           side_effect=None)
    def test_refuse(self, mod_intervention, mock_reddit, mock_claim,
                    mock_dunno):
        mock_reddit.comment = MagicMock(name='comment',
                                        return_value=self.comment)

        self.comment.body = 'Nah, screw it. I can do it later'
        process_comment(self.comment.id)

        mock_dunno.assert_called_once()
        mock_claim.assert_not_called()
        mock_reddit.comment.assert_called_with(self.comment.id)
        mod_intervention.assert_called_once()

    @patch('tor_worker.tasks.moderator.send_to_slack.delay', side_effect=None)
    def test_mod_intervention(self, mock_slack):
        self.comment.body = 'Nah, fuck it. I can do it later'
        process_mod_intervention(self.comment)
        mock_slack.assert_called_once()


class ProcessDoneCommentTest(unittest.TestCase):
    """
    Given that the parent comment indicates the post is unclaimed...
    """

    def setUp(self):
        submission = generate_submission(
            flair='In Progress',
        )
        parent = generate_comment(
            body='The post is yours!',
            author='transcribersofreddit',
            submission=submission,
        )
        target = parent.reply('done')

        self.comment = target

    @patch('tor_worker.tasks.moderator.process_comment.reddit')
    def test_misspelled_done(self, mock_reddit):
        mock_reddit.comment = MagicMock(name='comment',
                                        return_value=self.comment)

        self.comment.body = 'deno'
        process_comment(self.comment.id)
        # TODO: more to come when actual functionality is built-out

        mock_reddit.comment.assert_any_call(self.comment.id)

    @patch('tor_worker.tasks.moderator.process_comment.reddit')
    def test_done(self, mock_reddit):
        mock_reddit.comment = MagicMock(name='comment',
                                        return_value=self.comment)

        process_comment(self.comment.id)
        # TODO: more to come when actual functionality is built-out

        mock_reddit.comment.assert_any_call(self.comment.id)

    @patch('tor_worker.tasks.moderator.process_comment.reddit')
    def test_override_as_admin(self, mock_reddit):
        mock_reddit.comment = MagicMock(name='comment',
                                        return_value=self.comment)

        self.comment.body = '!override'
        self.comment.author = generate_redditor(username='tor_mod5')
        # TODO: Test exception being thrown because unprivileged user???
        process_comment(self.comment.id)
        # TODO: more to come when actual functionality is built-out

        mock_reddit.comment.assert_any_call(self.comment.id)

    @patch('tor_worker.tasks.moderator.process_comment.reddit')
    def test_override_as_anon(self, mock_reddit):
        mock_reddit.comment = MagicMock(name='comment',
                                        return_value=self.comment)

        self.comment.body = '!override'
        # TODO: Test exception being thrown because unprivileged user???
        process_comment(self.comment.id)
        # TODO: more to come when actual functionality is built-out

        mock_reddit.comment.assert_any_call(self.comment.id)

    @patch('tor_worker.tasks.moderator.unhandled_comment.delay',
           side_effect=None)
    @patch('tor_worker.tasks.moderator.process_comment.reddit')
    def test_weird_response(self, mock_reddit, mock_dunno):
        mock_reddit.comment = MagicMock(name='comment',
                                        return_value=self.comment)

        self.comment.body = "adsflkj232oiqqw123lk1209uasd;"
        process_comment(self.comment.id)
        # TODO: more to come when actual functionality is built-out

        mock_dunno.assert_called_once()
        mock_reddit.comment.assert_any_call(self.comment.id)
