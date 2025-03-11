from celery import Celery
from config import (
    CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND,
)

from opentelemetry.instrumentation.celery import CeleryInstrumentor
def init_celery_tracing(*args, **kwargs):
    CeleryInstrumentor().instrument()

def init_celery() -> Celery:
    init_celery_tracing()

    celery_app = Celery(
        "celery_tasks",
        broker=CELERY_BROKER_URL,
        # backend=CELERY_BACKEND,
        task_ignore_result=True,
    )

    celery_app.conf.update(
        result_backend=CELERY_RESULT_BACKEND,
    )

    celery_app.conf.task_routes = {
        "load_datasource_task": "tasks-load-datasource",
        "delete_datasources_task": "tasks-load-datasource",
        "delete_datastore_task": "tasks-load-datasource",
    }

    # celery_app.set_default()
    celery_app.autodiscover_tasks()
    return celery_app

celery_app = init_celery()