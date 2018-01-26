#!/usr/bin/env python3

import time

from tor_worker.app import app  # noqa
from tor_worker.tasks.anyone import test_system  # noqa
from tor_worker.tasks.moderator import send_bot_message  # noqa

from redis import StrictRedis as RedisClient


redis = RedisClient(host='localhost', port=6379, db=1)

print('Pre-seed time:  %d' % time.time())

for i in range(1, 500):
    test_system.delay()
    # pass
    # send_bot_message.delay(f'test message {i}', to='spez',
    #                        subject=f'Test {i}')

start = time.time()
print('Post-seed time: %d' % start)
count = redis.llen('celery')

while count > 0:
    print('Jobs left: %d' % count)
    time.sleep(1)
    count = redis.llen('celery')
    pass

stop = time.time()
print('Done time:      %d' % stop)

print('Execution time: %d' % (stop - start))
