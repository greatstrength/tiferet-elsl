"""Utils - End-of-Input Parse Error Position Tests"""

# *** imports

# ** core
from typing import Any, List, Optional

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

# ** constant: block_probe
BLOCK_PROBE = '''"""EOF probe"""

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

# ** constant: trailing_header
TRAILING_HEADER = '''
# ** function: other
def other() -> None:
'''

# ** constant: end_of_input_probe
END_OF_INPUT_PROBE = BLOCK_PROBE + TRAILING_HEADER

# ** constant: token_probe
TOKEN_PROBE = BLOCK_PROBE.replace('    y = x\n', '    y = = x\n')

# ** constant: truncated_corpus
TRUNCATED_CORPUS = {
    'two_space_indent': BLOCK_PROBE.replace('\n    ', '\n  '),
    'tab_indent_header_at_eof': BLOCK_PROBE.replace('\n    ', '\n\t') + TRAILING_HEADER,
    'body_then_header_at_eof': END_OF_INPUT_PROBE,
    'def_header_at_eof': HEADER_PROBE,
    'def_header_at_eof_no_newline': HEADER_PROBE.rstrip('\n'),
    'unclosed_call': HEADER_PROBE + "    '''\n    Return x.\n    '''\n\n    # Call.\n    y = max(x,\n",
    'class_header_at_eof': HEADER_PROBE.replace('def probe(x: int) -> int:', 'class Probe(object):'),
    'bad_assignment': TOKEN_PROBE,
}

# *** functions

# ** function: _tokenize
def _tokenize(text: str) -> List[Any]:
    '''
    Tokenize a source text against the declared catalogues.

    :param text: The source text.
    :type text: str
    :return: The recognized token stream.
    :rtype: List[Any]
    '''

    # Use the declared catalogues, as the lexical event does.
    return TiferetLexer().tokenize(text, load_token_rules(), load_grammar_rules())

# ** function: _parse_error
def _parse_error(text: str, stream: Optional[List[Any]] = None) -> ServiceError:
    '''
    Parse a source text, and return the parse error it raises.

    :param text: The source text.
    :type text: str
    :param stream: A token stream to parse instead of the text's own tokens.
    :type stream: Optional[List[Any]]
    :return: The raised error.
    :rtype: ServiceError
    '''

    # Use the declared catalogues, as the lexical and syntactic events do.
    if stream is None:
        stream = _tokenize(text)
    with pytest.raises(ServiceError) as raised:
        TiferetParser().parse(
            'probe',
            stream,
            load_grammar_rules(),
            load_token_rules(),
            load_production_rules(),
            source_text=text,
        )
    assert raised.value.error_code == 'PARSE_ERROR'
    return raised.value

# *** tests

# ** test: block_probe_parses
def test_block_probe_parses() -> None:
    '''
    Test that the block probe parses, so a probe built on it fails only where it differs.
    '''

    # The 4-space body opens one block and closes it at end of input.
    stream = _tokenize(BLOCK_PROBE)
    types = [token.type for token in stream]
    assert (types.count(a.lexer.INDENT), types.count(a.lexer.DEDENT)) == (1, 1)
    TiferetParser().parse(
        'probe',
        stream,
        load_grammar_rules(),
        load_token_rules(),
        load_production_rules(),
        source_text=BLOCK_PROBE,
    )

# ** test: end_of_input_error_has_position
def test_end_of_input_error_has_position() -> None:
    '''
    Test that an end-of-input parse error carries at_end and the last real token.
    '''

    # The trailing def header has no body, so the error arrives at end of input.
    error = _parse_error(END_OF_INPUT_PROBE)

    # The position is the trailing header's colon, the last real token, with an offset.
    assert error.kwargs['at_end'] is True
    assert error.kwargs['lineno'] == 22
    assert error.kwargs['lexpos'] is not None
    assert (error.kwargs['type'], error.kwargs['value']) == (a.lexer.COLON, ':')

    # The original payload stays, and the original error is the cause.
    assert error.message == 'Syntax error.'
    assert error.kwargs['grammar_id'] == 'tiferet_dialect'
    assert isinstance(error.__cause__, ServiceError)
    assert 'lineno' not in error.__cause__.kwargs

# ** test: end_of_input_error_closed_blocks
def test_end_of_input_error_closed_blocks() -> None:
    '''
    Test that an end-of-input parse error after a closed block has no open-block keys.
    '''

    # The layout filter closes the function body before the trailing header.
    error = _parse_error(END_OF_INPUT_PROBE)
    assert 'open_blocks' not in error.kwargs
    assert 'open_block_lineno' not in error.kwargs

# ** test: end_of_input_error_reports_open_block
def test_end_of_input_error_reports_open_block() -> None:
    '''
    Test that an end-of-input parse error names a block the supplied stream left open.
    '''

    # A stream with an indent no dedent closes; the layout filter never emits one.
    stream = _tokenize(HEADER_PROBE)
    stream.append(tok(a.lexer.INDENT, '', lineno=7, lexpos=len(HEADER_PROBE)))
    error = _parse_error(HEADER_PROBE, stream)

    # The position is still the colon; the open block is the indent's line.
    assert error.kwargs['at_end'] is True
    assert (error.kwargs['type'], error.kwargs['lineno']) == (a.lexer.COLON, 6)
    assert (error.kwargs['open_blocks'], error.kwargs['open_block_lineno']) == (1, 7)

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
