"""Tests - TiferetLexer (tiferet-ly adapter)"""

# *** imports

# ** infra
import pytest
from tiferet_ly.repos.grammar import GrammarConfigRepository
from tiferet_ly.repos.token import TokenConfigRepository

# ** app
from ... import assets as a
from ...interfaces import LexerService
from ..lexer import TiferetLexer

# *** constants

# ** constant: token_yaml_file
TOKEN_YAML_FILE = 'compiler/assets/tokens.yml'

# ** constant: grammar_yaml_file
GRAMMAR_YAML_FILE = 'compiler/assets/grammars.yml'

# ** constant: sample_source
SAMPLE_SOURCE = '''"""Arithmetic events for the Tiferet dialect."""

# *** imports

# ** infra
from tiferet.events import DomainEvent

# *** events

# ** event: add
class Add(DomainEvent):
    """
    Add two integers.

    The sum is the result of applying addition to the two operands.
    """

    # * method: execute
    def execute(self, a: int, b: int) -> int:
        """
        Add the operands.

        :param a: The first operand.
        :type a: int
        :param b: The second operand.
        :type b: int
        :return: The sum.
        :rtype: int
        """

        # Return the sum of the two operands.
        return a + b

# ** event: subtract
class Subtract(DomainEvent):
    """
    Subtract one integer from another.

    The difference is the result of applying subtraction to the two operands.
    """

    # * method: execute
    def execute(self, a: int, b: int) -> int:
        """
        Subtract the operands.

        :param a: The first operand.
        :type a: int
        :param b: The second operand.
        :type b: int
        :return: The difference.
        :rtype: int
        """

        # Return the difference of the two operands.
        return a - b

# ** event: multiply
class Multiply(DomainEvent):
    """
    Multiply two integers.

    The product is the result of applying multiplication to the two operands.
    """

    # * method: execute
    def execute(self, a: int, b: int) -> int:
        """
        Multiply the operands.

        :param a: The first operand.
        :type a: int
        :param b: The second operand.
        :type b: int
        :return: The product.
        :rtype: int
        """

        # Return the product of the two operands.
        return a * b

# ** event: divide
class Divide(DomainEvent):
    """
    Divide one integer by another.

    The quotient is the result of applying division to the two operands.
    """

    # * method: execute
    def execute(self, a: int, b: int) -> int:
        """
        Divide the operands.

        :param a: The first operand.
        :type a: int
        :param b: The second operand.
        :type b: int
        :return: The quotient.
        :rtype: int
        """

        # Return the quotient of the two operands.
        return a / b

# ** event: modulus
class Modulus(DomainEvent):
    """
    Compute the remainder of two integers.

    The remainder is the result of applying modulus to the two operands.
    """

    # * method: execute
    def execute(self, a: int, b: int) -> int:
        """
        Compute the remainder.

        :param a: The first operand.
        :type a: int
        :param b: The second operand.
        :type b: int
        :return: The remainder.
        :rtype: int
        """

        # Return the remainder of the two operands.
        return a % b

# ** event: exponentiate
class Exponentiate(DomainEvent):
    """
    Raise one integer to the power of another.

    The power is the result of applying exponentiation to the two operands.
    """

    # * method: execute
    def execute(self, a: int, b: int) -> int:
        """
        Raise the first operand to the power of the second.

        :param a: The first operand.
        :type a: int
        :param b: The second operand.
        :type b: int
        :return: The power.
        :rtype: int
        """

        # Return the first operand raised to the second.
        return a ** b
'''

# *** fixtures

# ** fixture: tokens
@pytest.fixture(scope='module')
def tokens():
    '''
    Load the declared token catalogue.

    :return: The token rules from tokens.yml.
    :rtype: list
    '''

    # Load through the tiferet-ly token configuration repository.
    return TokenConfigRepository(token_config=TOKEN_YAML_FILE).list()

# ** fixture: grammars
@pytest.fixture(scope='module')
def grammars():
    '''
    Load the declared grammar catalogue.

    :return: The grammars from grammars.yml.
    :rtype: list
    '''

    # Load through the tiferet-ly grammar configuration repository.
    return GrammarConfigRepository(grammar_config=GRAMMAR_YAML_FILE).list()

# ** fixture: sample_text
@pytest.fixture
def sample_text() -> str:
    '''
    Provide a Tiferet events module covering six arithmetic operators.

    :return: The sample source text.
    :rtype: str
    '''

    # Return the module that the full-tokenize cases scan.
    return SAMPLE_SOURCE

# *** tests

# ** test: tiferet_lexer_full_tokenize_includes_indents
def test_tiferet_lexer_full_tokenize_includes_indents(sample_text, tokens, grammars) -> None:
    '''
    Test that a full scan injects indent and dedent and exceeds 200 tokens.

    :param sample_text: The arithmetic events module.
    :type sample_text: str
    :param tokens: The declared token catalogue.
    :type tokens: list
    :param grammars: The declared grammar catalogue.
    :type grammars: list
    '''

    # Scan with layout enabled.
    result = TiferetLexer().tokenize(sample_text, tokens, grammars)
    types = [token.type for token in result]

    # Indent and dedent are present, and the stream is longer than 200 tokens.
    assert a.lexer.INDENT in types
    assert a.lexer.DEDENT in types
    assert len(result) > 200

