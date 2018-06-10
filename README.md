# ToR Worker

This is a workhorse for Transcribers Of Reddit (ToR) to chug through tasks queued up for processing. This shall act as the integration of all of the ToR bots and a control center for more easily administering those celery workers.

It is currently in pre-alpha and is only made publicly available for feedback from select individuals (you already know who you are).

## Install

```bash
$ git clone git@github.com:GrafeasGroup/tor_worker.git tor_worker
$ cd tor_worker
$ pip install --process-dependency-links -e .
```
