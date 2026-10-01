"""Utils – Parser Rewrite Helper Tests"""

# *** imports

# ** core
from types import SimpleNamespace

# ** infra
from tiferet_ly.utils.parse import PlyParser as LyPlyParser

# ** app
from ...domain.ast import ExprKind, TypeKind
from ...interfaces import ParserService
from .. import parser as parser_module
from ..parser import (
    GRAMMAR_ID,
    PlyParser,
    TiferetParser,
    flatten_args_list,
    get_attribute_type,
    make_position_helpers,
    parse_artifact_header,
    parse_member_kind,
    parse_member_qualifier,
    parse_see_guide_path,
    render_lambda_body,
)
from .fixtures.simple_grammar import (
    SIMPLE_GRAMMAR_ID,
    SIMPLE_GRAMMARS,
    SIMPLE_PRODUCTIONS,
    SIMPLE_TOKENS,
)
from .parser_test_helpers import get_class_decl, get_group, get_member, get_section, tok

# *** tests

# ** test: grammar_id
def test_grammar_id() -> None:
    '''
    Test the dialect id and that mutations live on the published adapter.
    '''

    # The constant names the dialect grammar. Mutations stay off the module.
    assert GRAMMAR_ID == 'tiferet_dialect'
    assert hasattr(parser_module, 'TiferetParser')
    assert issubclass(PlyParser, LyPlyParser)
    assert PlyParser is not LyPlyParser
    assert not hasattr(parser_module, 'apply_annotations')
    assert not hasattr(parser_module, 'attach_dangling_else')

# ** test: parse_artifact_header
def test_parse_artifact_header() -> None:
    '''
    Test simple group, section, and colon headers.
    '''

    # A tier-1 group header keeps the marker as its type.
    assert parse_artifact_header('# *** imports') == ('imports', None, '***')

    # A colon header puts the keyword on the type and the name after the colon.
    assert parse_artifact_header('# ** event: ping') == ('ping', None, '** event')

    # A hash with no remainder is an unknown name.
    assert parse_artifact_header('#') == ('unknown', None, '')

# ** test: parse_artifact_header_qualified
def test_parse_artifact_header_qualified() -> None:
    '''
    Test a qualified group header, including surrounding whitespace.
    '''

    # The parenthetical is the qualifier, not part of the name.
    assert parse_artifact_header('# *** constants (ids)') == ('constants', 'ids', '***')

    # Whitespace around the token and inside the qualifier is ignored.
    assert parse_artifact_header('  # ***  constants  ( ids )  ') == (
        'constants',
        'ids',
        '***',
    )

# ** test: parse_member_kind
def test_parse_member_kind() -> None:
    '''
    Test method, attribute, init, and static-qualified member roles.
    '''

    # The role is the first word, including when a qualifier follows the name.
    assert parse_member_kind('# * method: execute') == 'method'
    assert parse_member_kind('# * attribute: name') == 'attribute'
    assert parse_member_kind('# * init') == 'init'
    assert parse_member_kind('# * method: execute (static)') == 'method'

# ** test: parse_member_qualifier
def test_parse_member_qualifier() -> None:
    '''
    Test a static qualifier and the unqualified absence case.
    '''

    # A trailing parenthetical is returned stripped.
    assert parse_member_qualifier('# * method: execute (static)') == 'static'
    assert parse_member_qualifier('(static)') == 'static'

    # A missing or empty pair is not a qualifier.
    assert parse_member_qualifier('# * init') is None
    assert parse_member_qualifier('# * method: execute ()') is None

# ** test: get_attribute_type_primitives
def test_get_attribute_type_primitives() -> None:
    '''
    Test that primitive annotation strings map to their type kinds.
    '''

    # Each built-in name selects the matching kind.
    assert get_attribute_type('int').kind == TypeKind.INT
    assert get_attribute_type('str').kind == TypeKind.STR
    assert get_attribute_type('float').kind == TypeKind.FLOAT
    assert get_attribute_type('bool').kind == TypeKind.BOOL
    assert get_attribute_type('list').kind == TypeKind.LIST
    assert get_attribute_type('dict').kind == TypeKind.DICT

# ** test: get_attribute_type_class_fallback
def test_get_attribute_type_class_fallback() -> None:
    '''
    Test that an unknown annotation string becomes a class type.
    '''

    # A class name is not one of the primitive spellings.
    subtype = get_attribute_type('str')
    class_type = get_attribute_type('ErrorService', additional_types=subtype)
    assert class_type.kind == TypeKind.CLASS
    assert class_type.subtype is subtype

