from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, UserProfile
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
from django.core.exceptions import ObjectDoesNotExist


@receiver(post_save, sender=CustomUser)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create the UserProfile if the CustomUser is created
        UserProfile.objects.create(user=instance)
    else:
        # If the user already exists, ensure the profile is saved
        try:
            instance.profile.save()
        except ObjectDoesNotExist:
            # Handle the case where the profile doesn't exist for some reason
            UserProfile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def send_user_update(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    try:
        user_data = {
            'id': instance.id,
            'username': instance.username,
            'email': instance.email,
            'first_name': instance.profile.first_name,
            'last_name': instance.profile.last_name,
            # Add more user fields as needed
        }

        event_type = 'new_user' if created else 'update_user'

        async_to_sync(channel_layer.group_send)(
            'users',
            {
                'type': event_type,
                'user': user_data
            }
        )
    except Exception as e:
        # Handle potential errors (e.g., profile data not available,
        # channel layer not connected)
        print(f"Error in sending user update: {str(e)}")
