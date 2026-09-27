"""Mappers – AST Aggregate Domain Method Tests"""

# *** imports

# ** app
from ...domain.ast import ExprKind, StatementKind, TypeKind
from ..ast import (
    DeclarationAggregate as Decl,
    ExpressionAggregate as Expr,
    ParamListAggregate,
    StatementAggregate as Stmt,
    TypeAggregate,
    _as_list,
)

# *** tests

# ** test: type_name_str
def test_type_name_str() -> None:
    '''
    Test that a string type reports str.
    '''

    # A string kind reports its enum value.
    assert TypeAggregate(kind=TypeKind.STR).type_name == 'str'

# ** test: type_name_int
def test_type_name_int() -> None:
    '''
    Test that an integer type reports int.
    '''

    # An integer kind reports its enum value.
    assert TypeAggregate(kind=TypeKind.INT).type_name == 'int'

# ** test: type_name_float
def test_type_name_float() -> None:
    '''
    Test that a float type reports float.
    '''

    # A float kind reports its enum value.
    assert TypeAggregate(kind=TypeKind.FLOAT).type_name == 'float'

# ** test: type_name_bool
def test_type_name_bool() -> None:
    '''
    Test that a bool type reports bool.
    '''

    # A bool kind reports its enum value.
    assert TypeAggregate(kind=TypeKind.BOOL).type_name == 'bool'

# ** test: type_name_list
def test_type_name_list() -> None:
    '''
    Test that a list type reports list.
    '''

    # A list kind reports its enum value.
    assert TypeAggregate(kind=TypeKind.LIST).type_name == 'list'

# ** test: type_name_unknown
def test_type_name_unknown() -> None:
    '''
    Test that an unknown type reports unknown.
    '''

    # An unknown kind reports its enum value.
    assert TypeAggregate(kind=TypeKind.UNKNOWN).type_name == 'unknown'

# ** test: type_name_none_kind
def test_type_name_none_kind() -> None:
    '''
    Test that a none kind reports None.
    '''

    # The none kind reports the string None.
    assert TypeAggregate(kind=TypeKind.NONE).type_name == 'None'

# ** test: type_name_class_named
def test_type_name_class_named() -> None:
    '''
    Test that a named class type reports that name.
    '''

    # A named class reports the explicit name.
    assert TypeAggregate.new_class_type(name='ErrorService').type_name == 'ErrorService'

# ** test: type_name_class_unnamed
def test_type_name_class_unnamed() -> None:
    '''
    Test that an unnamed class type reports unknown.
    '''

    # An unnamed class reports unknown.
    assert TypeAggregate(kind=TypeKind.CLASS).type_name == 'unknown'

# ** test: type_name_func
def test_type_name_func() -> None:
    '''
    Test that a function type reports func.
    '''

    # A function factory reports func.
    assert TypeAggregate.new_func_type().type_name == 'func'

# ** test: new_null_and_unknown
def test_new_null_and_unknown() -> None:
    '''
    Test that null and unknown factories set the matching kinds.
    '''

    # Null is none and unknown is unknown.
    assert TypeAggregate.new_null_type().kind == TypeKind.NONE
    assert TypeAggregate.new_unknown_type().kind == TypeKind.UNKNOWN

# ** test: new_artifact_type
def test_new_artifact_type() -> None:
    '''
    Test that the artifact factory sets the artifact kind.
    '''

    # The artifact factory sets artifact.
    assert TypeAggregate.new_artifact_type().kind == TypeKind.ARTIFACT

# ** test: new_func_type_params_list
def test_new_func_type_params_list() -> None:
    '''
    Test that a single function parameter is wrapped into a one-item list.
    '''

    # Wrap one parameter through the function factory.
    param = ParamListAggregate.new('id')
    func_type = TypeAggregate.new_func_type(params=param)

    # The parameter is stored as a list of length 1.
    assert len(func_type.params) == 1
    assert func_type.params[0].name == 'id'

# ** test: set_subtype_chains
def test_set_subtype_chains() -> None:
    '''
    Test that a second subtype nests on the existing subtype.
    '''

    # Assign a subtype, then nest a second one.
    root = TypeAggregate.new(kind=TypeKind.LIST)
    first = TypeAggregate.new(kind=TypeKind.LIST)
    second = TypeAggregate.new(kind=TypeKind.STR)
    root.set_subtype(first)
    root.set_subtype(second)

    # The second call nests on the existing subtype.
    assert root.subtype is first
    assert first.subtype is second

