# backend/core/task_utils.py

from celery import Task
import logging

logger = logging.getLogger(__name__)


class BaseTask(Task):
    autoretry_for = (Exception,)
    retry_backoff = True
    retry_backoff_max = 3600  # 1 hour
    max_retries = 5
    default_retry_delay = 60  # 1 minute

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {self.name} [{task_id}] failed with exception: {exc}")
        super().on_failure(exc, task_id, args, kwargs, einfo)
