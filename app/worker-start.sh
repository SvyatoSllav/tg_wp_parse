#! /usr/bin/env bash
set -e

celery -A app.main_worker beat -l info --detach
celery -A app.main_worker worker -l info