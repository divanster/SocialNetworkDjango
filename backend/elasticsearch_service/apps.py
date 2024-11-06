# elasticsearch_service/apps.py

from django.apps import AppConfig


class ElasticsearchServiceConfig(AppConfig):
    name = 'elasticsearch_service'

    def ready(self):
        import elasticsearch_service.signals  # noqa
