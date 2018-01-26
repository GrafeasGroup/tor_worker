#!/usr/bin/env python3

from tor_worker.app import app  # noqa
from tor_worker.tasks.anyone import test_system


for i in range(1, 100):
    test_system.delay()
