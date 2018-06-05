from celery import current_app as app


app.autodiscover_tasks(packages=[
    'tor_worker.role_anyone',
    'tor_worker.role_moderator',
])
