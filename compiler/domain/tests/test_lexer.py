"""Domain – Lexer Domain Objects Tests"""

# *** imports

# ** infra
import pytest
from pydantic import ValidationError

# ** app
from ..lexer import Token

# *** fixtures

# ** fixture: minimal_token
@pytest.fixture
def minimal_token() -> Token:
    '''
    Fixture for a minimal identifier token.

    :return: The Token instance.
    :rtype: Token
    '''

    # Create and return a minimal identifier token.
    return Token(type='IDENTIFIER', value='error_service', lineno=42, lexpos=156)

# ** fixture: artifact_token
@pytest.fixture
def artifact_token() -> Token:
    '''
    Fixture for an artifact-member token.

    :return: The Token instance.
    :rtype: Token
    '''

    # Create and return an artifact-member token.
    return Token(type='ARTIFACT_MEMBER', value='# * method: execute', lineno=17, lexpos=289)

# *** tests

# ** test: token_creation_and_access
def test_token_creation_and_access(minimal_token: Token, artifact_token: Token) -> None:
    '''
    Test that both fixtures expose the four token attributes with the expected values.

    :param minimal_token: The minimal identifier token fixture.
    :type minimal_token: Token
    :param artifact_token: The artifact-member token fixture.
    :type artifact_token: Token
    '''

    # Assert the minimal identifier token attributes.
    assert minimal_token.type == 'IDENTIFIER'
    assert minimal_token.value == 'error_service'
    assert minimal_token.lineno == 42
    assert minimal_token.lexpos == 156

    # Assert the artifact-member token attributes.
    assert artifact_token.type == 'ARTIFACT_MEMBER'
    assert artifact_token.value == '# * method: execute'
    assert artifact_token.lineno == 17
    assert artifact_token.lexpos == 289

# ** test: token_field_validation
def test_token_field_validation() -> None:
    '''
    Test that omitting any one required field raises ValidationError.
    '''

    # Define a complete set of required token fields.
    complete = dict(
        type='IDENTIFIER',
        value='error_service',
        lineno=42,
        lexpos=156,
    )

    # Omitting any one required field must raise ValidationError.
    for field in ('type', 'value', 'lineno', 'lexpos'):
        data = dict(complete)
        data.pop(field)
        with pytest.raises(ValidationError):
            Token(**data)

# ** test: token_rejects_unknown_fields
def test_token_rejects_unknown_fields() -> None:
    '''
    Test that constructing Token with an undeclared field raises ValidationError.
    '''

    # Constructing with an undeclared column field must raise ValidationError.
    with pytest.raises(ValidationError):
        Token(
            type='IDENTIFIER',
            value='error_service',
            lineno=42,
            lexpos=156,
            column=8,
        )

# ** test: token_with_edge_values
def test_token_with_edge_values() -> None:
    '''
    Test that Token stores empty text at the start of the input.
    '''

    # Construct a newline token at the origin of the source text.
    token = Token(type='NEWLINE', value='', lineno=1, lexpos=0)

    # Assert the edge values are stored unchanged.
    assert token.type == 'NEWLINE'
    assert token.value == ''
    assert token.lineno == 1
    assert token.lexpos == 0

# ** test: token_with_long_value
def test_token_with_long_value() -> None:
    '''
    Test that Token stores a multi-word ARTIFACT_MEMBER value unchanged.
    '''

    # Construct a token with a multi-word artifact-member value.
    long_value = '# * method: format_message for the specified language'
    token = Token(
        type='ARTIFACT_MEMBER',
        value=long_value,
        lineno=10,
        lexpos=100,
    )

    # Assert the long value is stored unchanged.
    assert token.type == 'ARTIFACT_MEMBER'
    assert token.value == long_value
    assert token.lineno == 10
    assert token.lexpos == 100
