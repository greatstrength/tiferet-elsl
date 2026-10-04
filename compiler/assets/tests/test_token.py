"""Compiler Default Token Catalog Tests"""

# *** imports

# ** app
from .. import lexer
from ..grammar import TIFERET_DIALECT_ID
from ..token import COMPILER_DEFAULT_TOKENS

# *** constants

# ** constant: ordered_names
_ORDERED_NAMES = (
    'ARTIFACT_START',
    'ARTIFACT_SECTION',
    'ARTIFACT_MEMBER',
    'OBSOLETE',
    'TODO',
    'SEE',
    'DOCSTRING',
    'LINE_COMMENT',
    'STRING_LITERAL',
    'ARROW',
    'NUMBER_LITERAL',
    'IDENTIFIER',
    'TRUE',
    'FALSE',
    'DOUBLESTAR',
    'DOUBLESLASH',
    'EQEQ',
    'NOTEQ',
    'LTEQ',
    'GTEQ',
    'PLUS',
    'MINUS',
    'STAR',
    'SLASH',
    'PERCENT',
    'PIPE',
    'AMPERSAND',
    'LT',
    'GT',
    'AT',
    'LPAREN',
    'RPAREN',
    'LBRACK',
    'RBRACK',
    'LBRACE',
    'RBRACE',
    'COMMA',
    'COLON',
    'ELLIPSIS',
    'DOT',
    'EQUALS',
    'NEWLINE',
    'FROM',
    'IMPORT',
    'AS',
    'CLASS',
    'DEF',
    'INIT',
    'RETURN',
    'YIELD',
    'SELF',
    'IF',
    'ELIF',
    'ELSE',
    'FOR',
    'WHILE',
    'TRY',
    'EXCEPT',
    'FINALLY',
    'WITH',
    'ASSERT',
    'PASS',
    'RAISE',
    'CONTINUE',
    'BREAK',
    'NOT',
    'AND',
    'OR',
    'IN',
    'IS',
    'NONE',
    'ASYNC',
    'AWAIT',
    'DEL',
    'LAMBDA',
    'INDENT',
    'DEDENT',
)

# ** constant: complex_names
_COMPLEX_NAMES = (
    'ARTIFACT_START',
    'ARTIFACT_SECTION',
    'ARTIFACT_MEMBER',
    'OBSOLETE',
    'TODO',
    'SEE',
    'DOCSTRING',
    'LINE_COMMENT',
    'STRING_LITERAL',
    'ARROW',
    'NUMBER_LITERAL',
    'IDENTIFIER',
    'NEWLINE',
)

# ** constant: simple_names
_SIMPLE_NAMES = (
    'TRUE',
    'FALSE',
    'DOUBLESTAR',
    'DOUBLESLASH',
    'EQEQ',
    'NOTEQ',
    'LTEQ',
    'GTEQ',
    'PLUS',
    'MINUS',
    'STAR',
    'SLASH',
    'PERCENT',
    'PIPE',
    'AMPERSAND',
    'LT',
    'GT',
    'AT',
    'LPAREN',
    'RPAREN',
    'LBRACK',
    'RBRACK',
    'LBRACE',
    'RBRACE',
    'COMMA',
    'COLON',
    'ELLIPSIS',
    'DOT',
    'EQUALS',
)

# ** constant: synthetic_names
_SYNTHETIC_NAMES = (
    'FROM',
    'IMPORT',
    'AS',
    'CLASS',
    'DEF',
    'INIT',
    'RETURN',
    'YIELD',
    'SELF',
    'IF',
    'ELIF',
    'ELSE',
    'FOR',
    'WHILE',
    'TRY',
    'EXCEPT',
    'FINALLY',
    'WITH',
    'ASSERT',
    'PASS',
    'RAISE',
    'CONTINUE',
    'BREAK',
    'NOT',
    'AND',
    'OR',
    'IN',
    'IS',
    'NONE',
    'ASYNC',
    'AWAIT',
    'DEL',
    'LAMBDA',
    'INDENT',
    'DEDENT',
)

# *** tests

# ** test: compiler_default_tokens_order
def test_compiler_default_tokens_order() -> None:
    '''
    Test that token order is the declared match order.
    '''

    # TRUE and FALSE are string keys, not booleans.
    names = list(COMPILER_DEFAULT_TOKENS)
    assert names == list(_ORDERED_NAMES)
    assert names[12] == 'TRUE'
    assert names[13] == 'FALSE'
    assert isinstance(names[12], str)
    assert isinstance(names[13], str)

# ** test: token_variant_sets
def test_token_variant_sets() -> None:
    '''
    Test the complex, simple, and synthetic token field sets.
    '''

    # Complex rules carry a pattern and an action that ends in one newline.
    for name in _COMPLEX_NAMES:
        body = COMPILER_DEFAULT_TOKENS[name]
        assert 'pattern' in body
        assert body['action'].endswith('\n')
        assert not body['action'].endswith('\n\n')

    # Simple rules carry a pattern and omit action.
    for name in _SIMPLE_NAMES:
        body = COMPILER_DEFAULT_TOKENS[name]
        assert 'pattern' in body
        assert 'action' not in body

    # Synthetic rules name a grammar only. Indent and dedent stay unpatterned.
    for name in _SYNTHETIC_NAMES:
        assert set(COMPILER_DEFAULT_TOKENS[name]) == {'grammar_id'}

# ** test: artifact_start_and_true_strings
def test_artifact_start_and_true_strings() -> None:
    '''
    Test the declared ARTIFACT_START and TRUE strings.
    '''

    # The pattern is the loaded escape sequence, and the action keeps its newline.
    start = COMPILER_DEFAULT_TOKENS['ARTIFACT_START']
    assert start['pattern'] == '\\#\\s*\\*{3}\\s+.*'
    assert start['action'] == 'return t\n'
    assert COMPILER_DEFAULT_TOKENS['TRUE']['pattern'] == '\\bTrue\\b'

# ** test: lexer_string_constants_are_catalog_keys
def test_lexer_string_constants_are_catalog_keys() -> None:
    '''
    Test that lexer string constants are catalog keys, except the TOKENS tuple.
    '''

    # String constants are ids. The tuple is not a catalog key.
    string_constants = {
        name: value
        for name, value in vars(lexer).items()
        if isinstance(value, str) and name.isupper()
    }
    assert 'TOKENS' not in string_constants
    for name, value in string_constants.items():
        assert name == value
        assert value in COMPILER_DEFAULT_TOKENS

    # ELLIPSIS and YIELD live only in the catalog. Catalog order is not TOKENS order.
    assert 'ELLIPSIS' in COMPILER_DEFAULT_TOKENS
    assert 'YIELD' in COMPILER_DEFAULT_TOKENS
    assert not hasattr(lexer, 'ELLIPSIS')
    assert not hasattr(lexer, 'YIELD')
    assert list(COMPILER_DEFAULT_TOKENS) != list(lexer.TOKENS)

# ** test: token_grammar_ids_omit_name
def test_token_grammar_ids_omit_name() -> None:
    '''
    Test that every token names the dialect id and omits name.
    '''

    # The grammar id is the shared constant, not a repeated string.
    for body in COMPILER_DEFAULT_TOKENS.values():
        assert body['grammar_id'] is TIFERET_DIALECT_ID
        assert 'name' not in body
