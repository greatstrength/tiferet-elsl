"""Compiler Default Grammar Catalog"""

# *** constants

# ** constant: tiferet_dialect_id
TIFERET_DIALECT_ID = 'tiferet_dialect'

# ** constant: tiferet_dialect_data
TIFERET_DIALECT_DATA = {
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

# ** constant: compiler_default_grammars
COMPILER_DEFAULT_GRAMMARS = {
    TIFERET_DIALECT_ID: TIFERET_DIALECT_DATA,
}
