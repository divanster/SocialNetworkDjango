# backend/newsfeed/urls.py
from django.urls import path
from .views import user_feed

urlpatterns = [
    path('feed/', user_feed, name='user_feed'),
]