# ** test: get_attribute_type_class_name_preserved
def test_get_attribute_type_class_name_preserved() -> None:
    '''
    Test that a class type keeps the annotation as its name.
    '''

    # Both the stored name and the derived type name keep the class spelling.
    class_type = get_attribute_type('ErrorService')
    assert class_type.name == 'ErrorService'
    assert class_type.type_name == 'ErrorService'

# ** test: get_attribute_type_none
def test_get_attribute_type_none() -> None:
    '''
    Test that the None annotation is a null type, not a class.
    '''

    # The null factory reports the none kind and the name None.
    none_type = get_attribute_type('None')
    assert none_type.kind == TypeKind.NONE
    assert none_type.type_name == 'None'

# ** test: parse_see_guide_path_at_guides_shorthand
def test_parse_see_guide_path_at_guides_shorthand() -> None:
    '''
    Test that an @guides shorthand is returned from a see annotation.
    '''

    # The shorthand is accepted as the guide path.
    token = '# >> see: @guides/domain/error.md#error'
    assert parse_see_guide_path(token) == '@guides/domain/error.md#error'

# ** test: parse_see_guide_path_full_docs_path
def test_parse_see_guide_path_full_docs_path() -> None:
    '''
    Test that a docs/guides path is returned from a see annotation.
    '''

    # The repository path is accepted as the guide path.
    token = '# >> see: docs/guides/domain/error.md#error'
    assert parse_see_guide_path(token) == 'docs/guides/domain/error.md#error'

# ** test: apply_annotations_promotes_see_guide_path
def test_apply_annotations_promotes_see_guide_path() -> None:
    '''
    Test that annotations are stored and the first SEE sets guide_path.
    '''

    # A TODO before the first SEE does not hide that SEE. A later SEE is ignored.
    annots = [
        {'kind': 'TODO', 'text': 'later'},
        {'kind': 'SEE', 'text': '# >> see: @guides/domain/error.md#error'},
        {'kind': 'SEE', 'text': '# >> see: docs/guides/other.md#x'},
    ]
    decl = SimpleNamespace()
    PlyParser.apply_annotations(decl, annots)

    # The list is stored as given, and the first SEE is the guide path.
    assert decl.annotations is annots
    assert decl.guide_path == '@guides/domain/error.md#error'

# ** test: apply_annotations_no_see_leaves_guide_path_unset
def test_apply_annotations_no_see_leaves_guide_path_unset() -> None:
    '''
    Test that TODO-only annotations leave guide_path unset.
    '''

    # Store the notes without inventing a guide path.
    annots = [{'kind': 'TODO', 'text': 'later'}]
    decl = SimpleNamespace()
    PlyParser.apply_annotations(decl, annots)

    # The notes are stored, and no SEE means no guide path attribute.
    assert decl.annotations is annots
    assert not hasattr(decl, 'guide_path')

# ** test: flatten_args_list_none
def test_flatten_args_list_none() -> None:
    '''
    Test that a missing argument spine flattens to an empty list.
    '''

    # None contributes no arguments.
    assert flatten_args_list(None) == []

# ** test: flatten_args_list_nested
def test_flatten_args_list_nested() -> None:
    '''
    Test that an ARGS_LIST spine flattens left to right.
    '''

    # A two-leaf spine is the left leaf followed by the right leaf.
    left = SimpleNamespace(kind=ExprKind.NAME, name='left')
    right = SimpleNamespace(kind=ExprKind.NAME, name='right')
    spine = SimpleNamespace(kind=ExprKind.ARGS_LIST, left=left, right=right)
    assert flatten_args_list(spine) == [left, right]

# ** test: render_lambda_body_name
def test_render_lambda_body_name() -> None:
    '''
    Test that a NAME expression renders as its name.
    '''

    # The identifier is the rendered text.
    expr = SimpleNamespace(kind=ExprKind.NAME, name='feature_id')
    assert render_lambda_body(expr) == 'feature_id'

