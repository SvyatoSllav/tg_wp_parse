from app.core.containers import CeleryContainer
from app import workers
from celery.signals import task_failure
from app.utils.rollbar import init_rollbar
from app.core.celery import celery_app
import rollbar

container = CeleryContainer()
container.wire(packages=[workers])
container.init_resources()


config = container.config.provided()
init_rollbar(config.ROLLBAR_TOKEN, config.PYTHON_ENV)


def handle_task_failure(**kw):
    rollbar.report_exc_info(extra_data=kw)


task_failure.connect(handle_task_failure)
