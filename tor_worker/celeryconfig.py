from typing import Dict, Any


class Config:
    timezone = 'UTC'
    enable_utc = True
    task_default_queue = 'default'
    beat_schedule: Dict[str, Dict[str, Any]] = {
        'check-inbox': {
            'task': 'tor_worker.role_moderator.tasks.check_inbox',
            'schedule': 90,  # seconds
        },
        'check-subreddit-feeds': {
            'task': 'tor_worker.role_anyone.tasks.check_new_feeds',
            'schedule': 30,  # seconds
        },
    }
    task_routes = ([
        ('tor_worker.role_moderator.tasks.check_inbox', {
            'queue': 'u_transcribersofreddit'
        }),
        ('tor_worker.role_moderator.tasks.process_message', {
            'queue': 'u_transcribersofreddit'
        }),
        ('tor_worker.role_moderator.tasks.send_bot_message', {
            'queue': 'u_transcribersofreddit'
        }),
        ('tor_worker.role_moderator.tasks.*', {
            'queue': 'f_tor_mod'
        }),
    ],)
