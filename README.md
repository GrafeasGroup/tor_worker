# ToR Worker

This is a workhorse for Transcribers Of Reddit to chug through tasks queued up for processing. This shall act as an experiment to rewrite the Transcribers of Reddit bots using Celery task runner framework as a basis.

It is currently in pre-alpha and is only made publicly available for feedback from select individuals (you already know who you are).

## Install

```bash
$ git clone git@github.com:GrafeasGroup/tor_worker.git tor_worker
$ cd tor_worker
$ pip install --process-dependency-links -e .
```

## Use

Set these environment variables ahead of time:

- `praw_username` - The username of the Reddit account to login
- `praw_password` - The password of the Reddit account to login
- `praw_client_id` - The client key of the registered Reddit app
- `praw_client_secret` - The client secret of the registered Reddit app

Invoke the worker locally, like so:

```shell
$ celery worker --app=tor_worker.app -l info -Q 'default' --autoscale '10,1' -n 'main@%h' -B -E
```

Once built, where it says `'default'` above, we will add in the username-specific queues that match up with the PRAW username. We will also start one worker per PRAW username.
