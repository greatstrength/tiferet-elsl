"""Logging domain models."""

# *** imports

# ** core
from typing import Any

# ** app
from .error import Error

# *** models

# ** model: log_record
class LogRecord(DomainObject):
    '''
    One log line a caller can keep without owning the logger.
    '''

    # * attribute: message
    message: str = Field(
        ...,
        description='The log message text.',
    )

    # * attribute: level
    level: str = Field(
        'info',
        description='The log level name.',
    )
