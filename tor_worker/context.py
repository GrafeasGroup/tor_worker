from praw.models import Comment

"""
These methods are used for detecting the current state of a post (e.g., claimed,
unclaimed, done) and the surrounding context based on the specific comment data
given.

This helps reduce the amount of data we _have_ to store in Redis.
"""


def is_code_of_conduct(comment: Comment):
    if 'code of conduct' in comment.body.lower():
        return True

    return False


def is_claimed_post_response(comment: Comment):
    if 'is yours' in comment.body.lower():
        return True
    if 'already claimed' in comment.body.lower():
        return True

    return False


def is_claimable_post(comment: Comment):
    # Need to accept the CoC before claiming
    if is_code_of_conduct(comment):
        return False

    if 'is still unclaimed' in comment.body.lower():
        return True

    return False
