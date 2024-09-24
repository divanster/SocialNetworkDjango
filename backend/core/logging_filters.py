# core/logging_filters.py

import logging


class SensitiveDataFilter(logging.Filter):
    SENSITIVE_FIELDS = {'password', 'password1', 'password2'}

    def filter(self, record):
        if hasattr(record, 'msg'):
            sanitized_msg = record.msg
            for field in self.SENSITIVE_FIELDS:
                if field in sanitized_msg:
                    sanitized_msg = sanitized_msg.replace(
                        sanitized_msg.split(field + '=')[1].split()[0], '****'
                    )
            record.msg = sanitized_msg
        return True
