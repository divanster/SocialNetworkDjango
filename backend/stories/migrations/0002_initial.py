# Generated by Django 5.1.4 on 2025-01-09 14:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('stories', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='user',
            field=models.ForeignKey(help_text='User who created the story', on_delete=django.db.models.deletion.CASCADE, related_name='stories', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='story',
            name='viewed_by',
            field=models.ManyToManyField(blank=True, help_text='Users who have viewed the story', related_name='viewed_stories', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='story',
            index=models.Index(fields=['user'], name='stories_user_id_6205fe_idx'),
        ),
        migrations.AddIndex(
            model_name='story',
            index=models.Index(fields=['created_at'], name='stories_created_c866ff_idx'),
        ),
        migrations.AddIndex(
            model_name='story',
            index=models.Index(fields=['visibility'], name='stories_visibil_c3581a_idx'),
        ),
    ]
