"""Tiferet DI mappers."""

# *** imports

# ** core
from typing import Any, ClassVar, Dict

# ** app
from ..domain.di import Binding
from .app import AppAggregate

# *** mappers

# ** mapper: binding_aggregate
class BindingAggregate(Binding):
    '''
    A mutable service binding the container can register.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_data': {'exclude': {'secret'}},
    }

    # * method: set_name
    def set_name(self, name: str) -> None:
        '''
        Set the binding name.

        :param name: The binding name.
        :type name: str
        :return: None
        :rtype: None
        '''

        # Store the name on the aggregate.
        self.name = name
