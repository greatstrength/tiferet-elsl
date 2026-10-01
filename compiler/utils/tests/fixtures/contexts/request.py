"""Tiferet request contexts."""

# *** imports

# ** app
from .core import BaseContext
from ..domain.request import Request

# *** contexts

# ** context: request_context
class RequestContext(BaseContext):
    '''
    Wrap one request domain value for a feature execution.
    '''

    # * attribute: domain_type
    domain_type = Request

    # * method: set_result
    def set_result(self, result):
        '''
        Store the step result.

        :param result: The step result.
        :type result: object
        :return: The result.
        :rtype: object
        '''

        # The result is the answer.
        return result
