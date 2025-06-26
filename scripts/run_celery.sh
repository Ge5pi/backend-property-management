#!/bin/bash

# Start celery worker
celery -A property_management worker -l info & \
 # Start celery beat
celery -A property_management beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
