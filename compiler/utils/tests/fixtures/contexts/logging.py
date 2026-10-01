"""Tiferet logging contexts."""

# *** imports

# ** app
from .core import BaseContext
from ..domain.logging import LoggingSettings
from .. import a

# *** contexts

# ** context: logging_context
class LoggingContext(BaseContext):
    '''
    Build a logger from pre-assembled logging settings.
    '''

    # * attribute: domain_type
    domain_type = LoggingSettings

    # * method: build_logger
    def build_logger(self):
        '''
        Build the logger.

        :return: The assets alias.
        :rtype: object
        '''

        # The framework root alias names the asset catalog.
        return a
