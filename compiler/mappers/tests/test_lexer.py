"""Mappers - Lexer Mapper Objects Tests"""

# *** imports

# ** infra
import pytest
from pydantic import ValidationError
from tiferet_ly.mappers.lexeme import LexemeAggregate

# ** app
from ...domain import Token
from ..lexer import TokenAggregate

# *** fixtures

# ** fixture: minimal_token_aggregate
@pytest.fixture
def minimal_token_aggregate() -> TokenAggregate:
    '''
    Fixture for a minimal identifier token aggregate.

    :return: The token aggregate.
    :rtype: TokenAggregate
    '''

    # Create and return a minimal identifier token aggregate.
    return TokenAggregate.new(
        type='IDENTIFIER',
        value='error_service',
        lineno=42,
        lexpos=156,
    )

# ** fixture: artifact_token_aggregate
@pytest.fixture
def artifact_token_aggregate() -> TokenAggregate:
    '''
    Fixture for an artifact-member token aggregate.

    :return: The token aggregate.
    :rtype: TokenAggregate
    '''

    # Create and return an artifact-member token aggregate.
    return TokenAggregate.new(
        type='ARTIFACT_MEMBER',
        value='# * method: execute',
        lineno=17,
        lexpos=289,
    )

# *** tests

# ** test: token_aggregate_creation_via_new
def test_token_aggregate_creation_via_new(
        minimal_token_aggregate: TokenAggregate,
        artifact_token_aggregate: TokenAggregate,
) -> None:
    '''
    Test that both fixtures store the four token fields.

    :param minimal_token_aggregate: The minimal identifier fixture.
    :type minimal_token_aggregate: TokenAggregate
    :param artifact_token_aggregate: The artifact-member fixture.
    :type artifact_token_aggregate: TokenAggregate
    '''

    # Assert the minimal identifier token fields.
    assert minimal_token_aggregate.type == 'IDENTIFIER'
    assert minimal_token_aggregate.value == 'error_service'
    assert minimal_token_aggregate.lineno == 42
    assert minimal_token_aggregate.lexpos == 156

    # Assert the artifact-member token fields.
    assert artifact_token_aggregate.type == 'ARTIFACT_MEMBER'
    assert artifact_token_aggregate.value == '# * method: execute'
    assert artifact_token_aggregate.lineno == 17
    assert artifact_token_aggregate.lexpos == 289

# ** test: token_aggregate_inherits_from_token
def test_token_aggregate_inherits_from_token() -> None:
    '''
    Test that a token aggregate is a Token.
    '''

    # Construct a token aggregate and assert the domain type.
    aggregate = TokenAggregate.new(
        type='IDENTIFIER',
        value='error_service',
        lineno=42,
        lexpos=156,
    )
    assert isinstance(aggregate, Token)

# ** test: token_aggregate_new_requires_all_params
def test_token_aggregate_new_requires_all_params() -> None:
    '''
    Test that new requires every span field and rejects null positions.
    '''

    # Omitting lexpos is a call-signature error.
    with pytest.raises(TypeError):
        TokenAggregate.new(
            type='IDENTIFIER',
            value='error_service',
            lineno=42,
        )

    # Null positions fail field validation.
    with pytest.raises(ValidationError):
        TokenAggregate.new(
            type='IDENTIFIER',
            value='error_service',
            lineno=None,
            lexpos=None,
        )

# ** test: token_aggregate_column_default
def test_token_aggregate_column_default(minimal_token_aggregate: TokenAggregate) -> None:
    '''
    Test that a token aggregate has no column attribute.

    :param minimal_token_aggregate: The minimal identifier fixture.
    :type minimal_token_aggregate: TokenAggregate
    '''

    # Column is not part of the token span.
    assert hasattr(minimal_token_aggregate, 'column') is False

# ** test: token_aggregate_mutation
def test_token_aggregate_mutation(minimal_token_aggregate: TokenAggregate) -> None:
    '''
    Test that assigning type and value persists.

    :param minimal_token_aggregate: The minimal identifier fixture.
    :type minimal_token_aggregate: TokenAggregate
    '''

    # Reassign the mutable type and value fields.
    minimal_token_aggregate.type = 'KEYWORD'
    minimal_token_aggregate.value = 'class'

    # Assert the assignments persisted.
    assert minimal_token_aggregate.type == 'KEYWORD'
    assert minimal_token_aggregate.value == 'class'

