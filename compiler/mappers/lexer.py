"""Tiferet Compiler Lexer Mapper Objects"""

# *** imports

# ** infra
from tiferet_ly.mappers.lexeme import LexemeAggregate

# ** app
from ..domain import Token

# *** mappers

# ** mapper: token_aggregate
class TokenAggregate(Token):
    '''
    Mutable factory and bridge over a read-only token.

    Scan and parse construct tokens, synthesize indent markers, and convert
    to and from tiferet-ly lexemes here, without scanning source text.
    '''

    # * method: new (static)
    @staticmethod
    def new(
        type: str,
        value: str,
        lineno: int,
        lexpos: int,
    ) -> 'TokenAggregate':
        '''
        Construct a token aggregate from its four span fields.

        :param type: The token type name.
        :type type: str
        :param value: The token text.
        :type value: str
        :param lineno: The 1-based source line.
        :type lineno: int
        :param lexpos: The 0-based offset in the input text.
        :type lexpos: int
        :return: The constructed token aggregate.
        :rtype: TokenAggregate
        '''

        # Construct the aggregate from the four span fields.
        return TokenAggregate(
            type=type,
            value=value,
            lineno=lineno,
            lexpos=lexpos,
        )

    # * method: new_indent (static)
    @staticmethod
    def new_indent(lineno: int, lexpos: int) -> 'TokenAggregate':
        '''
        Construct a synthetic indent token at the given position.

        :param lineno: The 1-based source line.
        :type lineno: int
        :param lexpos: The 0-based offset in the input text.
        :type lexpos: int
        :return: The constructed indent token aggregate.
        :rtype: TokenAggregate
        '''

        # Synthesize an empty INDENT token at the given position.
        return TokenAggregate.new(
            type='INDENT',
            value='',
            lineno=lineno,
            lexpos=lexpos,
        )

    # * method: new_dedent (static)
    @staticmethod
    def new_dedent(lineno: int = 0, lexpos: int = 0) -> 'TokenAggregate':
        '''
        Construct a synthetic dedent token.

        :param lineno: The 1-based source line. Defaults to 0.
        :type lineno: int
        :param lexpos: The 0-based offset in the input text. Defaults to 0.
        :type lexpos: int
        :return: The constructed dedent token aggregate.
        :rtype: TokenAggregate
        '''

        # Synthesize an empty DEDENT token at the given position.
        return TokenAggregate.new(
            type='DEDENT',
            value='',
            lineno=lineno,
            lexpos=lexpos,
        )

    # * method: from_lexeme (static)
    @staticmethod
    def from_lexeme(lexeme: LexemeAggregate) -> 'TokenAggregate':
        '''
        Copy a tiferet-ly lexeme into a token aggregate.

        :param lexeme: The lexeme to copy.
        :type lexeme: LexemeAggregate
        :return: The constructed token aggregate.
        :rtype: TokenAggregate
        '''

        # Copy the four span fields; do not invent a column.
        return TokenAggregate.new(
            type=lexeme.type,
            value=lexeme.value,
            lineno=lexeme.lineno,
            lexpos=lexeme.lexpos,
        )

    # * method: to_lexeme
    def to_lexeme(self) -> LexemeAggregate:
        '''
        Convert this token aggregate into a tiferet-ly lexeme.

        :return: The synthesized lexeme aggregate.
        :rtype: LexemeAggregate
        '''

        # Synthesize a lexeme from the four span fields.
        return LexemeAggregate.synthesize(
            type=self.type,
            lineno=self.lineno,
            lexpos=self.lexpos,
            value=self.value,
        )
