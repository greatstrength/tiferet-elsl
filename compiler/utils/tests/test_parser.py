"""Utils – Parser Rewrite Helper Tests"""

# *** imports

# ** core
from types import SimpleNamespace

# ** infra
from tiferet_ly.utils.parse import PlyParser as LyPlyParser

# ** app
from ...domain.ast import ExprKind, TypeKind
from .. import parser as parser_module
from ..parser import (
    GRAMMAR_ID,
    PlyParser,
    flatten_args_list,
    get_attribute_type,
    make_position_helpers,
    parse_artifact_header,
    parse_member_kind,
    parse_member_qualifier,
    parse_see_guide_path,
    render_lambda_body,
)

# *** tests

# ** test: grammar_id
def test_grammar_id() -> None:
    '''
    Test the dialect id and that mutations live on the published adapter.
    '''

    # The constant names the dialect grammar. TiferetParser belongs to #21.
    assert GRAMMAR_ID == 'tiferet_dialect'
    assert not hasattr(parser_module, 'TiferetParser')
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
