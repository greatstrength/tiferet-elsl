"""DI container contract."""

# *** imports

# ** core
from abc import ABC, abstractmethod

# ** app
from ..domain.error import Error
from ..interfaces.container import ContainerService

# *** classes

# ** class: container
class Container(ABC):
    '''
    Resolve a named service without the caller knowing the binding.
    '''

    # * method: get
    @abstractmethod
    def get(self, name):
        '''
        Resolve one named service.

        :param name: The service name.
        :type name: str
        :return: The resolved service.
        :rtype: object
        '''

        # The container supplies the body. This contract only names the raise.
        raise NotImplementedError('get')

    # * method: has
    @abstractmethod
    def has(self, name):
        '''
        Report whether a name is bound.

        :param name: The service name.
        :type name: str
        :return: True when the name is bound.
        :rtype: bool
        '''

        # The container supplies the body. This contract only names the raise.
        raise NotImplementedError('has')