# ** test: set_return_type_chains
def test_set_return_type_chains() -> None:
    '''
    Test that a second return type nests on the existing return type.
    '''

    # Assign a return type, then nest a second one.
    root = TypeAggregate.new_func_type()
    first = TypeAggregate.new(kind=TypeKind.FUNC)
    second = TypeAggregate.new(kind=TypeKind.STR)
    root.set_return_type(first)
    root.set_return_type(second)

    # The second call nests on the existing return type.
    assert root.return_type is first
    assert first.return_type is second

# ** test: param_list_new_required_default
def test_param_list_new_required_default() -> None:
    '''
    Test that the parameter factory defaults required to True.
    '''

    # A name-only parameter is required.
    assert ParamListAggregate.new('id').required is True

# ** test: new_args_param
def test_new_args_param() -> None:
    '''
    Test that the args factory is a list of unknown named args.
    '''

    # Build the default args parameter.
    param = ParamListAggregate.new_args_param()

    # The parameter is named args and typed as a list of unknown.
    assert param.name == 'args'
    assert param.type.kind == TypeKind.LIST
    assert param.type.subtype.kind == TypeKind.UNKNOWN

# ** test: new_kwargs_param
def test_new_kwargs_param() -> None:
    '''
    Test that the kwargs factory is a dict of unknown named kwargs.
    '''

    # Build the default kwargs parameter.
    param = ParamListAggregate.new_kwargs_param()

    # The parameter is named kwargs and typed as a dict of unknown.
    assert param.name == 'kwargs'
    assert param.type.kind == TypeKind.DICT
    assert param.type.subtype.kind == TypeKind.UNKNOWN

# ** test: as_list_none_list_scalar
def test_as_list_none_list_scalar() -> None:
    '''
    Test that _as_list normalizes None, a list, and a scalar.
    '''

    # None is empty, a list is unchanged, and a scalar is wrapped.
    assert _as_list(None) == []
    assert _as_list([1]) == [1]
    assert _as_list(1) == [1]

# ** test: collect_import_names_single
def test_collect_import_names_single() -> None:
    '''
    Test that a name expression contributes its name.
    '''

    # A single imported name is returned as a one-item list.
    names = Expr.collect_import_names(Expr.new_name_expr('DomainEvent'))
    assert names == ['DomainEvent']

# ** test: collect_import_names_none
def test_collect_import_names_none() -> None:
    '''
    Test that a missing expression contributes no names.
    '''

    # None is an empty import list.
    assert Expr.collect_import_names(None) == []

# ** test: collect_import_names_multi
def test_collect_import_names_multi() -> None:
    '''
    Test that nested multi-imports flatten in order.
    '''

    # Nest three names under import-multi nodes.
    expr = Expr.new_import_expr_multi(
        Expr.new_import_expr_multi(
            Expr.new_name_expr('DomainEvent'),
            'a',
        ),
        'TiferetError',
    )

    # The walk returns each name from left to right.
    assert Expr.collect_import_names(expr) == [
        'DomainEvent',
        'a',
        'TiferetError',
    ]

# ** test: collect_import_names_aliased
def test_collect_import_names_aliased() -> None:
    '''
    Test that an import-as expression returns only the alias.
    '''

    # Alias an imported name.
    expr = Expr.new_import_expr_as(
        Expr.new_name_expr('typing'),
        't',
    )

    # Only the alias is collected.
    assert expr.kind == ExprKind.IMPORT_AS
    assert Expr.collect_import_names(expr) == ['t']

# ** test: collect_import_names_multi_with_alias
def test_collect_import_names_multi_with_alias() -> None:
    '''
    Test that a multi-import containing an alias flattens to the visible names.
    '''

    # Combine an aliased name with a following name.
    expr = Expr.new_import_expr_multi(
        Expr.new_import_expr_as(
            Expr.new_name_expr('typing.List'),
            'List',
        ),
        'Any',
    )

    # The alias replaces the original name, then the next name follows.
    assert Expr.collect_import_names(expr) == ['List', 'Any']

# ** test: collect_import_names_unknown_kind
def test_collect_import_names_unknown_kind() -> None:
    '''
    Test that a call expression contributes no import names.
    '''

    # A call is not an import form.
    expr = Expr.new_call_expr(Expr.new_name_expr('fn'))
    assert expr.kind == ExprKind.CALL
    assert Expr.collect_import_names(expr) == []

# ** test: new_try_stmt_stores_finally
def test_new_try_stmt_stores_finally() -> None:
    '''
    Test that a try statement stores its finally body.
    '''

    # Build a try with a finally statement.
    final = Stmt.new_pass_stmt()
    stmt = Stmt.new_try_stmt(
        Stmt.new_pass_stmt(),
        finally_body=final,
    )

    # The finally body is stored, not dropped.
    assert stmt.kind == StatementKind.TRY_EXCEPT
    assert stmt.finally_body == [final]

