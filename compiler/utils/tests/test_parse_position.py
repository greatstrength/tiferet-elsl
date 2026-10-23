"""Utils - End-of-Input Parse Error Position Tests"""

# *** imports

# ** infra
import pytest
from tiferet.interfaces.core import ServiceError

# ** app
from ... import assets as a
from ..lexer import TiferetLexer
from ..parser import TiferetParser, end_of_input_position
from .parser_test_helpers import (
    load_grammar_rules,
    load_production_rules,
    load_token_rules,
    tok,
)

# *** constants

# ** constant: open_block_probe
OPEN_BLOCK_PROBE = '''"""EOF probe"""

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
  # A comment at the block column.
  return y
'''

# ** constant: header_probe
HEADER_PROBE = '''"""Header probe"""

# *** functions

# ** function: probe
def probe(x: int) -> int:
'''

# ** constant: token_probe
TOKEN_PROBE = OPEN_BLOCK_PROBE.replace('  y = x\n', '  y = = x\n')

# ** constant: truncated_corpus
TRUNCATED_CORPUS = {
    'two_space_indent': OPEN_BLOCK_PROBE,
    'tab_indent': OPEN_BLOCK_PROBE.replace('\n  ', '\n\t'),
    'def_header_at_eof': HEADER_PROBE,
    'def_header_at_eof_no_newline': HEADER_PROBE.rstrip('\n'),
    'unclosed_call': HEADER_PROBE + "    '''\n    Return x.\n    '''\n\n    # Call.\n    y = max(x,\n",
    'class_header_at_eof': HEADER_PROBE.replace('def probe(x: int) -> int:', 'class Probe(object):'),
    'bad_assignment': TOKEN_PROBE,
}

# *** functions

# ** function: _parse_error
def _parse_error(text: str) -> ServiceError:
    '''
    Tokenize and parse a source text, and return the parse error it raises.

    :param text: The source text.
    :type text: str
    :return: The raised error.
    :rtype: ServiceError
    '''

    # Use the declared catalogues, as the lexical and syntactic events do.
    tokens = load_token_rules()
    grammars = load_grammar_rules()
    stream = TiferetLexer().tokenize(text, tokens, grammars)
    with pytest.raises(ServiceError) as raised:
        TiferetParser().parse(
            'probe',
            stream,
            grammars,
            tokens,
            load_production_rules(),
            source_text=text,
        )
    assert raised.value.error_code == 'PARSE_ERROR'
    return raised.value

# *** tests

# ** test: end_of_input_error_has_position
def test_end_of_input_error_has_position() -> None:
    '''
    Test that an end-of-input parse error carries at_end and the last real token.
    '''

    # The block never closes, so the error arrives at end of input.
    error = _parse_error(OPEN_BLOCK_PROBE)

    # The position is the return y line, the last real token, with an offset.
    assert error.kwargs['at_end'] is True
    assert error.kwargs['lineno'] == 19
    assert error.kwargs['lexpos'] is not None
    assert (error.kwargs['type'], error.kwargs['value']) == (a.lexer.IDENTIFIER, 'y')

    # The original payload stays, and the original error is the cause.
    assert error.message == 'Syntax error.'
    assert error.kwargs['grammar_id'] == 'tiferet_dialect'
    assert isinstance(error.__cause__, ServiceError)
    assert 'lineno' not in error.__cause__.kwargs

# ** test: end_of_input_error_reports_open_block
def test_end_of_input_error_reports_open_block() -> None:
    '''
    Test that an end-of-input parse error names the innermost unclosed block.
    '''

    # The function body indent on the docstring line never closes.
    error = _parse_error(OPEN_BLOCK_PROBE)
    assert error.kwargs['open_blocks'] >= 1
    assert error.kwargs['open_block_lineno'] == 7

# ** test: end_of_input_error_without_open_block
def test_end_of_input_error_without_open_block() -> None:
    '''
    Test that a def header at end of input has a position and no open-block keys.
    '''

    # The header is the last line, so its colon is the last real token.
    error = _parse_error(HEADER_PROBE)
    assert error.kwargs['at_end'] is True
    assert (error.kwargs['type'], error.kwargs['lineno']) == (a.lexer.COLON, 6)
    assert 'open_blocks' not in error.kwargs
    assert 'open_block_lineno' not in error.kwargs

# ** test: token_error_unchanged
def test_token_error_unchanged() -> None:
    '''
    Test that a parse error that already has a token keeps its payload.
    '''

    # The second equals sign on the y = = x line is the offending token.
    error = _parse_error(TOKEN_PROBE)

    # The payload is the supplier's, with no added keys and no wrapping.
    assert set(error.kwargs) == {'grammar_id', 'type', 'value', 'lineno', 'lexpos'}
    assert (error.kwargs['type'], error.kwargs['lineno']) == (a.lexer.EQUALS, 17)
    assert error.__cause__ is None

# ** test: end_of_input_position_empty_stream
def test_end_of_input_position_empty_stream() -> None:
    '''
    Test that an empty or layout-only stream is placed at line 1, offset 0.
    '''

    # No real lexeme means the start of the input.
    assert end_of_input_position([]) == {'at_end': True, 'lineno': 1, 'lexpos': 0}

    # Layout tokens and newlines are not real tokens.
    layout_only = [
        tok('NEWLINE', '\n', lineno=1, lexpos=0).to_lexeme(),
        tok('INDENT', '', lineno=2, lexpos=1).to_lexeme(),
    ]
    assert end_of_input_position(layout_only) == {
        'at_end': True,
        'lineno': 1,
        'lexpos': 0,
        'open_blocks': 1,
        'open_block_lineno': 2,
    }

# ** test: end_of_input_position_innermost_block
def test_end_of_input_position_innermost_block() -> None:
    '''
    Test that the open-block line is the innermost indent no dedent closed.
    '''

    # Two blocks open, the inner one closes, and a third opens inside the outer one.
    stream = [
        tok('IDENTIFIER', 'a', lineno=1, lexpos=0).to_lexeme(),
        tok('INDENT', '', lineno=2, lexpos=4).to_lexeme(),
        tok('INDENT', '', lineno=3, lexpos=12).to_lexeme(),
        tok('DEDENT', '', lineno=4, lexpos=20).to_lexeme(),
        tok('INDENT', '', lineno=5, lexpos=28).to_lexeme(),
        tok('IDENTIFIER', 'b', lineno=5, lexpos=32).to_lexeme(),
        tok('NEWLINE', '\n', lineno=5, lexpos=33).to_lexeme(),
    ]
    position = end_of_input_position(stream)
    assert (position['type'], position['value'], position['lineno']) == ('IDENTIFIER', 'b', 5)
    assert (position['open_blocks'], position['open_block_lineno']) == (2, 5)

# ** test: no_parse_error_lacks_lineno
@pytest.mark.parametrize('name', sorted(TRUNCATED_CORPUS))
def test_no_parse_error_lacks_lineno(name) -> None:
    '''
    Test that every parse error over the truncated and mis-indented corpus has a line.

    :param name: The corpus entry.
    :type name: str
    '''

    # Every entry fails to parse, and every failure is placed.
    error = _parse_error(TRUNCATED_CORPUS[name])
    assert isinstance(error.kwargs.get('lineno'), int)
    assert error.kwargs.get('lexpos') is not None
