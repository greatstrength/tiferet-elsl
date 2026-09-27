"""Mappers – AST Aggregate Domain Method Tests"""

# *** imports

# ** app
from ...domain.ast import TypeKind
from ..ast import ParamListAggregate, TypeAggregate, _as_list

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
