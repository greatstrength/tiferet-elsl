"""Utilities - TiferetLexer (tiferet-ly adapter)"""

# *** imports

# ** core
from typing import List

# ** infra
from tiferet_ly.domain.grammar import Grammar
from tiferet_ly.domain.token import TokenRule
from tiferet_ly.mappers.lexeme import LexemeAggregate
from tiferet_ly.utils.layout import LayoutFilter
from tiferet_ly.utils.lex import PlyLexer

# ** app
from ..interfaces import LexerService
from ..mappers import TokenAggregate
from .. import assets as a

# *** constants

# ** constant: grammar_id
GRAMMAR_ID = 'tiferet_dialect'

# *** utils

# ** util: tiferet_lexer
class TiferetLexer(LexerService):
    '''
    Adapt a declared catalogue into token aggregates without hosting rules.

    Callers pass the token and grammar catalogues. Layout is applied after
    a trailing newline is synthesized, and indent tracking stays in tiferet-ly.
    '''

    # * attribute: include_indent_dedent
    include_indent_dedent: bool

    # * init
    def __init__(self, include_indent_dedent: bool = True) -> None:
        '''
        Initialize the lexer adapter.

        :param include_indent_dedent: Whether to apply the dialect layout profile.
        :type include_indent_dedent: bool
        '''

        # Store the flag. Catalogues are passed to tokenize, not injected.
        self.include_indent_dedent = include_indent_dedent

    # * method: tokenize
    def tokenize(self, text: str, tokens: List[TokenRule], grammars: List[Grammar]) -> List[TokenAggregate]:
        '''
        Tokenize source text against caller-supplied catalogues.

        :param text: Source text to tokenize.
        :type text: str
        :param tokens: Declared token-rule catalogue.
        :type tokens: List[TokenRule]
        :param grammars: Declared grammar catalogue.
        :type grammars: List[Grammar]
        :return: Recognized token aggregates.
        :rtype: List[TokenAggregate]
        '''

        # Resolve the dialect grammar from the caller-supplied catalogue.
        grammar = next(g for g in grammars if g.id == GRAMMAR_ID)

        # Hold layout for a later pass, or skip it when indent injection is off.
        layout_profile = grammar.layout if self.include_indent_dedent else None

        # Strip layout so PlyLexer does not apply it before trailing-newline synthesis.
        raw_grammars = [
            g.model_copy(update={'layout': None}) if g.id == GRAMMAR_ID else g
            for g in grammars
        ]

        # Tokenize the raw stream. Unmatched characters fail loud.
        lexemes = PlyLexer().tokenize(GRAMMAR_ID, raw_grammars, tokens, text)

        # Synthesize a trailing newline when the raw stream does not already end on one.
        if lexemes and lexemes[-1].type != a.lexer.NEWLINE:
            lexemes.append(LexemeAggregate.synthesize(
                type=a.lexer.NEWLINE,
                lineno=lexemes[-1].lineno,
                lexpos=len(text),
                value='\n',
            ))

        # Apply declared layout only when indent and dedent injection is requested.
        if layout_profile is not None:
            lexemes = LayoutFilter.apply(lexemes, layout_profile, text)

        # Normalize injected layout tokens so indent and dedent values are empty strings.
        normalized = []
        for lexeme in lexemes:
            if lexeme.type in (a.lexer.INDENT, a.lexer.DEDENT) and lexeme.value is None:
                normalized.append(LexemeAggregate.synthesize(
                    type=lexeme.type,
                    lineno=lexeme.lineno,
                    lexpos=lexeme.lexpos,
                    value='',
                ))
            else:
                normalized.append(lexeme)
        lexemes = normalized

        # Drop a line comment that does not start a line. Keep standalone comments.
        filtered = []
        prev_type = None
        for lexeme in lexemes:
            if (
                lexeme.type == a.lexer.LINE_COMMENT
                and prev_type is not None
                and prev_type not in (a.lexer.NEWLINE, a.lexer.INDENT, a.lexer.DEDENT)
            ):
                continue

            filtered.append(lexeme)
            prev_type = lexeme.type
        lexemes = filtered

        # Map the filtered lexeme stream through the token aggregate factory.
        return [TokenAggregate.from_lexeme(lexeme) for lexeme in lexemes]
