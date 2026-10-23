"""Utilities - TiferetLexer (tiferet-ly adapter)"""

# *** imports

# ** core
from typing import Dict, List

# ** infra
from tiferet_ly.domain.grammar import Grammar
from tiferet_ly.domain.layout import LayoutProfile
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

# *** functions

# ** function: _lift_standalone_comments
def _lift_standalone_comments(lexemes: List[LexemeAggregate], profile: LayoutProfile) -> tuple:
    '''
    Hold standalone comment lines out of the stream that layout reads.

    A standalone comment is a line comment that starts its line outside any
    open delimiter and is followed by its newline. The comment and that
    newline are held together, keyed by the next lexeme that is not a newline.

    :param lexemes: The raw lexeme stream, before layout.
    :type lexemes: List[LexemeAggregate]
    :param profile: The layout profile that names the open and close delimiters.
    :type profile: LayoutProfile
    :return: The kept stream, the held pairs by anchor identity, and the pairs held at end of input.
    :rtype: tuple
    '''

    # Walk the raw stream once, tracking delimiter depth as layout does.
    kept = []
    held = {}
    pending = []
    depth = 0
    prev_type = None
    index = 0
    while index < len(lexemes):
        lexeme = lexemes[index]

        # A comment that starts its line outside delimiters is held with its newline.
        if (
            lexeme.type == a.lexer.LINE_COMMENT
            and depth == 0
            and prev_type in (None, a.lexer.NEWLINE)
            and index + 1 < len(lexemes)
            and lexemes[index + 1].type == a.lexer.NEWLINE
        ):
            pending.extend([lexeme, lexemes[index + 1]])
            prev_type = a.lexer.NEWLINE
            index += 2
            continue

        # The first kept lexeme that is not a newline anchors the held pairs.
        if pending and lexeme.type != a.lexer.NEWLINE:
            held[id(lexeme)] = pending
            pending = []

        # Keep the lexeme and update the delimiter depth.
        if lexeme.type in profile.open_delimiters:
            depth += 1
        elif lexeme.type in profile.close_delimiters:
            depth = max(0, depth - 1)
        kept.append(lexeme)
        prev_type = lexeme.type
        index += 1

    # Pairs with no later code line are held for the end of input.
    return kept, held, pending

# ** function: _restore_standalone_comments
def _restore_standalone_comments(laid: List[LexemeAggregate],
                                 held: Dict[int, List[LexemeAggregate]],
                                 tail: List[LexemeAggregate]) -> List[LexemeAggregate]:
    '''
    Put held comment lines back after layout has run.

    Each held pair goes immediately before its anchor, after the indent and
    dedent run injected for that line. Pairs held at end of input go before
    the final dedent run.

    :param laid: The kept stream after layout.
    :type laid: List[LexemeAggregate]
    :param held: The held pairs keyed by anchor identity.
    :type held: Dict[int, List[LexemeAggregate]]
    :param tail: The pairs held at end of input.
    :type tail: List[LexemeAggregate]
    :return: The stream with every held comment line restored in order.
    :rtype: List[LexemeAggregate]
    '''

    # Buffer each layout run so the comments land after it.
    restored = []
    layout_run = []
    for lexeme in laid:
        if lexeme.type in (a.lexer.INDENT, a.lexer.DEDENT):
            layout_run.append(lexeme)
            continue
        restored.extend(layout_run)
        restored.extend(held.get(id(lexeme), []))
        restored.append(lexeme)
        layout_run = []

    # End-of-input comments go before the final dedent run.
    restored.extend(tail)
    restored.extend(layout_run)
    return restored

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
        # Standalone comment lines are held out so they do not move the block column.
        if layout_profile is not None:
            kept, held, tail = _lift_standalone_comments(lexemes, layout_profile)
            laid = LayoutFilter.apply(kept, layout_profile, text)
            lexemes = _restore_standalone_comments(laid, held, tail)

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
