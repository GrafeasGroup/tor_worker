#!/usr/bin/env bash

celery worker --app=tor_worker.app -l info -Q 'celery' -B --autoscale='10,1' -n 'main@%n.%d' --purge
