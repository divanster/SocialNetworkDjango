# backend/core/management/commands/wait_for_db.py

import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to pause execution until the database is available"""

    def handle(self, *args, **options):
        """
        Repeatedly try to establish a connection to the database until successful.
        This command is particularly useful when orchestrating with Docker to ensure
        that the database is fully ready before Django attempts to migrate or perform other actions.
        """
        self.stdout.write('Waiting for database...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
                self.stdout.write(self.style.SUCCESS('Database available!'))
            except OperationalError:
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)
