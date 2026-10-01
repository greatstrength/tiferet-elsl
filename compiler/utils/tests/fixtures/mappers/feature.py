"""Tiferet feature mappers."""

# *** imports

# ** core
from typing import Any, ClassVar, Dict

# ** app
from ..domain.feature import Feature
from ..events.feature import CompileFeature

# *** mappers

# ** mapper: feature_aggregate
class FeatureAggregate(Feature):
    '''
    A mutable feature the caller can extend without reading the store.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {'exclude': {'type'}},
    }

    # * method: add_step
    def add_step(self, name: str) -> None:
        '''
        Add one named step.

        :param name: The step name.
        :type name: str
        :return: None
        :rtype: None
        '''

        # Record the step name. The event import names the compile boundary.
        self.name = name
        return CompileFeature
