# backend/kafka_app/constants.py

# =========================================
# Kafka Topic Keys
# =========================================
USER_EVENTS = 'USER_EVENTS'
NOTIFICATIONS = 'NOTIFICATIONS'
ALBUM_EVENTS = 'ALBUM_EVENTS'
COMMENT_EVENTS = 'COMMENT_EVENTS'
FOLLOW_EVENTS = 'FOLLOW_EVENTS'
FRIEND_EVENTS = 'FRIEND_EVENTS'
NEWSFEED_EVENTS = 'NEWSFEED_EVENTS'
REACTION_EVENTS = 'REACTION_EVENTS'
SOCIAL_EVENTS = 'SOCIAL_EVENTS'
TAGGING_EVENTS = 'TAGGING_EVENTS'
PHOTO_EVENTS = 'PHOTO_EVENTS'
STORY_EVENTS = 'STORY_EVENTS'
MESSENGER_EVENTS = 'MESSENGER_EVENTS'

# =========================================
# User Event Types
# =========================================
USER_CREATED = 'user_created'
USER_UPDATED = 'user_updated'
USER_SOFT_DELETED = 'user_soft_deleted'
USER_RESTORED = 'user_restored'
USER_REGISTERED = 'USER_REGISTERED'

# =========================================
# Album Event Types
# =========================================
ALBUM_CREATED = 'album_created'
ALBUM_UPDATED = 'album_updated'
ALBUM_DELETED = 'album_deleted'

# =========================================
# Comment Event Types
# =========================================
COMMENT_CREATED = 'comment_created'
COMMENT_UPDATED = 'comment_updated'
COMMENT_DELETED = 'comment_deleted'

# =========================================
# Follow Event Types
# =========================================
FOLLOW_CREATED = 'follow_created'
FOLLOW_DELETED = 'follow_deleted'

# =========================================
# Friend Event Types
# =========================================
FRIEND_ADDED = 'friend_added'
FRIEND_REMOVED = 'friend_removed'
FRIEND_CREATED = 'friend_created'
FRIEND_UPDATED = 'friend_updated'
FRIEND_DELETED = 'friend_deleted'

# =========================================
# Newsfeed Event Types
# =========================================
NEWSFEED_CREATED = 'newsfeed_created'
NEWSFEED_UPDATED = 'newsfeed_updated'
NEWSFEED_DELETED = 'newsfeed_deleted'

# =========================================
# Reaction Event Types
# =========================================
REACTION_CREATED = 'reaction_created'
REACTION_UPDATED = 'reaction_updated'
REACTION_DELETED = 'reaction_deleted'
REACTION_ADDED = 'reaction_added'

# =========================================
# Social Event Types
# =========================================
POST_CREATED = 'post_created'
POST_UPDATED = 'post_updated'
POST_DELETED = 'post_deleted'
SOCIAL_ACTION = 'social_action'

# =========================================
# Tagging Event Types
# =========================================
TAGGING_CREATED = 'tagging_created'
TAGGING_DELETED = 'tagging_deleted'
TAG_ADDED = 'tag_added'
TAG_REMOVED = 'tag_removed'

# =========================================
# Photo Event Types
# =========================================
PHOTO_CREATED = 'photo_created'
PHOTO_UPDATED = 'photo_updated'
PHOTO_DELETED = 'photo_deleted'

# =========================================
# Messenger Event Types
# =========================================
MESSAGE_CREATED = 'message_created'
MESSAGE_UPDATED = 'message_updated'
MESSAGE_DELETED = 'message_deleted'
MESSAGE_EVENT = "message_event"


# =========================================
# Story Event Types
# =========================================
STORY_SHARED = 'story_shared'
STORY_CREATED = 'story_created'
STORY_UPDATED = 'story_updated'
STORY_DELETED = 'story_deleted'
STORY_SOFT_DELETED = 'story_soft_deleted'
STORY_RESTORED = 'story_restored'

# =========================================
# Notification Event Types
# =========================================
NOTIFICATION_CREATED = 'notification_created'
NOTIFICATION_UPDATED = 'notification_updated'
NOTIFICATION_DELETED = 'notification_deleted'
NOTIFICATION_SENT = 'NOTIFICATION_SENT'


# =========================================
# Generic Event Types
# =========================================
EVENT_CREATED = 'created'
EVENT_UPDATED = 'updated'
EVENT_DELETED = 'deleted'

# =========================================
# Add other event_type constants as needed
# =========================================

# Email Event Types
WELCOME_EMAIL_SENT = 'WELCOME_EMAIL_SENT'
PROFILE_UPDATE_NOTIFIED = 'PROFILE_UPDATE_NOTIFIED'