# ** test: new_try_stmt_no_finally
def test_new_try_stmt_no_finally() -> None:
    '''
    Test that an omitted finally body is an empty list.
    '''

    # Omit the finally body.
    stmt = Stmt.new_try_stmt(Stmt.new_pass_stmt())
    assert stmt.finally_body == []

# ** test: new_double_star_expr
def test_new_double_star_expr() -> None:
    '''
    Test that a double-star expression stores the operand name.
    '''

    # Star a kwargs name.
    expr = Expr.new_double_star_expr(Expr.new_name_expr('kwargs'))
    assert expr.kind == ExprKind.DOUBLE_STAR_EXPR
    assert expr.left.name == 'kwargs'

# ** test: new_star_expr_distinct_from_double
def test_new_star_expr_distinct_from_double() -> None:
    '''
    Test that star and double-star expressions use distinct kinds.
    '''

    # Build both star forms.
    star = Expr.new_star_expr(Expr.new_name_expr('args'))
    double = Expr.new_double_star_expr(Expr.new_name_expr('kwargs'))

    # The kinds are distinct.
    assert star.kind == ExprKind.STAR_EXPR
    assert star.kind != double.kind

# ** test: param_list_set_default_clears_required
def test_param_list_set_default_clears_required() -> None:
    '''
    Test that setting a default stores it and clears required.
    '''

    # Assign a default to a required parameter.
    param = ParamListAggregate.new('id')
    default = Expr.new_none_expr()
    param.set_default(default)

    # The default is stored and the parameter is no longer required.
    assert param.default is default
    assert param.required is False

# ** test: new_name_or_literal_bool_str_num
def test_new_name_or_literal_bool_str_num() -> None:
    '''
    Test that bool strings, other strings, and integers classify correctly.
    '''

    # Classify a bool string, a string, and an integer.
    assert Expr.new_name_or_literal_expr('True').kind == ExprKind.BOOL_VAL
    assert Expr.new_name_or_literal_expr('hello').kind == ExprKind.STR_VAL
    number = Expr.new_name_or_literal_expr(3)
    assert number.kind == ExprKind.NUM_VAL
    assert number.value == '3'

# ** test: new_operator_expr_add_and_unknown
def test_new_operator_expr_add_and_unknown() -> None:
    '''
    Test that a plus operator is add and an unknown operator is a name.
    '''

    # Build a known operator and an unknown operator.
    left = Expr.new_name_expr('a')
    right = Expr.new_name_expr('b')
    added = Expr.new_operator_expr('+', left, right)
    unknown = Expr.new_operator_expr('??', left, right)

    # Plus maps to add; anything else is a name that keeps the operator text.
    assert added.kind == ExprKind.ADD
    assert unknown.kind == ExprKind.NAME
    assert unknown.value == '??'

# ** test: new_attribute_expr_preserves_receiver
def test_new_attribute_expr_preserves_receiver() -> None:
    '''
    Test that an attribute expression keeps the receiver and the attribute name.
    '''

    # Build an attribute on a receiver.
    receiver = Expr.new_name_expr('self')
    attr = Expr.new_attribute_expr(receiver, 'name')

    # The receiver is the left child and the attribute is the name.
    assert attr.left is receiver
    assert attr.name == 'name'

# ** test: new_module_and_func_decl
def test_new_module_and_func_decl() -> None:
    '''
    Test that a module body is a list and a function type is a type aggregate.
    '''

    # Wrap one module statement and attach a function type.
    body = Stmt.new_pass_stmt()
    module = Decl.new_module_decl('mod', code=body)
    func_type = TypeAggregate.new_func_type()
    func = Decl.new_func_decl('run', type=func_type)

    # The module body is a list and the function type is the aggregate.
    assert isinstance(module.code, list)
    assert module.code == [body]
    assert isinstance(func.type, TypeAggregate)
    assert func.type is func_type

# ** test: new_class_decl_wraps_members
def test_new_class_decl_wraps_members() -> None:
    '''
    Test that a class declaration is a class type with a member list.
    '''

    # Wrap one class member.
    member = Stmt.new_pass_stmt()
    decl = Decl.new_class_decl('Error', None, None, member)

    # The type is a class and the members are a list.
    assert decl.type.kind == TypeKind.CLASS
    assert isinstance(decl.code, list)
    assert decl.code == [member]

# ** test: new_if_stmt_normalizes_body
def test_new_if_stmt_normalizes_body() -> None:
    '''
    Test that a single if body becomes a one-element list.
    '''

    # Pass one statement as the body.
    body = Stmt.new_pass_stmt()
    stmt = Stmt.new_if_stmt(Expr.new_name_expr('flag'), body)

    # The body is a one-element list.
    assert len(stmt.body) == 1
    assert stmt.body[0] is body