# ** test: render_lambda_body_call
def test_render_lambda_body_call() -> None:
    '''
    Test that a call renders its callee and comma-separated arguments.
    '''

    # Flatten the argument spine inside the call parentheses.
    callee = SimpleNamespace(kind=ExprKind.NAME, name='int')
    left = SimpleNamespace(kind=ExprKind.INT_VAL, value='1')
    right = SimpleNamespace(kind=ExprKind.STR_VAL, value="'a'")
    args = SimpleNamespace(kind=ExprKind.ARGS_LIST, left=left, right=right)
    call = SimpleNamespace(kind=ExprKind.CALL, left=callee, right=args)
    assert render_lambda_body(call) == "int(1, 'a')"

# ** test: attach_dangling_else_empty
def test_attach_dangling_else_empty() -> None:
    '''
    Test that an empty statement list is left unchanged.
    '''

    # There is no last statement to mutate.
    stmts = []
    PlyParser.attach_dangling_else(stmts, [SimpleNamespace(is_if_else=False)])
    assert stmts == []

# ** test: attach_dangling_else_innermost
def test_attach_dangling_else_innermost() -> None:
    '''
    Test that a dangling else lands on the innermost open if.
    '''

    # Each outer if holds exactly one nested if, so the walk continues.
    inner = SimpleNamespace(is_if_else=True, else_body=[])
    middle = SimpleNamespace(is_if_else=True, else_body=[inner])
    outer = SimpleNamespace(is_if_else=True, else_body=[middle])
    else_body = [SimpleNamespace(is_if_else=False)]
    PlyParser.attach_dangling_else([outer], else_body)

    # Only the landed if receives the else body.
    assert inner.else_body is else_body
    assert middle.else_body == [inner]

# ** test: make_position_helpers_find_column
def test_make_position_helpers_find_column() -> None:
    '''
    Test column offsets, closure order, and the default position cells.
    '''

    # Unpack the six closures in rewrite-table order.
    source = 'ab\ncd'
    (
        pos,
        find_column,
        set_last_op_pos,
        get_last_op_pos,
        set_last_ident_pos,
        get_last_ident_pos,
    ) = make_position_helpers(source)
    assert find_column.__name__ == 'find_column'
    assert pos.__name__ == 'pos'

    # Offset zero is column zero. A character after the newline is column-relative.
    assert find_column(0) == 0
    assert find_column(3) == 0
    assert find_column(4) == 1

    # A source with no newline returns the offset itself.
    _, plain_find_column, *_rest = make_position_helpers('abcd')
    assert plain_find_column(2) == 2

    # pos pairs the symbol line with the column of its lexer offset.
    stub = SimpleNamespace(lineno=lambda n: 2, lexpos=lambda n: 4)
    assert pos(stub, 1) == (2, 1)

    # Both cells start at (0, 0) and do not share writes.
    assert get_last_op_pos() == (0, 0)
    assert get_last_ident_pos() == (0, 0)
    set_last_op_pos((3, 4))
    set_last_ident_pos((5, 6))
    assert get_last_op_pos() == (3, 4)
    assert get_last_ident_pos() == (5, 6)

# *** classes

# ** class: simple_parser_harness
class SimpleParserHarness:
    '''
    Parse synthetic tokens against the adapter fixture catalogue.
    '''

    # * init
    def __init__(self) -> None:
        '''
        Initialize the harness with one parser adapter.
        '''

        # The adapter takes no injected catalogues.
        self._parser = TiferetParser()

    # * method: parse
    def parse(self, module_name, tokens):
        '''
        Parse tokens against the synthetic catalogue.

        :param module_name: Module being parsed.
        :type module_name: str
        :param tokens: Synthetic token stream.
        :type tokens: list
        :return: The root module AST.
        :rtype: Any
        '''

        # The synthetic catalogue never reads compiler/assets.
        return self._parser.parse(
            module_name,
            tokens,
            SIMPLE_GRAMMARS,
            SIMPLE_TOKENS,
            SIMPLE_PRODUCTIONS,
        )

# *** functions

# ** function: attr_member_tokens
def _attr_member_tokens(name: str, type_name: str, lineno: int) -> list:
    '''
    Build one typed attribute member for the synthetic grammar.

    :param name: The attribute name.
    :type name: str
    :param type_name: The annotation name.
    :type type_name: str
    :param lineno: The member header line.
    :type lineno: int
    :return: The member token list.
    :rtype: list
    '''

    # The synthetic grammar accepts a typed attribute and nothing else.
    return [
        tok('ARTIFACT_MEMBER', f'# * attribute: {name}', lineno=lineno, lexpos=0),
        tok('NEWLINE', '\n', lineno=lineno, lexpos=1),
        tok('IDENTIFIER', name, lineno=lineno + 1, lexpos=2),
        tok('COLON', ':', lineno=lineno + 1, lexpos=3),
        tok('IDENTIFIER', type_name, lineno=lineno + 1, lexpos=4),
        tok('NEWLINE', '\n', lineno=lineno + 1, lexpos=5),
    ]

