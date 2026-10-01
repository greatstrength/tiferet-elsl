"""Tiferet interfaces error."""

# *** imports

# ** app
from ..mappers.error import Error
from .core import Service

# *** interfaces

# ** interface: error_service
class ErrorService(Service):
    '''
    Load a catalogued error without the caller reading the store.
    '''

    # * method: get
    @abstractmethod
    def get(self, code: str):
        '''
        Retrieve one catalogued error.

        :param code: The error code.
        :type code: str
        :return: The error.
        :rtype: Error
        '''

        # The implementation supplies the body.
        raise NotImplementedError('get')
