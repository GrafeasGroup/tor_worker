#!/usr/bin/env bash

celery worker --app=tor_worker.app --purge -l info -Q 'celery' --autoscale='10,1' -n 'main@%n.%d' # -B