# ** function: class_module_tokens
def _class_module_tokens(members: list) -> list:
    '''
    Wrap attribute members in one events class for the synthetic grammar.

    :param members: Member token lists.
    :type members: list
    :return: The module token list.
    :rtype: list
    '''

    # One group, one section, and one class are the only successful path.
    tokens = [
        tok('ARTIFACT_START', '# *** events', lineno=1, lexpos=0),
        tok('NEWLINE', '\n', lineno=1, lexpos=1),
        tok('ARTIFACT_SECTION', '# ** event: sample', lineno=2, lexpos=2),
        tok('NEWLINE', '\n', lineno=2, lexpos=3),
        tok('CLASS', 'class', lineno=3, lexpos=4),
        tok('IDENTIFIER', 'Sample', lineno=3, lexpos=5),
        tok('LPAREN', '(', lineno=3, lexpos=6),
        tok('IDENTIFIER', 'DomainEvent', lineno=3, lexpos=7),
        tok('RPAREN', ')', lineno=3, lexpos=8),
        tok('COLON', ':', lineno=3, lexpos=9),
        tok('NEWLINE', '\n', lineno=3, lexpos=10),
        tok('INDENT', '', lineno=4, lexpos=11),
    ]
    for member in members:
        tokens.extend(member)
    tokens.append(tok('DEDENT', '', lineno=8, lexpos=40))
    return tokens

# *** tests

# ** test: instantiation
def test_instantiation() -> None:
    '''
    Test that the adapter can be constructed with no dependencies.
    '''

    # Construction does not load a catalogue or a grammar.
    parser = TiferetParser()
    assert parser is not None
    assert not any(name.startswith('p_') for name in dir(TiferetParser))

# ** test: implements_parser_service
def test_implements_parser_service() -> None:
    '''
    Test that the adapter is a ParserService.
    '''

    # The service contract is the base class, not a duck-typed method.
    assert isinstance(TiferetParser(), ParserService)

# ** test: simple_grammar_id
def test_simple_grammar_id() -> None:
    '''
    Test that the synthetic catalogue uses the dialect grammar id.
    '''

    # Adapter tests must not invent a second grammar id.
    assert SIMPLE_GRAMMAR_ID == GRAMMAR_ID == 'tiferet_dialect'

# ** test: simple_grammar_module_group_section_class_attr
def test_simple_grammar_module_group_section_class_attr() -> None:
    '''
    Test header, member-kind, and attribute-type wiring on one class.
    '''

    # Parse one typed attribute through the synthetic catalogue.
    module = SimpleParserHarness().parse(
        'sample',
        _class_module_tokens([_attr_member_tokens('service', 'ErrorService', 4)]),
    )
    group = get_group(module)
    section = get_section(module)
    cls = get_class_decl(module)
    member = get_member(module)
    attr = member.code[0].decl

    # Headers, the class, and the attribute type all come from the rewrite table.
    assert module.name == '__main__'
    assert group.decl.name == 'events'
    assert group.decl.artifact_type == '***'
    assert section.decl.name == 'sample'
    assert section.decl.artifact_type == '** event'
    assert cls.name == 'Sample'
    assert cls.type.subtype.name == 'DomainEvent'
    assert member.artifact_role == 'attribute'
    assert attr.name == 'service'
    assert attr.type.kind == TypeKind.CLASS
    assert attr.type.name == 'ErrorService'

# ** test: simple_grammar_multiple_members_accumulate
def test_simple_grammar_multiple_members_accumulate() -> None:
    '''
    Test that two attribute members accumulate on the class.
    '''

    # Two members share one class body.
    module = SimpleParserHarness().parse(
        'sample',
        _class_module_tokens([
            _attr_member_tokens('service', 'ErrorService', 4),
            _attr_member_tokens('name', 'str', 6),
        ]),
    )
    cls = get_class_decl(module)

    # Both members remain, in source order, with their own types.
    assert len(cls.code) == 2
    assert get_member(module, 0).code[0].decl.name == 'service'
    assert get_member(module, 1).code[0].decl.name == 'name'
    assert get_member(module, 1).code[0].decl.type.kind == TypeKind.STR
