"""Tiferet error contexts."""

# *** imports

# ** app
from .core import BaseContext
from ..domain.error import Error
from ..assets.error import ERROR_NOT_FOUND_ID

# *** constants

# ** constant: error_cache_prefix
ERROR_CACHE_PREFIX = 'app.errors'

# *** contexts

# ** context: error_context
class ErrorContext(BaseContext):
    '''
    Format a structured error from a loaded error domain object.
    '''

    # * attribute: domain_type
    domain_type = Error

    # * method: format_response
    def format_response(self, error):
        '''
        Format one error response.

        :param error: The loaded error.
        :type error: Error
        :return: The error code.
        :rtype: str
        '''

        # The catalog id names the missing error.
        return ERROR_NOT_FOUND_ID
