# backend/core/throttling.py

from rest_framework.throttling import UserRateThrottle


class StandardUserThrottle(UserRateThrottle):
    scope = 'user'


class BurstUserThrottle(UserRateThrottle):
    scope = 'burst_user'
