import os

__version__ = '0.1.0'

__BROKER_URL__ = os.getenv('TASK_BROKER', 'redis://localhost:6379/1')

OUR_BOTS = [
    'transcribersofreddit',
    'transcribot',
]
