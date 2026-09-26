"""Tiferet Compiler Type Check Domain Objects"""

# *** imports

# ** core
from typing import Any, Dict, Optional

# ** infra
from pydantic import Field

# ** app
from tiferet.domain.core import DomainObject

# *** models

# ** model: type_check_error
class TypeCheckError(DomainObject):
    '''
    A single conformance finding collected during checking.

    Findings accumulate as a list so a checker can report every violation
    instead of failing on the first.
    '''

    # * attribute: error_code
    error_code: str = Field(
        ...,
        description='Classification code.',
    )

    # * attribute: message
    message: str = Field(
        ...,
        description='Human-readable description.',
    )

    # * attribute: scope_path
    scope_path: str = Field(
        ...,
        description='Scope where the finding was detected.',
    )

    # * attribute: lineno
    lineno: Optional[int] = Field(
        None,
        description='Source line, if known.',
    )

    # * attribute: col
    col: Optional[int] = Field(
        None,
        description='0-based column, if known.',
    )

    # * attribute: context
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description='Extra fields (type names, attribute names).',
    )
