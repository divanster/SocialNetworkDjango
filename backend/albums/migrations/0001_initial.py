# Generated by Django 5.1.2 on 2024-11-04 19:08

import albums.models
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('visibility', models.CharField(choices=[('public', 'Public'), ('friends', 'Friends'), ('private', 'Private')], default='public', help_text='Visibility of the album', max_length=10)),
                ('user', models.ForeignKey(help_text='User who owns the album', on_delete=django.db.models.deletion.CASCADE, related_name='albums', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'albums',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('image', models.ImageField(upload_to=albums.models.album_image_file_path)),
                ('description', models.TextField(blank=True)),
                ('album', models.ForeignKey(help_text='Album to which this photo belongs', on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='albums.album')),
            ],
            options={
                'db_table': 'photos',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='album',
            index=models.Index(fields=['user'], name='user_idx'),
        ),
        migrations.AddIndex(
            model_name='album',
            index=models.Index(fields=['visibility'], name='albums_visibil_5e0271_idx'),
        ),
        migrations.AddConstraint(
            model_name='album',
            constraint=models.UniqueConstraint(fields=('user', 'title'), name='unique_user_album_title'),
        ),
    ]
