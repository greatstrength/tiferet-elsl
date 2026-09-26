"""Assets – Declared Lexicon Catalogue Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import yaml

# ** app
from compiler.assets import lexer as a

# *** constants

# ** constant: assets_dir
_ASSETS_DIR = Path(__file__).resolve().parents[2] / 'assets'

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

# *** functions

# ** function: load_tokens
def load_tokens() -> list:
    '''
    Load the declared token catalogue.

    :return: The tokens list.
    :rtype: list
    '''

    # Read the token catalogue with a safe YAML loader.
    with (_ASSETS_DIR / 'tokens.yml').open(encoding='utf-8') as handle:
        document = yaml.safe_load(handle)

    # Return the tokens list.
    return document['tokens']

# ** function: load_grammars
def load_grammars() -> dict:
    '''
    Load the declared grammar catalogue.

    :return: The grammars mapping.
    :rtype: dict
    '''

    # Read the grammar catalogue with a safe YAML loader.
    with (_ASSETS_DIR / 'grammars.yml').open(encoding='utf-8') as handle:
        document = yaml.safe_load(handle)

    # Return the grammars mapping.
    return document['grammars']

# ** function: expand_tokens
def expand_tokens() -> list:
    '''
    Expand each token item to a name and body pair.

    :return: Ordered (name, body) pairs.
    :rtype: list
    '''

    # Expand each single-key token map.
    return [next(iter(item.items())) for item in load_tokens()]

# *** tests

# ** test: tokens_count_and_order
def test_tokens_count_and_order() -> None:
    '''
    Test that the catalogue has 77 names in declared order.
    '''

    # Expand the catalogue in file order.
    pairs = expand_tokens()
    names = [name for name, _body in pairs]

    # Assert the declared order, including string keys for TRUE and FALSE.
    assert len(names) == 77
    assert names == list(_ORDERED_NAMES)
    assert names[12] == 'TRUE'
    assert names[13] == 'FALSE'
    assert isinstance(names[12], str)
    assert isinstance(names[13], str)

# ** test: tokens_grammar_id
def test_tokens_grammar_id() -> None:
    '''
    Test that every token belongs to tiferet_dialect.
    '''

    # Every body carries the declared grammar id.
    for _name, body in expand_tokens():
        assert body['grammar_id'] == 'tiferet_dialect'

# ** test: tokens_complex_have_pattern_and_action
def test_tokens_complex_have_pattern_and_action() -> None:
    '''
    Test that each complex token has a pattern and an action.
    '''

    # Index the catalogue by name.
    by_name = dict(expand_tokens())

    # Complex rules carry both fields.
    for name in _COMPLEX_NAMES:
        assert 'pattern' in by_name[name]
        assert 'action' in by_name[name]

# ** test: tokens_simple_have_pattern_no_action
def test_tokens_simple_have_pattern_no_action() -> None:
    '''
    Test that each simple token has a pattern and no action.
    '''

    # Index the catalogue by name.
    by_name = dict(expand_tokens())

    # Simple rules carry a pattern only.
    for name in _SIMPLE_NAMES:
        assert 'pattern' in by_name[name]
        assert 'action' not in by_name[name]

# ** test: tokens_synthetic_omit_pattern_and_action
def test_tokens_synthetic_omit_pattern_and_action() -> None:
    '''
    Test that each synthetic token omits pattern and action.
    '''

    # Index the catalogue by name.
    by_name = dict(expand_tokens())

    # Synthetic rules name a type only.
    for name in _SYNTHETIC_NAMES:
        assert 'pattern' not in by_name[name]
        assert 'action' not in by_name[name]

# ** test: number_literal_action_sets_unknown
def test_number_literal_action_sets_unknown() -> None:
    '''
    Test that NUMBER_LITERAL reclassifies a trailing identifier as UNKNOWN.
    '''

    # Read the NUMBER_LITERAL action.
    by_name = dict(expand_tokens())
    action = by_name['NUMBER_LITERAL']['action']

    # The action is the only UNKNOWN path.
    assert "t.type = 'UNKNOWN'" in action

# ** test: identifier_action_reclassifies_keywords
def test_identifier_action_reclassifies_keywords() -> None:
    '''
    Test that IDENTIFIER reclassifies the declared keywords.
    '''

    # Read the IDENTIFIER action.
    by_name = dict(expand_tokens())
    action = by_name['IDENTIFIER']['action']

    # Structural and import keywords are reclassified by equality.
    for source, token_type in (
        ('class', 'CLASS'),
        ('def', 'DEF'),
        ('__init__', 'INIT'),
        ('return', 'RETURN'),
        ('self', 'SELF'),
        ('from', 'FROM'),
        ('import', 'IMPORT'),
        ('as', 'AS'),
    ):
        assert f"t.value == '{source}'" in action
        assert f"t.type = '{token_type}'" in action

    # yield is reclassified through the keyword map.
    assert "'yield': 'YIELD'" in action

# ** test: no_catchall_unknown_token
def test_no_catchall_unknown_token() -> None:
    '''
    Test that the catalogue does not name an UNKNOWN token.
    '''

    # No catalogue entry is named UNKNOWN.
    names = [name for name, _body in expand_tokens()]
    assert 'UNKNOWN' not in names

# ** test: grammars_single_tiferet_dialect
def test_grammars_single_tiferet_dialect() -> None:
    '''
    Test that the grammar catalogue declares only tiferet_dialect.
    '''

    # Load the grammar document.
    grammars = load_grammars()
    grammar = grammars['tiferet_dialect']

    # Assert the single grammar identity and lexing ignore string.
    assert list(grammars) == ['tiferet_dialect']
    assert grammar['parent_ids'] == []
    assert grammar['start'] == 'module'
    assert grammar['ignore'] == ' \t'

# ** test: grammars_layout_profile
def test_grammars_layout_profile() -> None:
    '''
    Test that the grammar layout profile matches the declared fields.
    '''

    # Load the layout profile.
    layout = load_grammars()['tiferet_dialect']['layout']

    # Assert block, delimiter, newline, and indent fields.
    assert layout['block_tokens'] == [
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
    ]
    assert layout['open_delimiters'] == ['LPAREN', 'LBRACK', 'LBRACE']
    assert layout['close_delimiters'] == ['RPAREN', 'RBRACK', 'RBRACE']
    assert layout['newline_token'] == 'NEWLINE'
    assert layout['suppress_newline_in_delimiters'] is True
    assert layout['indent_token'] == 'INDENT'
    assert layout['dedent_token'] == 'DEDENT'
    assert layout['tab_size'] == 4

# ** test: token_type_constants
def test_token_type_constants() -> None:
    '''
    Test that lexer token-type constants match their identifier strings.
    '''

    # Named layout and comment types are importable constants.
    assert a.NEWLINE == 'NEWLINE'
    assert a.INDENT == 'INDENT'
    assert a.DEDENT == 'DEDENT'
    assert a.LINE_COMMENT == 'LINE_COMMENT'
    assert a.SEE == 'SEE'
    assert a.NEWLINE in a.TOKENS

# ** test: no_rules_or_block_tracker_in_assets
def test_no_rules_or_block_tracker_in_assets() -> None:
    '''
    Test that the lexer constants module has no hand-wired rules.
    '''

    # Hand-wired rule tables and layout trackers are not part of this module.
    assert not hasattr(a, 'RULES')
    assert not hasattr(a, 'BlockTracker')
    assert not hasattr(a, 'TAB_SIZE')

    # Token-type constants may start with T_; rule functions may not.
    token_constants = {
        name for name in dir(a)
        if isinstance(getattr(a, name), str) and getattr(a, name) == name
    }
    rule_functions = [
        name for name in dir(a)
        if name.startswith('T_') and name not in token_constants
    ]
    assert rule_functions == []
