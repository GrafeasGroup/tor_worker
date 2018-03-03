#!/usr/bin/env python3

import time

# We need this for routing:
from tor_worker.app import app  # noqa

from celery import signature
from redis import StrictRedis as RedisClient


redis = RedisClient(host='localhost', port=6379, db=1)

# Here are the tasks imported using an agnostic way of queuing them
test_system = signature('tor_worker.tasks.anyone.test_system')  # noqa
send_bot_message = signature('tor_worker.tasks.moderator.send_bot_message')  # noqa
fake_task = signature('tor_worker.foo')  # noqa

print('Pre-seed time:  %d' % time.time())

for i in range(1, 500):
    # fake_task.delay()
    test_system.delay()
    # send_bot_message.delay(f'test message {i}', to='spez',
    #                        subject=f'Test {i}')

start = time.time()
print('Post-seed time: %d' % start)
count = redis.llen('celery')

while count > 0:
    print('Jobs left: %d' % count)
    time.sleep(1)
    count = redis.llen('celery')

stop = time.time()
print('Done time:      %d' % stop)

print('Execution time: %d' % (stop - start))
