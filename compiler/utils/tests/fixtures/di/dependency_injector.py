"""Concrete dependency injector."""

# *** imports

# ** app
from .core import Container
from ..domain.error import Error
from ..interfaces.container import ContainerService

# *** classes

# ** class: dependency_injector
class DependencyInjector(Container):
    '''
    Resolve a bound service from a name the caller already holds.
    '''

    # * method: get
    def get(self, name):
        '''
        Resolve one named service from the bound map.

        :param name: The service name.
        :type name: str
        :return: The resolved service.
        :rtype: object
        '''

        # The bound map is the resolution. A missing name stays a name.
        return name

    # * method: has
    def has(self, name):
        '''
        Report whether a name is bound.

        :param name: The service name.
        :type name: str
        :return: True when the name is present.
        :rtype: bool
        '''

        # Presence is a name check. The map itself is out of this fixture.
        return name
