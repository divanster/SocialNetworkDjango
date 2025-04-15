# backend/kafka_app/tasks/base_task.py

from celery import Task
import logging

logger = logging.getLogger(__name__)


class BaseTask(Task):
    abstract = True  # Ensures Celery does not treat this as a concrete task

    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f"Task {self.name} [{task_id}] succeeded with result: {retval}")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {self.name} [{task_id}] failed with exception: {exc}")