# ** test: token_aggregate_with_edge_values
def test_token_aggregate_with_edge_values() -> None:
    '''
    Test that new stores empty text at the start of the input.
    '''

    # Construct a newline token at the origin of the source text.
    aggregate = TokenAggregate.new(
        type='NEWLINE',
        value='',
        lineno=1,
        lexpos=0,
    )

    # Assert the edge values are stored unchanged.
    assert aggregate.type == 'NEWLINE'
    assert aggregate.value == ''
    assert aggregate.lineno == 1
    assert aggregate.lexpos == 0

# ** test: token_aggregate_with_long_value
def test_token_aggregate_with_long_value() -> None:
    '''
    Test that new stores a multi-word ARTIFACT_MEMBER value unchanged.
    '''

    # Construct a token with a multi-word artifact-member value.
    long_value = '# * method: format_message for the specified language'
    aggregate = TokenAggregate.new(
        type='ARTIFACT_MEMBER',
        value=long_value,
        lineno=10,
        lexpos=100,
    )

    # Assert the long value is stored unchanged.
    assert aggregate.type == 'ARTIFACT_MEMBER'
    assert aggregate.value == long_value

# ** test: token_aggregate_new_indent
def test_token_aggregate_new_indent() -> None:
    '''
    Test that new_indent synthesizes an empty INDENT token.
    '''

    # Synthesize an indent at the given position.
    aggregate = TokenAggregate.new_indent(lineno=10, lexpos=4)

    # Assert the indent type, empty value, and position.
    assert aggregate.type == 'INDENT'
    assert aggregate.value == ''
    assert aggregate.lineno == 10
    assert aggregate.lexpos == 4

# ** test: token_aggregate_new_dedent
def test_token_aggregate_new_dedent() -> None:
    '''
    Test default and explicit dedent positions.
    '''

    # The default dedent is an empty marker at the origin.
    default_aggregate = TokenAggregate.new_dedent()
    assert default_aggregate.type == 'DEDENT'
    assert default_aggregate.value == ''
    assert default_aggregate.lineno == 0
    assert default_aggregate.lexpos == 0

    # Explicit positions persist.
    explicit_aggregate = TokenAggregate.new_dedent(lineno=9, lexpos=12)
    assert explicit_aggregate.type == 'DEDENT'
    assert explicit_aggregate.value == ''
    assert explicit_aggregate.lineno == 9
    assert explicit_aggregate.lexpos == 12

# ** test: token_aggregate_from_lexeme
def test_token_aggregate_from_lexeme() -> None:
    '''
    Test that from_lexeme copies the four span fields.
    '''

    # Synthesize a lexeme and copy it into a token aggregate.
    lexeme = LexemeAggregate.synthesize(
        type='IDENTIFIER',
        lineno=3,
        lexpos=7,
        value='error_service',
    )
    aggregate = TokenAggregate.from_lexeme(lexeme)

    # Assert the four span fields were copied.
    assert aggregate.type == lexeme.type
    assert aggregate.value == lexeme.value
    assert aggregate.lineno == lexeme.lineno
    assert aggregate.lexpos == lexeme.lexpos

# ** test: token_aggregate_to_lexeme
def test_token_aggregate_to_lexeme(minimal_token_aggregate: TokenAggregate) -> None:
    '''
    Test that to_lexeme round-trips the four span fields.

    :param minimal_token_aggregate: The minimal identifier fixture.
    :type minimal_token_aggregate: TokenAggregate
    '''

    # Convert the token aggregate into a lexeme.
    lexeme = minimal_token_aggregate.to_lexeme()

    # Assert the four span fields round-trip through LexemeAggregate.
    assert isinstance(lexeme, LexemeAggregate)
    assert lexeme.type == minimal_token_aggregate.type
    assert lexeme.value == minimal_token_aggregate.value
    assert lexeme.lineno == minimal_token_aggregate.lineno
    assert lexeme.lexpos == minimal_token_aggregate.lexpos
