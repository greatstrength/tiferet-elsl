"""Tiferet Compiler Lexer Domain Objects"""

# *** imports

# ** infra
from pydantic import Field

# ** app
from tiferet.domain.core import DomainObject

# *** models

# ** model: token
class Token(DomainObject):
    '''
    A token is the smallest recognized unit of Tiferet source text.
    '''

    # * attribute: type
    type: str = Field(
        ...,
        description='Token type name (e.g. `IDENTIFIER`, `KEYWORD`, `ARTIFACT_MEMBER`)',
    )

    # * attribute: value
    value: str = Field(..., description='Token text')

    # * attribute: lineno
    lineno: int = Field(..., description='1-based source line')

    # * attribute: lexpos
    lexpos: int = Field(..., description='0-based offset in the input text')
