"""Tiferet interfaces core."""

# *** imports

# ** core
from abc import ABC

# *** classes

# ** class: service_error
class ServiceError(Exception):
    '''
    An infrastructural failure that is not a domain outcome.
    '''

    # * method: _format
    def _format(self):
        '''
        Format the error for a private caller.

        :return: The formatted text.
        :rtype: str
        '''

        # The private formatter returns the class name.
        return 'ServiceError'

# *** interfaces

# ** interface: service
class Service(ABC):
    '''
    The root marker every infrastructure contract extends.
    '''

    pass
