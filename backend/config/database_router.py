# backend/config/database_router.py

class SocialRouter:
    """
    A router to control all database operations on models in social apps.
    """

    route_app_labels = {
        'albums',
        'comments',
        'media',
        'messenger',
        'newsfeed',
        'notifications',
        'pages',
        'reactions',
        'social',
        'stories',
        'tagging',
    }

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'social_db'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'social_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        # Allow relations only within the same database
        if obj1._state.db == obj2._state.db:
            return True
        return False  # Disallow cross-database relations

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == 'social_db'
        return db == 'default'
