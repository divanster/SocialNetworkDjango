# backend/core/management/commands/migration_questioner.py
from django.db.migrations.questioner import MigrationQuestioner


class NonInteractiveMigrationQuestioner(MigrationQuestioner):
    def ask_rename(self, model_name, old_name, new_name, field_instance):
        return True

    def ask_merge(self, conflict):
        return True

    def ask_rename_model(self, old_model_state, new_model_state):
        return True

    def _boolean_input(self, question, default=None):
        return True  # Automatically answer "yes" to all boolean questions

    def _choice_input(self, question, choices, default=None):
        return default  # Automatically choose the default option for all choices
