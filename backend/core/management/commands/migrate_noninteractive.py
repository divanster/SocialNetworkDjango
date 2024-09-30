# backend/core/management/commands/migrate_noninteractive.py

from django.core.management.commands.migrate import Command as MigrateCommand
from .migration_questioner import NonInteractiveMigrationQuestioner


class Command(MigrateCommand):
    """
    Custom migrate command that runs migrations non-interactively.
    """

    def handle(self, *args, **options):
        options['interactive'] = False
        options['questioner'] = NonInteractiveMigrationQuestioner()
        super().handle(*args, **options)
