"""Tests - TiferetLexer (tiferet-ly adapter)"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest

# ** app
from ... import assets as a
from .parser_test_helpers import (
    load_grammar_rules,
    load_production_rules,
    load_token_rules,
)
from ...blueprints.core import build_cache
from ...contexts.provision import COMPILER_PROVISION_CACHE_PREFIX
from ...interfaces import LexerService
from ...mappers.transfer import DeclarationTransferObject
from .. import lexer as lexer_module
from ..lexer import TiferetLexer
from ..parser import TiferetParser
from ..semantic import SymbolTableBuilder
from ..typecheck import ConformanceChecker

# *** constants

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

# ** constant: comment_probe
COMMENT_PROBE = '''\"\"\"Gap 12 probe\"\"\"

# *** functions

# ** function: probe
def probe(x: int) -> int:
    \'\'\'
    Return x.

    :param x: The value.
    :type x: int
    :return: The value.
    :rtype: int
    \'\'\'

    # Copy the value.
    y = x
{indent}# A comment inside the body.
    return y
'''

# ** constant: comment_probe_lineno
COMMENT_PROBE_LINENO = 18

# ** constant: nested_probe
NESTED_PROBE = '''\"\"\"Nested probe\"\"\"

# *** functions

# ** function: probe
def probe(x: int) -> int:
    \'\'\'
    Return x.
    \'\'\'

    # Branch on the value.
    if x:
        y = 1
# A commented-out line at column 0.
        y = 2
    else:
        y = 3
    return y
'''

# ** constant: trailing_probe
TRAILING_PROBE = '''\"\"\"Trailing probe\"\"\"

# *** functions

# ** function: probe
def probe(x: int) -> int:
    \'\'\'
    Return x.
    \'\'\'

    # Return the value.
    return x
# A last line at column 0 inside the block.'''

# ** constant: delimiter_probe
DELIMITER_PROBE = '''\"\"\"Delimiter probe\"\"\"

# *** functions

# ** function: probe
def probe(x: int) -> int:
    \'\'\'
    Return x.
    \'\'\'

    # Call inside open delimiters.
    y = max(
        # An indented comment inside the call.
        x,
# A column-0 comment inside the call.
        1,
    )
    return y
'''

# ** constant: fixtures_dir
_FIXTURES_DIR = Path(__file__).resolve().parent / 'fixtures'

# *** functions

# ** function: _drop_line
def _drop_line(text: str, lineno: int) -> str:
    '''
    Remove one 1-based line from a source text.

    :param text: The source text.
    :type text: str
    :param lineno: The 1-based line to remove.
    :type lineno: int
    :return: The text without that line.
    :rtype: str
    '''

    # Keep line endings so every other line keeps its text.
    lines = text.splitlines(keepends=True)
    return ''.join(lines[:lineno - 1] + lines[lineno:])

# ** function: _skeleton
def _skeleton(stream: list) -> list:
    '''
    Return the token types of a stream with standalone comment lines removed.

    Layout tokens stay, so two skeletons are equal only when every indent and
    dedent sits between the same code tokens.

    :param stream: The token aggregates.
    :type stream: list
    :return: The token types without comment lines.
    :rtype: list
    '''

    # Drop each line comment and the newline that ends it.
    types = []
    skip_newline = False
    for token in stream:
        if token.type == a.lexer.LINE_COMMENT:
            skip_newline = True
            continue
        if skip_newline and token.type == a.lexer.NEWLINE:
            skip_newline = False
            continue
        skip_newline = False
        types.append(token.type)
    return types

# ** function: _parse
def _parse(text: str, tokens: list, grammars: list):
    '''
    Tokenize and parse a source text with the declared catalogues.

    :param text: The source text.
    :type text: str
    :param tokens: The declared token catalogue.
    :type tokens: list
    :param grammars: The declared grammar catalogue.
    :type grammars: list
    :return: The root module AST.
    :rtype: Any
    '''

    # Layout runs in the lexer. The parser receives tokens only.
    stream = TiferetLexer().tokenize(text, tokens, grammars)
    return TiferetParser().parse(
        'probe',
        stream,
        grammars,
        tokens,
        load_production_rules(),
        source_text=text,
    )

# ** function: _masked_ast
def _masked_ast(ast, lineno: int) -> dict:
    '''
    Return the emitted AST with the column of one line's nodes removed.

    :param ast: The root module AST.
    :type ast: Any
    :param lineno: The line whose node columns are masked.
    :type lineno: int
    :return: The primitive AST without those columns.
    :rtype: dict
    '''

    # Walk the primitive form the parse emit writes.
    def mask(node):
        if isinstance(node, dict):
            return {
                key: mask(value)
                for key, value in node.items()
                if not (key == 'col' and node.get('lineno') == lineno)
            }
        if isinstance(node, list):
            return [mask(item) for item in node]
        return node

    # Mask the comment node only. Every other column stays compared.
    return mask(DeclarationTransferObject.from_model(ast).to_primitive())

# ** function: _findings
def _findings(ast) -> list:
    '''
    Return the common and domain findings of a module as code and message pairs.

    :param ast: The root module AST.
    :type ast: Any
    :return: The findings in check order.
    :rtype: list
    '''

    # Build the symbol table once, then run the two selectors semantic runs for domain.
    cache = build_cache()
    builder = SymbolTableBuilder(cache, COMPILER_PROVISION_CACHE_PREFIX)
    builder.build(ast)
    findings = []
    for selector in ('common.', 'domain.'):
        findings.extend(ConformanceChecker(
            builder.scopes,
            cache,
            selector,
            COMPILER_PROVISION_CACHE_PREFIX,
        ).check(ast))
    return [(finding['error_code'], finding['message']) for finding in findings]

# *** fixtures

# ** fixture: tokens
@pytest.fixture(scope='module')
def tokens():
    '''
    Load the declared token catalogue.

    :return: The token rules.
    :rtype: list
    '''

    # Map the group dict in declared order.
    return load_token_rules()

# ** fixture: grammars
@pytest.fixture(scope='module')
def grammars():
    '''
    Load the declared grammar catalogue.

    :return: The grammars.
    :rtype: list
    '''

    # Map the group dict in declared order.
    return load_grammar_rules()

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

# ** test: comment_below_block_column_parses
@pytest.mark.parametrize('column', [0, 2, 4])
def test_comment_below_block_column_parses(column, tokens, grammars) -> None:
    '''
    Test that a comment at columns 0, 2 and 4 gives the same AST and findings.

    :param column: The comment column.
    :type column: int
    :param tokens: The declared token catalogue.
    :type tokens: list
    :param grammars: The declared grammar catalogue.
    :type grammars: list
    '''

    # The block-column variant is the control.
    control = _parse(COMMENT_PROBE.format(indent=' ' * 4), tokens, grammars)
    probe = _parse(COMMENT_PROBE.format(indent=' ' * column), tokens, grammars)

    # Only the comment node's column may differ.
    assert _masked_ast(probe, COMMENT_PROBE_LINENO) == _masked_ast(control, COMMENT_PROBE_LINENO)
    assert _findings(probe) == _findings(control)

# ** test: comment_below_block_column_keeps_layout
@pytest.mark.parametrize('column', [0, 2, 4])
def test_comment_below_block_column_keeps_layout(column, tokens, grammars) -> None:
    '''
    Test that a standalone comment never changes the indent and dedent tokens.

    The comparison is the same file with that comment line removed.

    :param column: The comment column.
    :type column: int
    :param tokens: The declared token catalogue.
    :type tokens: list
    :param grammars: The declared grammar catalogue.
    :type grammars: list
    '''

    # Compare with the same file with the comment line removed.
    text = COMMENT_PROBE.format(indent=' ' * column)
    with_comment = TiferetLexer().tokenize(text, tokens, grammars)
    without = TiferetLexer().tokenize(_drop_line(text, COMMENT_PROBE_LINENO), tokens, grammars)
    assert _skeleton(with_comment) == _skeleton(without)

    # The comment stays in the stream for the grammar, followed by its newline.
    index = next(
        position
        for position, token in enumerate(with_comment)
        if token.type == a.lexer.LINE_COMMENT and token.lineno == COMMENT_PROBE_LINENO
    )
    assert with_comment[index + 1].type == a.lexer.NEWLINE

# ** test: column0_comment_in_nested_block_parses
def test_column0_comment_in_nested_block_parses(tokens, grammars) -> None:
    '''
    Test that a column-0 comment between two statements of a nested block parses.

    :param tokens: The declared token catalogue.
    :type tokens: list
    :param grammars: The declared grammar catalogue.
    :type grammars: list
    '''

    # The comment line does not close the nested block.
    stream = TiferetLexer().tokenize(NESTED_PROBE, tokens, grammars)
    without = TiferetLexer().tokenize(_drop_line(NESTED_PROBE, 14), tokens, grammars)
    assert _skeleton(stream) == _skeleton(without)

    # The module parses.
    assert _parse(NESTED_PROBE, tokens, grammars) is not None

# ** test: trailing_column0_comment_inside_block_parses
def test_trailing_column0_comment_inside_block_parses(tokens, grammars) -> None:
    '''
    Test that a file whose last line is a column-0 comment inside a block parses.

    :param tokens: The declared token catalogue.
    :type tokens: list
    :param grammars: The declared grammar catalogue.
    :type grammars: list
    '''

    # The held comment goes before the final dedent run.
    stream = TiferetLexer().tokenize(TRAILING_PROBE, tokens, grammars)
    types = [token.type for token in stream]
    assert types[-3:] == [a.lexer.LINE_COMMENT, a.lexer.NEWLINE, a.lexer.DEDENT]

    # The module parses.
    assert _parse(TRAILING_PROBE, tokens, grammars) is not None

# ** test: comment_inside_delimiters_is_not_held
def test_comment_inside_delimiters_is_not_held(tokens, grammars) -> None:
    '''
    Test that comments inside open delimiters keep their current handling.

    :param tokens: The declared token catalogue.
    :type tokens: list
    :param grammars: The declared grammar catalogue.
    :type grammars: list
    '''

    # Comments inside the call are dropped as before, so no comment sits between the parentheses.
    stream = TiferetLexer().tokenize(DELIMITER_PROBE, tokens, grammars)
    types = [token.type for token in stream]
    opened = types.index(a.lexer.LPAREN)
    closed = types.index(a.lexer.RPAREN, opened)
    assert a.lexer.LINE_COMMENT not in types[opened:closed]

    # The module parses.
    assert _parse(DELIMITER_PROBE, tokens, grammars) is not None

# ** test: artifact_tokens_unchanged_on_fixtures
def test_artifact_tokens_unchanged_on_fixtures(tokens, grammars, monkeypatch) -> None:
    '''
    Test that artifact comment tokens and their positions are unchanged on the dialect fixtures.

    :param tokens: The declared token catalogue.
    :type tokens: list
    :param grammars: The declared grammar catalogue.
    :type grammars: list
    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    '''

    # Tokenize every fixture with the held comments.
    paths = sorted(_FIXTURES_DIR.rglob('*.py'))
    assert paths
    artifact_types = (a.lexer.ARTIFACT_START, a.lexer.ARTIFACT_SECTION, a.lexer.ARTIFACT_MEMBER)
    def artifacts(stream):
        return [
            (token.type, token.value, token.lineno, token.lexpos)
            for token in stream
            if token.type in artifact_types
        ]
    held = {
        path: TiferetLexer().tokenize(path.read_text(encoding='utf-8'), tokens, grammars)
        for path in paths
    }

    # Tokenize again with nothing held, which is the stream before this change.
    monkeypatch.setattr(lexer_module, '_lift_standalone_comments', lambda lexemes, profile: (lexemes, {}, []))
    for path, stream in held.items():
        before = TiferetLexer().tokenize(path.read_text(encoding='utf-8'), tokens, grammars)
        assert artifacts(stream) == artifacts(before), path.name
