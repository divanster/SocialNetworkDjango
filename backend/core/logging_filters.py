# backend/core/logging_filters.py

import logging
import re


class SensitiveDataFilter(logging.Filter):
    """
    Logging filter to sanitize sensitive data from log records.
    """
    # Define regex patterns for sensitive data
    sensitive_patterns = [
        r'password=\S+',
        r'password1=\S+',
        r'password2=\S+',
        r'token=\S+',
        r'Authorization: Bearer \S+',
        r'SIMPLE_JWT_SIGNING_KEY=\S+',
        # Add other patterns as necessary
    ]

    def filter(self, record):
        if hasattr(record, 'msg'):
            sanitized_msg = record.msg
            for pattern in self.sensitive_patterns:
                sanitized_msg = re.sub(pattern, lambda m: m.group(0).split('=')[0] + '=****', sanitized_msg)
            record.msg = sanitized_msg
        return True
