# backend/core/signals.py

from django.dispatch import Signal

# Define custom signals for soft deletion and restoration
soft_delete = Signal()
restore = Signal()
