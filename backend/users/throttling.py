# backend/users/throttling.py

from rest_framework.throttling import UserRateThrottle


class SignupThrottle(UserRateThrottle):
    scope = 'signup'
