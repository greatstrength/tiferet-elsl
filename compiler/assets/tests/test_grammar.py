"""Compiler Default Grammar Catalog Tests"""

# *** imports

# ** app
from ..grammar import (
    COMPILER_DEFAULT_GRAMMARS,
    TIFERET_DIALECT_DATA,
    TIFERET_DIALECT_ID,
)
from ..token import COMPILER_DEFAULT_TOKENS

# *** tests

# ** test: compiler_default_grammars_identity
def test_compiler_default_grammars_identity() -> None:
    '''
    Test that the grammar catalog is the one dialect id.
    '''

    # The group dict key is the dialect id. The body does not repeat it.
    assert TIFERET_DIALECT_ID == 'tiferet_dialect'
    assert list(COMPILER_DEFAULT_GRAMMARS) == [TIFERET_DIALECT_ID]
    assert COMPILER_DEFAULT_GRAMMARS[TIFERET_DIALECT_ID] is TIFERET_DIALECT_DATA
    assert 'id' not in TIFERET_DIALECT_DATA

# ** test: tiferet_dialect_data_matches_declared_body
def test_tiferet_dialect_data_matches_declared_body() -> None:
    '''
    Test that the dialect body matches the declared grammar fields.
    '''

    # Layout lists are lists of token-name strings. Ignore is one space and one tab.
    assert TIFERET_DIALECT_DATA == {
        'parent_ids': [
        ],
        'start': 'module',
        'ignore': ' \t',
        'layout': {
            'block_tokens': [
                'CLASS',
                'DEF',
                'IF',
                'ELIF',
                'ELSE',
                'FOR',
                'WHILE',
                'TRY',
                'EXCEPT',
                'FINALLY',
                'WITH',
            ],
            'open_delimiters': [
                'LPAREN',
                'LBRACK',
                'LBRACE',
            ],
            'close_delimiters': [
                'RPAREN',
                'RBRACK',
                'RBRACE',
            ],
            'newline_token': 'NEWLINE',
            'suppress_newline_in_delimiters': True,
            'indent_token': 'INDENT',
            'dedent_token': 'DEDENT',
            'tab_size': 4,
        },
    }

# ** test: layout_token_names_are_catalog_keys
def test_layout_token_names_are_catalog_keys() -> None:
    '''
    Test that every layout token name is a token-catalog key.
    '''

    # Block, delimiter, newline, indent, and dedent names are catalog keys.
    layout = TIFERET_DIALECT_DATA['layout']
    names = [
        *layout['block_tokens'],
        *layout['open_delimiters'],
        *layout['close_delimiters'],
        layout['newline_token'],
        layout['indent_token'],
        layout['dedent_token'],
    ]
    for name in names:
        assert name in COMPILER_DEFAULT_TOKENS
