# ToR Worker

This is a workhorse for Transcribers Of Reddit to chug through tasks queued up for processing

## Install

```bash
$ git clone git@github.com:GrafeasGroup/tor_worker.git tor_worker
$ cd tor_worker
$ pip install -e .
```

## Use

### For a specific username

Set these environment variables ahead of time:

- `QUEUES` - A space-delimited list of queues to process
- `praw_username` - The username of the Reddit account to login
- `praw_password` - The password of the Reddit account to login
- `praw_client_id` - The client key of the registered Reddit app
- `praw_client_secret` - The client secret of the registered Reddit app

Invoke the worker like so:

```shell
$ tor-worker work <QUEUE_NAME> [<QUEUE_NAME> [<QUEUE_NAME> [...]]]
# => starts daemon mode chugging through the work in the queues
```
