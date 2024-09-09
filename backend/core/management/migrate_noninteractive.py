# backend/users/management/commands/migrate_noninteractive.py
from django.core.management.commands.migrate import Command as MigrateCommand
from migration_questioner import NonInteractiveMigrationQuestioner


class Command(MigrateCommand):
    def handle(self, *args, **options):
        options['interactive'] = False
        options['questioner'] = NonInteractiveMigrationQuestioner()
        super().handle(*args, **options)
