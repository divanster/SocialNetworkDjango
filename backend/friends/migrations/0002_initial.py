# Generated by Django 4.2.14 on 2024-09-18 18:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('friends', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendship',
            name='user1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friendships', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='friendship',
            name='user2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friends', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='friendrequest',
            name='receiver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_friend_requests', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='friendrequest',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_friend_requests', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='block',
            name='blocked',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocked_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='block',
            name='blocker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocker_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='friendship',
            constraint=models.UniqueConstraint(fields=('user1', 'user2'), name='unique_friendship'),
        ),
        migrations.AddConstraint(
            model_name='friendship',
            constraint=models.CheckConstraint(check=models.Q(('user1__lt', models.F('user2'))), name='user1_lt_user2'),
        ),
        migrations.AddConstraint(
            model_name='friendrequest',
            constraint=models.UniqueConstraint(condition=models.Q(('status', 'pending')), fields=('sender', 'receiver'), name='unique_pending_request'),
        ),
        migrations.AlterUniqueTogether(
            name='friendrequest',
            unique_together={('sender', 'receiver')},
        ),
        migrations.AddConstraint(
            model_name='block',
            constraint=models.CheckConstraint(check=models.Q(('blocker', models.F('blocked')), _negated=True), name='block_self_check'),
        ),
        migrations.AlterUniqueTogether(
            name='block',
            unique_together={('blocker', 'blocked')},
        ),
    ]