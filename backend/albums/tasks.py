from celery import shared_task

from config.celery import app
from .models import Album
from celery.schedules import crontab


@shared_task
def process_new_album(album_id):
    # Simulate post-creation processing, such as sending notifications
    try:
        album = Album.objects.get(id=album_id)
        # Add background logic here, e.g., send notifications
        print(f'Processing album: {album.title}')
    except Album.DoesNotExist:
        print(f'Album with id {album_id} does not exist')

    # scheduled update of the album statistics every night
    app.conf.beat_schedule = {
        'daily-album-update': {
            'task': 'albums.tasks.daily_album_statistics_update',
            'schedule': crontab(hour=0, minute=0),  # Runs every day at midnight
        },
    }
