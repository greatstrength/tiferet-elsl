"""Error domain models."""

# *** imports

# ** core
from typing import Optional

# ** app
from ..assets.core import ERROR_NOT_FOUND_ID

# *** constants

# ** constant: error_not_found_id
ERROR_NOT_FOUND_ID = 'ERROR_NOT_FOUND'

# *** models

# ** model: error
class Error(DomainObject):
    '''
    A structured error a caller can present without reading a raw exception.
    '''

    # * attribute: code
    code: str = Field(
        ...,
        description='The stable error code.',
    )

    # * attribute: text
    text: Optional[str] = Field(
        None,
        description='The rendered error text.',
    )
