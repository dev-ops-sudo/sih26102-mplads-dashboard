from celery import Celery

from app.config import settings


celery_app = Celery(
    "mplads_intelligence",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"],
)
celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    beat_schedule={
        "nightly-risk-and-duplicate-scan": {
            "task": "app.workers.tasks.refresh_national_risk",
            "schedule": 60 * 60 * 24,
        }
    },
)

