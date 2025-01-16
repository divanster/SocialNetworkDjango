# backend/core/management/commands/migrate_noninteractive.py

from django.core.management.base import BaseCommand
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run migrations without interactive prompts.'

    def handle(self, *args, **options):
        try:
            # Make migrations without prompts
            call_command('makemigrations', interactive=False, verbosity=1)
            # Apply migrations without prompts
            call_command('migrate', interactive=False, verbosity=1)
            logger.info("Migrations applied successfully without interactive prompts.")
        except Exception as e:
            logger.error(f"Error applying migrations non-interactively: {e}")
            self.stderr.write(self.style.ERROR(f"Migration failed: {e}"))
