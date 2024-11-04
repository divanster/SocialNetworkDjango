from django.core.management.base import BaseCommand
from tagging.models import TaggedItem
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Identify and fix broken GenericForeignKey relationships'

    def handle(self, *args, **kwargs):
        for tag in TaggedItem.objects.all():
            content_type = tag.content_type
            model_class = content_type.model_class()
            if not model_class.objects.filter(id=tag.object_id).exists():
                self.stdout.write(f"Deleting orphaned tag {tag.id} related to missing {content_type}")
                tag.delete()
