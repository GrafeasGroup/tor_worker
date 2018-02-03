import pytest  # noqa

from tor_worker.tasks.anyone import process_comment

from ..generators import RedditGenerator

import unittest
from unittest.mock import patch, MagicMock


class ProcessConductCommentTest(unittest.TestCase, RedditGenerator):
    """
    Given that the parent comment is about the code of conduct...
    """

    def setUp(self):
        target = self.generate_comment()
        parent = self.generate_comment()

        target.author.name = 'me'
        target.body = 'I accept. I volunteer as tribute!'
        target.parent = parent

        parent.author.name = 'transcribersofreddit'
        parent.body = 'You have to sign the code of conduct before you can ' \
            'claim anything, you dunce.'

        # Optional, but why not? They _should_ be the same in reality
        target.submission = parent.submission

        self.comment = target

    @patch('tor_worker.tasks.anyone.process_comment.reddit')
    @patch('tor_worker.tasks.anyone.is_claimed_post_response')
    @patch('tor_worker.tasks.anyone.is_code_of_conduct')
    @patch('tor_worker.tasks.anyone.is_claimable_post')
    def test_agree(self, mock_claimable, mock_coc, mock_claimed_post,
                   mock_reddit):
        self.comment.body = 'I accept. I volunteer as tribute!'
        mock_reddit.comment = MagicMock(name='comment',
                                        return_value=self.comment)

        process_comment('abcdef')
        # TODO: more to come when actual functionality is built-out

        mock_reddit.comment.assert_called_once_with('abcdef')
        mock_coc.assert_called_once_with(self.comment.parent)
        mock_claimed_post.assert_not_called()
        mock_claimable.assert_not_called()

    @patch('tor_worker.tasks.anyone.process_comment.reddit')
    @patch('tor_worker.tasks.anyone.is_claimed_post_response')
    @patch('tor_worker.tasks.anyone.is_code_of_conduct')
    @patch('tor_worker.tasks.anyone.is_claimable_post')
    def test_disagree(self, mock_claimable, mock_coc, mock_claimed_post,
                      mock_reddit):
        self.comment.body = 'Nah, go screw yourself.'
        mock_reddit.comment = MagicMock(name='comment',
                                        return_value=self.comment)

        process_comment('abcdef')
        # TODO: more to come when actual functionality is built-out

        mock_reddit.comment.assert_called_once_with('abcdef')
        mock_coc.assert_called_once_with(self.comment.parent)
        mock_claimed_post.assert_not_called()
        mock_claimable.assert_not_called()


class ProcessClaimableCommentTest(unittest.TestCase, RedditGenerator):
    """
    Given that the parent comment indicates the post is unclaimed...
    """

    def setUp(self):
        target = self.generate_comment()
        parent = self.generate_comment()

        target.author.name = 'me'
        target.body = 'I claim it! I volunteer as tribute!'
        target.parent = parent

        parent.author.name = 'transcribersofreddit'
        parent.body = 'This post is unclaimed'

        # Optional, but why not? They _should_ be the same in reality
        target.submission = parent.submission

        self.comment = target

    @patch('tor_worker.tasks.anyone.process_comment.reddit')
    @patch('tor_worker.tasks.anyone.process_mod_intervention')
    def test_other_bot_commented(self, mod_intervention, mock_reddit):
        self.comment.author.name = 'transcribot'
        mock_reddit.comment = MagicMock(name='comment',
                                        return_value=self.comment)
        mod_intervention.return_value = None

        process_comment('abcdef')
        # TODO: more to come when actual functionality is built-out

        mock_reddit.comment.assert_called_with('abcdef')
        mod_intervention.assert_not_called()

    @patch('tor_worker.tasks.anyone.process_comment.reddit')
    def test_claim(self, mock_reddit):
        self.comment.body = 'I claim this land in the name of France!'
        mock_reddit.comment = MagicMock(name='comment',
                                        return_value=self.comment)

        process_comment('abcdef')
        # TODO: more to come when actual functionality is built-out

        mock_reddit.comment.assert_called_with('abcdef')

    @patch('tor_worker.tasks.anyone.process_comment.reddit')
    @patch('tor_worker.tasks.anyone.send_to_slack.delay')
    def test_refuse(self, mock_slack, mock_reddit):
        self.comment.body = 'Nah, screw it. I can do it later'
        mock_slack.return_value = None
        mock_reddit.comment = MagicMock(name='comment',
                                        return_value=self.comment)

        process_comment('abcdef')
        # TODO: more to come when actual functionality is built-out

        mock_reddit.comment.assert_called_with('abcdef')
        mock_slack.assert_not_called()

    @patch('tor_worker.tasks.anyone.process_comment.reddit')
    @patch('tor_worker.tasks.anyone.send_to_slack.delay')
    def test_mod_intervention(self, mock_slack, mock_reddit):
        self.comment.body = 'Nah, fuck it. I can do it later'
        mock_slack.return_value = None
        mock_reddit.comment = MagicMock(name='comment',
                                        return_value=self.comment)

        process_comment('abcdef')
        # TODO: more to come when actual functionality is built-out

        mock_reddit.comment.assert_called_with('abcdef')
        mock_slack.assert_called()


