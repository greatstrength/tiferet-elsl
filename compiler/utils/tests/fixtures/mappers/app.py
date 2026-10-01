"""Tiferet app mappers."""

# *** imports

# ** core
from typing import Any, ClassVar, Dict

# ** app
from ..domain.app import App
from .core import Aggregate

# *** constants

# ** constant: app_role
APP_ROLE = 'app'

# *** mappers

# ** mapper: app_aggregate
class AppAggregate(App, Aggregate):
    '''
    A mutable app session the caller can save without touching the store.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {'exclude': {'type'}},
        'to_data': {'by_alias': True},
    }

    # * method: set_name
    def set_name(self, name: str) -> None:
        '''
        Set the app name.

        :param name: The app name.
        :type name: str
        :return: None
        :rtype: None
        '''

        # Store the name on the aggregate.
        self.name = name
