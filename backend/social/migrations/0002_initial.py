# Generated by Django 5.1.4 on 2025-01-09 14:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('social', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='user',
            field=models.ForeignKey(help_text='Author of the post', on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='postimage',
            name='post',
            field=models.ForeignKey(help_text='Post associated with this image', on_delete=django.db.models.deletion.CASCADE, related_name='images', to='social.post'),
        ),
        migrations.AddField(
            model_name='rating',
            name='post',
            field=models.ForeignKey(help_text='Post associated with this rating', on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='social.post'),
        ),
        migrations.AddField(
            model_name='rating',
            name='user',
            field=models.ForeignKey(help_text='User who gave the rating', on_delete=django.db.models.deletion.CASCADE, related_name='ratings_given', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['user'], name='post_user_idx'),
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['title'], name='post_title_idx'),
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['visibility'], name='post_visibility_idx'),
        ),
        migrations.AddIndex(
            model_name='postimage',
            index=models.Index(fields=['post'], name='post_idx'),
        ),
        migrations.AddIndex(
            model_name='rating',
            index=models.Index(fields=['post'], name='rating_post_idx'),
        ),
        migrations.AddIndex(
            model_name='rating',
            index=models.Index(fields=['user'], name='rating_user_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='rating',
            unique_together={('post', 'user')},
        ),
    ]
