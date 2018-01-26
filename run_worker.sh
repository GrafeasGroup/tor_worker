#!/usr/bin/env bash

celery worker --app=tor_worker.app -l info --purge -Q 'default' --autoscale='10,1' -n 'main@%n.%d' -E -B
