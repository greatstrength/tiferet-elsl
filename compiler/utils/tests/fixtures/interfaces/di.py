"""Tiferet interfaces DI."""

# *** imports

# ** app
from .core import Service

# *** interfaces

# ** interface: container_service
class ContainerService(Service):
    '''
    Resolve a named service without the caller knowing the binding.
    '''

    # * method: get
    @abstractmethod
    def get(self, name: str):
        '''
        Resolve one named service.

        :param name: The service name.
        :type name: str
        :return: The resolved service.
        :rtype: object
        '''

        # The implementation supplies the body.
        raise NotImplementedError('get')