class ProcessDoneCommentTest(unittest.TestCase, RedditGenerator):
    """
    Given that the parent comment indicates the post is unclaimed...
    """

    def setUp(self):
        target = self.generate_comment(name='comment')
        target.author.name = 'me'
        target.body = 'done'

        parent = self.generate_comment(name='parent')
        parent.author.name = 'transcribersofreddit'
        parent.body = 'The post is yours!'

        parent.submission = target.submission
        target.parent = parent

        target.submission.link_flair_text = 'In Progress'

        self.comment = target

    @patch('tor_worker.tasks.anyone.process_comment.reddit')
    @patch('tor_worker.tasks.anyone.is_claimed_post_response')
    @patch('tor_worker.tasks.anyone.is_code_of_conduct')
    @patch('tor_worker.tasks.anyone.is_claimable_post')
    def test_misspelled_done(self, mock_claimable, mock_coc, mock_claimed_post,
                             mock_reddit):
        mock_coc.return_value = False
        self.comment.body = 'deno'

        mock_reddit.comment = MagicMock(name='comment',
                                        return_value=self.comment)

        process_comment('abcdef')
        # TODO: more to come when actual functionality is built-out

        mock_reddit.comment.assert_called_once_with('abcdef')
        mock_coc.assert_called_once_with(self.comment.parent)
        mock_claimed_post.assert_called_once_with(self.comment.parent)
        mock_claimable.assert_not_called()

    @patch('tor_worker.tasks.anyone.process_comment.reddit')
    @patch('tor_worker.tasks.anyone.is_claimed_post_response')
    @patch('tor_worker.tasks.anyone.is_code_of_conduct')
    @patch('tor_worker.tasks.anyone.is_claimable_post')
    def test_done(self, mock_claimable, mock_coc, mock_claimed_post,
                  mock_reddit):
        mock_coc.return_value = False
        mock_reddit.comment = MagicMock(name='comment',
                                        return_value=self.comment)

        process_comment('abcdef')
        # TODO: more to come when actual functionality is built-out

        mock_reddit.comment.assert_called_once_with('abcdef')
        mock_coc.assert_called_once_with(self.comment.parent)
        mock_claimed_post.assert_called_once_with(self.comment.parent)
        mock_claimable.assert_not_called()

    @patch('tor_worker.tasks.anyone.process_comment.reddit')
    @patch('tor_worker.tasks.anyone.is_claimed_post_response')
    @patch('tor_worker.tasks.anyone.is_code_of_conduct')
    @patch('tor_worker.tasks.anyone.is_claimable_post')
    def test_override_as_admin(self, mock_claimable, mock_coc,
                               mock_claimed_post, mock_reddit):
        mock_coc.return_value = False
        self.comment.body = '!override'
        self.comment.author.name = 'tor_mod5'
        mock_reddit.comment = MagicMock(name='comment',
                                        return_value=self.comment)

        # TODO: Test exception being thrown because unprivileged user???
        process_comment('abcdef')
        # TODO: more to come when actual functionality is built-out

        mock_reddit.comment.assert_called_once_with('abcdef')
        mock_coc.assert_called_once_with(self.comment.parent)
        mock_claimed_post.assert_called_once_with(self.comment.parent)
        mock_claimable.assert_not_called()

    @patch('tor_worker.tasks.anyone.process_comment.reddit')
    @patch('tor_worker.tasks.anyone.is_claimed_post_response')
    @patch('tor_worker.tasks.anyone.is_code_of_conduct')
    @patch('tor_worker.tasks.anyone.is_claimable_post')
    def test_override_as_anon(self, mock_claimable, mock_coc, mock_claimed_post,
                              mock_reddit):
        mock_coc.return_value = False
        self.comment.body = '!override'
        mock_reddit.comment = MagicMock(name='comment',
                                        return_value=self.comment)

        # TODO: Test exception being thrown because unprivileged user???
        process_comment('abcdef')
        # TODO: more to come when actual functionality is built-out

        mock_reddit.comment.assert_called_once_with('abcdef')
        mock_coc.assert_called_once_with(self.comment.parent)
        mock_claimed_post.assert_called_once_with(self.comment.parent)
        mock_claimable.assert_not_called()
