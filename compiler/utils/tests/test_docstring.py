"""Utils – DocstringParser Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..docstring import DocstringParser

# *** fixtures

# ** fixture: rst_docstring
@pytest.fixture
def rst_docstring() -> str:
    '''
    Fixture for an RST docstring that includes its triple-quote delimiters.

    :return: The raw docstring text.
    :rtype: str
    '''

    # Return a raw triple-quoted string that includes the delimiter characters.
    return r'''"""Execute the operation.

:param a: The first operand.
:param b: The second operand.
:return: The computed result.
"""'''

# *** tests

# ** test: docstring_parser_strip_triple_double
def test_docstring_parser_strip_triple_double() -> None:
    '''
    Test that strip removes surrounding triple double quotes.
    '''

    # Strip a triple-double-quoted sentence.
    assert DocstringParser.strip('"""Hello, world."""') == 'Hello, world.'

# ** test: docstring_parser_strip_triple_single
def test_docstring_parser_strip_triple_single() -> None:
    '''
    Test that strip removes surrounding triple single quotes.
    '''

    # Strip a triple-single-quoted sentence.
    assert DocstringParser.strip("'''Hello, world.'''") == 'Hello, world.'

# ** test: docstring_parser_strip_empty
def test_docstring_parser_strip_empty() -> None:
    '''
    Test that strip returns an empty string for falsy input.
    '''

    # Both an empty string and a missing value return an empty string.
    assert DocstringParser.strip('') == ''
    assert DocstringParser.strip(None) == ''

# ** test: docstring_parser_parse_param_descriptions
def test_docstring_parser_parse_param_descriptions(rst_docstring: str) -> None:
    '''
    Test that :param names map to collapsed descriptions.

    :param rst_docstring: The delimited RST docstring fixture.
    :type rst_docstring: str
    '''

    # Map the fixture parameters to their descriptions.
    assert DocstringParser.parse_param_descriptions(rst_docstring) == {
        'a': 'The first operand.',
        'b': 'The second operand.',
    }

# ** test: docstring_parser_parse_param_descriptions_empty
def test_docstring_parser_parse_param_descriptions_empty() -> None:
    '''
    Test that a docstring without :param entries returns an empty map.
    '''

    # A description-only docstring has no parameter fields.
    assert DocstringParser.parse_param_descriptions('"""Return a value."""') == {}

# ** test: docstring_parser_parse_return_descriptions
def test_docstring_parser_parse_return_descriptions(rst_docstring: str) -> None:
    '''
    Test that :return descriptions are collected in order.

    :param rst_docstring: The delimited RST docstring fixture.
    :type rst_docstring: str
    '''

    # Collect the fixture return description.
    assert DocstringParser.parse_return_descriptions(rst_docstring) == [
        'The computed result.',
    ]

# ** test: docstring_parser_parse_return_descriptions_empty
def test_docstring_parser_parse_return_descriptions_empty() -> None:
    '''
    Test that a docstring without return fields returns an empty list.
    '''

    # A description-only docstring has no return fields.
    assert DocstringParser.parse_return_descriptions('"""Just a description."""') == []
