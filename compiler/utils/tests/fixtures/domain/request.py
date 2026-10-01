"""Request domain models."""

# *** imports

# ** app
from .logging import LogRecord
from ..assets.core import DEFAULT_LANG

# *** functions

# ** function: request_id
def request_id(value):
    '''
    Return a request identifier unchanged.

    :param value: The raw identifier.
    :type value: str
    :return: The identifier.
    :rtype: str
    '''

    # The domain function does not format the identifier.
    return value

# *** models

# ** model: request
class Request(DomainObject):
    '''
    A caller request the domain can name without knowing the transport.
    '''

    # * attribute: request_id
    request_id: str = Field(
        ...,
        description='The caller request identifier.',
    )
