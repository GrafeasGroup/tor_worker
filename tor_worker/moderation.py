# from tor_worker.tasks.anyone import send_to_slack

from praw.models import Comment


MOD_SUPPORT_PHRASES = [
]


def process_mod_intervention(comment: Comment, reddit):
    """
    Triggers an alert in Slack with a link to the comment if there is something
    offensive or in need of moderator intervention
    """
    from tor_worker.tasks.anyone import send_to_slack
    phrases = []
    for regex in MOD_SUPPORT_PHRASES:
        matches = regex.search(comment.body)
        if not matches:
            continue

        phrases.append(matches.group())

    if len(phrases) == 0:
        # Nothing offensive here, why did this function get triggered?
        return

    # Wrap each phrase in double-quotes (") and commas in between
    phrases = '"' + '", "'.join(phrases) + '"'

    title = 'Mod Intervention Needed'
    message = f'Detected use of {phrases} <{comment.submission.shortlink}>'

    # TODO: send message to slack
    send_to_slack.delay(
        f':rotating_light::rotating_light: {title} '
        f':rotating_light::rotating_light:\n\n'
        f'{message}',
        '#general'
    )
