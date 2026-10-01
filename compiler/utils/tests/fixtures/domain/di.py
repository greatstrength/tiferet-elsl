"""Dependency registration domain models."""

# *** imports

# ** app
from .error import Error
from ..assets.core import DI_BINDING_ID

# *** models

# ** model: binding
class Binding(DomainObject):
    '''
    A named service binding the domain can describe without constructing it.
    '''

    # * attribute: name
    name: str = Field(
        ...,
        description='The binding name.',
    )

    # * attribute: service_name
    service_name: str = Field(
        ...,
        description='The service type name this binding resolves.',
    )
