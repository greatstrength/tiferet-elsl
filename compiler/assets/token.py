"""Compiler Default Token Catalog"""

# *** imports

# ** app
from .grammar import TIFERET_DIALECT_ID

# *** constants

# ** constant: compiler_default_tokens
COMPILER_DEFAULT_TOKENS = {
    'ARTIFACT_START': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '\\#\\s*\\*{3}\\s+.*',
        'action': 'return t\n',
    },
    'ARTIFACT_SECTION': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '\\#\\s*\\*{2}\\s+.*',
        'action': 'return t\n',
    },
    'ARTIFACT_MEMBER': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '\\#\\s*\\*\\s+.*',
        'action': 'return t\n',
    },
    'OBSOLETE': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '\\#\\s*-{1,2}\\s+obsolete:[^\\n]+',
        'action': 'return t\n',
    },
    'TODO': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '\\#\\s*\\+{1,2}\\s+todo:[^\\n]+',
        'action': 'return t\n',
    },
    'SEE': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '\\#\\s*>{1,2}\\s+see:[^\\n]+',
        'action': 'return t\n',
    },
    'DOCSTRING': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '(\\"\\"\\"[\\s\\S]*?\\"\\"\\"|\\\'\\\'\\\'[\\s\\S]*?\\\'\\\'\\\')',
        'action': "t.lexer.lineno += t.value.count('\\n')\nreturn t\n",
    },
    'LINE_COMMENT': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '\\#(?!\\s*\\*)(?!\\s*-{1,2}\\s+obsolete:)(?!\\s*\\+{1,2}\\s+todo:)(?!\\s*>{1,2}\\s+see:)[^\\n].*',
        'action': 'return t\n',
    },
    'STRING_LITERAL': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '(\\"([^\\"\\\\]|\\\\.)*\\"|\\\'([^\\\'\\\\]|\\\\.)*\\\')',
        'action': 'return t\n',
    },
    'ARROW': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '->',
        'action': 'return t\n',
    },
    'NUMBER_LITERAL': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '[0-9]+(\\.[0-9]+)?([a-zA-Z_][a-zA-Z0-9_]*)?',
        'action': "import re\nif re.search(r'[a-zA-Z_]', t.value):\n    t.type = 'UNKNOWN'\nreturn t\n",
    },
    'IDENTIFIER': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '[a-zA-Z_][a-zA-Z0-9_]*',
        'action': "keyword_map = {\n    'if': 'IF',\n    'elif': 'ELIF',\n    'else': 'ELSE',\n    'for': 'FOR',\n    'while': 'WHILE',\n    'try': 'TRY',\n    'except': 'EXCEPT',\n    'finally': 'FINALLY',\n    'raise': 'RAISE',\n    'with': 'WITH',\n    'assert': 'ASSERT',\n    'pass': 'PASS',\n    'None': 'NONE',\n    'not': 'NOT',\n    'and': 'AND',\n    'or': 'OR',\n    'in': 'IN',\n    'is': 'IS',\n    'async': 'ASYNC',\n    'await': 'AWAIT',\n    'yield': 'YIELD',\n    'continue': 'CONTINUE',\n    'break': 'BREAK',\n    'del': 'DEL',\n    'lambda': 'LAMBDA',\n}\nif t.value == 'class':\n    t.type = 'CLASS'\nelif t.value == 'def':\n    t.type = 'DEF'\nelif t.value == '__init__':\n    t.type = 'INIT'\nelif t.value == 'return':\n    t.type = 'RETURN'\nelif t.value == 'self':\n    t.type = 'SELF'\nelif t.value == 'from':\n    t.type = 'FROM'\nelif t.value == 'import':\n    t.type = 'IMPORT'\nelif t.value == 'as':\n    t.type = 'AS'\nelif t.value in keyword_map:\n    t.type = keyword_map[t.value]\nreturn t\n",
    },
    'TRUE': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '\\bTrue\\b',
    },
    'FALSE': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '\\bFalse\\b',
    },
    'DOUBLESTAR': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '\\*\\*',
    },
    'DOUBLESLASH': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '//',
    },
    'EQEQ': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '==',
    },
    'NOTEQ': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '!=',
    },
    'LTEQ': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '<=',
    },
    'GTEQ': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '>=',
    },
    'PLUS': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '\\+',
    },
    'MINUS': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '-',
    },
    'STAR': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '\\*',
    },
    'SLASH': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '/',
    },
    'PERCENT': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '%',
    },
    'PIPE': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '\\|',
    },
    'AMPERSAND': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '&',
    },
    'LT': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '<',
    },
    'GT': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '>',
    },
    'AT': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '@',
    },
    'LPAREN': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '\\(',
    },
    'RPAREN': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '\\)',
    },
    'LBRACK': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '\\[',
    },
    'RBRACK': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '\\]',
    },
    'LBRACE': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '\\{',
    },
    'RBRACE': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '\\}',
    },
    'COMMA': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': ',',
    },
    'COLON': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': ':',
    },
    'ELLIPSIS': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '\\.\\.\\.',
    },
    'DOT': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '\\.',
    },
    'EQUALS': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '=',
    },
    'NEWLINE': {
        'grammar_id': TIFERET_DIALECT_ID,
        'pattern': '(?:[ \\t]*\\n)+',
        'action': "t.lexer.lineno += t.value.count('\\n')\nreturn t\n",
    },
    'FROM': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'IMPORT': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'AS': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'CLASS': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'DEF': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'INIT': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'RETURN': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'YIELD': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'SELF': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'IF': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'ELIF': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'ELSE': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'FOR': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'WHILE': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'TRY': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'EXCEPT': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'FINALLY': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'WITH': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'ASSERT': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'PASS': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'RAISE': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'CONTINUE': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'BREAK': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'NOT': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'AND': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'OR': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'IN': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'IS': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'NONE': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'ASYNC': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'AWAIT': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'DEL': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'LAMBDA': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'INDENT': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
    'DEDENT': {
        'grammar_id': TIFERET_DIALECT_ID,
    },
}