# ** test: tiferet_lexer_empty_text
def test_tiferet_lexer_empty_text(tokens, grammars) -> None:
    '''
    Test that empty text tokenizes to a list.

    :param tokens: The declared token catalogue.
    :type tokens: list
    :param grammars: The declared grammar catalogue.
    :type grammars: list
    '''

    # An empty source is a list, possibly empty.
    result = TiferetLexer().tokenize('', tokens, grammars)
    assert isinstance(result, list)
    assert len(result) >= 0

# ** test: lexer_preserves_original_tokens
def test_lexer_preserves_original_tokens(sample_text, tokens, grammars) -> None:
    '''
    Test that layout injection does not drop the original token types.

    :param sample_text: The arithmetic events module.
    :type sample_text: str
    :param tokens: The declared token catalogue.
    :type tokens: list
    :param grammars: The declared grammar catalogue.
    :type grammars: list
    '''

    # Drop synthetic indent markers before checking the original types.
    result = TiferetLexer().tokenize(sample_text, tokens, grammars)
    types = {
        token.type
        for token in result
        if token.type not in (a.lexer.INDENT, a.lexer.DEDENT)
    }

    # The structural types from the sample remain.
    assert a.lexer.CLASS in types
    assert a.lexer.ARTIFACT_MEMBER in types
    assert a.lexer.DEF in types
    assert a.lexer.NEWLINE in types
    assert a.lexer.IDENTIFIER in types

# ** test: lexer_respects_include_indent_dedent_flag
def test_lexer_respects_include_indent_dedent_flag(sample_text, tokens, grammars) -> None:
    '''
    Test that layout injection can be turned off.

    :param sample_text: The arithmetic events module.
    :type sample_text: str
    :param tokens: The declared token catalogue.
    :type tokens: list
    :param grammars: The declared grammar catalogue.
    :type grammars: list
    '''

    # Scan the same module with layout disabled.
    result = TiferetLexer(include_indent_dedent=False).tokenize(
        sample_text,
        tokens,
        grammars,
    )
    types = {token.type for token in result}

    # Neither indent nor dedent is emitted.
    assert a.lexer.INDENT not in types
    assert a.lexer.DEDENT not in types

# ** test: lexer_adds_final_newline_if_missing
def test_lexer_adds_final_newline_if_missing(tokens, grammars) -> None:
    '''
    Test that a source missing a trailing newline still ends on NEWLINE.

    :param tokens: The declared token catalogue.
    :type tokens: list
    :param grammars: The declared grammar catalogue.
    :type grammars: list
    '''

    # A class header with no newline still ends on NEWLINE.
    result = TiferetLexer().tokenize('class Foo:', tokens, grammars)
    assert result[-1].type == a.lexer.NEWLINE

# ** test: lexer_tokenizes_see_annotation
def test_lexer_tokenizes_see_annotation(tokens, grammars) -> None:
    '''
    Test that a see annotation is a SEE token carrying the guide path.

    :param tokens: The declared token catalogue.
    :type tokens: list
    :param grammars: The declared grammar catalogue.
    :type grammars: list
    '''

    # Scan a see annotation with layout off.
    result = TiferetLexer(include_indent_dedent=False).tokenize(
        '# >> see: @guides/domain/error.md#error',
        tokens,
        grammars,
    )
    see_tokens = [token for token in result if token.type == a.lexer.SEE]

    # The guide path is part of the SEE value.
    assert see_tokens
    assert '@guides/domain/error.md#error' in see_tokens[0].value

# ** test: lexer_implements_lexer_service
def test_lexer_implements_lexer_service() -> None:
    '''
    Test that the adapter is a LexerService.
    '''

    # The adapter satisfies the lexer service contract.
    assert isinstance(TiferetLexer(), LexerService)

# ** test: lexer_indent_dedent_values_are_empty_string
def test_lexer_indent_dedent_values_are_empty_string(sample_text, tokens, grammars) -> None:
    '''
    Test that injected indent and dedent values are empty strings.

    :param sample_text: The arithmetic events module.
    :type sample_text: str
    :param tokens: The declared token catalogue.
    :type tokens: list
    :param grammars: The declared grammar catalogue.
    :type grammars: list
    '''

    # Collect every injected layout token.
    result = TiferetLexer().tokenize(sample_text, tokens, grammars)
    layout_tokens = [
        token
        for token in result
        if token.type in (a.lexer.INDENT, a.lexer.DEDENT)
    ]

    # Each injected value is an empty string, not None.
    assert layout_tokens
    assert all(token.value == '' for token in layout_tokens)

# ** test: lexer_drops_trailing_inline_comment
def test_lexer_drops_trailing_inline_comment(tokens, grammars) -> None:
    '''
    Test that a trailing inline comment is dropped and a standalone comment is kept.

    :param tokens: The declared token catalogue.
    :type tokens: list
    :param grammars: The declared grammar catalogue.
    :type grammars: list
    '''

    # An inline noqa comment is not a line-starting comment.
    inline = TiferetLexer(include_indent_dedent=False).tokenize(
        'return x  # noqa: S307',
        tokens,
        grammars,
    )
    assert a.lexer.LINE_COMMENT not in [token.type for token in inline]

    # A comment on its own line is kept.
    standalone = TiferetLexer(include_indent_dedent=False).tokenize(
        '# comment',
        tokens,
        grammars,
    )
    assert a.lexer.LINE_COMMENT in [token.type for token in standalone]

# ** test: block_tracker_absent
def test_block_tracker_absent() -> None:
    '''
    Test that the adapter module does not define BlockTracker.
    '''

    # Import the module and assert the removed tracker is absent.
    import compiler.utils.lexer as lexer_module
    assert not hasattr(lexer_module, 'BlockTracker')
