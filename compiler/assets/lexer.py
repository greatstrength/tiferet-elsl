"""Lexer Token Type Constants"""

# *** constants

# ** constant: artifact_start
ARTIFACT_START = 'ARTIFACT_START'

# ** constant: artifact_section
ARTIFACT_SECTION = 'ARTIFACT_SECTION'

# ** constant: artifact_member
ARTIFACT_MEMBER = 'ARTIFACT_MEMBER'

# ** constant: obsolete
OBSOLETE = 'OBSOLETE'

# ** constant: todo
TODO = 'TODO'

# ** constant: see
SEE = 'SEE'

# ** constant: docstring
DOCSTRING = 'DOCSTRING'

# ** constant: line_comment
LINE_COMMENT = 'LINE_COMMENT'

# ** constant: from
FROM = 'FROM'

# ** constant: import
IMPORT = 'IMPORT'

# ** constant: as
AS = 'AS'

# ** constant: class
CLASS = 'CLASS'

# ** constant: def
DEF = 'DEF'

# ** constant: init
INIT = 'INIT'

# ** constant: return
RETURN = 'RETURN'

# ** constant: self
SELF = 'SELF'

# ** constant: if
IF = 'IF'

# ** constant: elif
ELIF = 'ELIF'

# ** constant: else
ELSE = 'ELSE'

# ** constant: for
FOR = 'FOR'

# ** constant: while
WHILE = 'WHILE'

# ** constant: try
TRY = 'TRY'

# ** constant: except
EXCEPT = 'EXCEPT'

# ** constant: finally
FINALLY = 'FINALLY'

# ** constant: raise
RAISE = 'RAISE'

# ** constant: with
WITH = 'WITH'

# ** constant: assert
ASSERT = 'ASSERT'

# ** constant: pass
PASS = 'PASS'

# ** constant: none
NONE = 'NONE'

# ** constant: not
NOT = 'NOT'

# ** constant: and
AND = 'AND'

# ** constant: or
OR = 'OR'

# ** constant: in
IN = 'IN'

# ** constant: is
IS = 'IS'

# ** constant: async
ASYNC = 'ASYNC'

# ** constant: await
AWAIT = 'AWAIT'

# ** constant: continue
CONTINUE = 'CONTINUE'

# ** constant: break
BREAK = 'BREAK'

# ** constant: del
DEL = 'DEL'

# ** constant: lambda
LAMBDA = 'LAMBDA'

# ** constant: identifier
IDENTIFIER = 'IDENTIFIER'

# ** constant: string_literal
STRING_LITERAL = 'STRING_LITERAL'

# ** constant: number_literal
NUMBER_LITERAL = 'NUMBER_LITERAL'

# ** constant: true
TRUE = 'TRUE'

# ** constant: false
FALSE = 'FALSE'

# ** constant: doublestar
DOUBLESTAR = 'DOUBLESTAR'

# ** constant: plus
PLUS = 'PLUS'

# ** constant: minus
MINUS = 'MINUS'

# ** constant: star
STAR = 'STAR'

# ** constant: slash
SLASH = 'SLASH'

# ** constant: doubleslash
DOUBLESLASH = 'DOUBLESLASH'

# ** constant: percent
PERCENT = 'PERCENT'

# ** constant: pipe
PIPE = 'PIPE'

# ** constant: ampersand
AMPERSAND = 'AMPERSAND'

# ** constant: eqeq
EQEQ = 'EQEQ'

# ** constant: noteq
NOTEQ = 'NOTEQ'

# ** constant: lteq
LTEQ = 'LTEQ'

# ** constant: gteq
GTEQ = 'GTEQ'

# ** constant: lt
LT = 'LT'

# ** constant: gt
GT = 'GT'

# ** constant: at
AT = 'AT'

# ** constant: lparen
LPAREN = 'LPAREN'

# ** constant: rparen
RPAREN = 'RPAREN'

# ** constant: lbrack
LBRACK = 'LBRACK'

# ** constant: rbrack
RBRACK = 'RBRACK'

# ** constant: lbrace
LBRACE = 'LBRACE'

# ** constant: rbrace
RBRACE = 'RBRACE'

# ** constant: comma
COMMA = 'COMMA'

# ** constant: colon
COLON = 'COLON'

# ** constant: arrow
ARROW = 'ARROW'

# ** constant: dot
DOT = 'DOT'

# ** constant: equals
EQUALS = 'EQUALS'

# ** constant: newline
NEWLINE = 'NEWLINE'

# ** constant: indent
INDENT = 'INDENT'

# ** constant: dedent
DEDENT = 'DEDENT'

# ** constant: tokens
TOKENS = (
    ARTIFACT_START,
    ARTIFACT_SECTION,
    ARTIFACT_MEMBER,
    OBSOLETE,
    TODO,
    SEE,
    DOCSTRING,
    LINE_COMMENT,
    FROM,
    IMPORT,
    AS,
    CLASS,
    DEF,
    INIT,
    RETURN,
    SELF,
    IF,
    ELIF,
    ELSE,
    FOR,
    WHILE,
    TRY,
    EXCEPT,
    FINALLY,
    WITH,
    ASSERT,
    PASS,
    RAISE,
    CONTINUE,
    BREAK,
    NOT,
    AND,
    OR,
    IN,
    IS,
    NONE,
    ASYNC,
    AWAIT,
    DEL,
    LAMBDA,
    IDENTIFIER,
    STRING_LITERAL,
    NUMBER_LITERAL,
    TRUE,
    FALSE,
    DOUBLESTAR,
    PLUS,
    MINUS,
    STAR,
    SLASH,
    DOUBLESLASH,
    PERCENT,
    PIPE,
    AMPERSAND,
    EQEQ,
    NOTEQ,
    LTEQ,
    GTEQ,
    LT,
    GT,
    AT,
    LPAREN,
    RPAREN,
    LBRACK,
    RBRACK,
    LBRACE,
    RBRACE,
    COMMA,
    COLON,
    ARROW,
    DOT,
    EQUALS,
    NEWLINE,
    INDENT,
    DEDENT,
)
