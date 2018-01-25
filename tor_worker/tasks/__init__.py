from tor_worker import __BROKER_URL__

from celery import Celery


app = Celery(broker=__BROKER_URL__)
app.conf.enable_utc = True
app.conf.task_routes = ([
    # ('tor_worker.tasks.moderator.*', {'queue': 'reddit_tor_user'}),
    # ('tor_worker.tasks.anyone.*', {'queue': 'reddit'}),
    # ('tor_worker.tasks.slack.*', {'queue': 'general'}),
])
