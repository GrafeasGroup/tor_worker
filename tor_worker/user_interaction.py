from urllib.parse import quote as uri_escape

from tor_worker import __version__

faq_link = 'https://www.reddit.com/r/TranscribersOfReddit/wiki/index'
source_link = 'https://github.com/GrafeasGroup/tor_worker'

responses = {
    'mention': (
        'Hi there! Thanks for pinging me!\n\n'
        'Due to some changes with how Reddit and individual subreddits handle '
        'bots, I can\'t be summoned directly to your comment anymore. If '
        'there\'s something that you would like assistance with, please post '
        'a link in /r/DescriptionPlease, and one of our lovely volunteers will '
        'be along shortly.\n\nThanks for using our services! We hope we can '
        'make your day a little bit better :)\n\nCheers,\n\n'
        'The Mods of /r/TranscribersOfReddit'
    ),
}


def message_link(to='/r/TranscribersOfReddit', subject='Bot Questions',
                 message=''):
    return 'https://www.reddit.com/message/compose?' \
        'to={to}&subject={sub}&message={msg}'.format(
            to=uri_escape(to),
            sub=uri_escape(subject),
            msg=uri_escape(message),
        )


def format_bot_response(message):
    """
    Formats the response message the bot sends out to users via comment or
    message. Often aliased as `_()`
    """
    message_the_mods_link = message_link(
        to='/r/TranscribersOfReddit',
        subject='Bot Questions'
    )

    footer = ' | '.join([
        f'v{__version__}',
        f'This message was posted by a bot.',
        f'[FAQ]({faq_link})',
        f'[Source]({source_link})',
        f'Questions? [Message the mods!]({message_the_mods_link})',
    ])
    return f'{message}\n\n---\n\n{footer}'
