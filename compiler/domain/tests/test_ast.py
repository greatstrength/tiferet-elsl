"""Domain – AST Domain Objects Tests"""

# *** imports

# ** core
from typing import List

# ** infra
import pytest
from pydantic import ValidationError

# ** app
from ..ast import ExprKind, ParamList, StatementKind, Type, TypeKind

# *** fixtures

# ** fixture: simple_string_type
@pytest.fixture
def simple_string_type() -> Type:
    '''
    Fixture for a string type.

    :return: The Type instance.
    :rtype: Type
    '''

    # Create and return a string type.
    return Type(name='str', kind=TypeKind.STR, subtype=None)

# ** fixture: simple_int_type
@pytest.fixture
def simple_int_type() -> Type:
    '''
    Fixture for an integer type.

    :return: The Type instance.
    :rtype: Type
    '''

    # Create and return an integer type.
    return Type(name='int', kind=TypeKind.INT, subtype=None)

# ** fixture: list_of_str_type
@pytest.fixture
def list_of_str_type(simple_string_type: Type) -> Type:
    '''
    Fixture for a list of strings.

    :param simple_string_type: The string element type.
    :type simple_string_type: Type
    :return: The Type instance.
    :rtype: Type
    '''

    # Create and return a list type whose element type is string.
    return Type(name='list', kind=TypeKind.LIST, subtype=simple_string_type)

# ** fixture: single_param
@pytest.fixture
def single_param(simple_string_type: Type) -> ParamList:
    '''
    Fixture for one required string parameter.

    :param simple_string_type: The parameter type.
    :type simple_string_type: Type
    :return: The ParamList instance.
    :rtype: ParamList
    '''

    # Create and return a required string parameter.
    return ParamList(name='id', type=simple_string_type, required=True, default=None)

# ** fixture: two_params
@pytest.fixture
def two_params(simple_string_type: Type, single_param: ParamList) -> List[ParamList]:
    '''
    Fixture for a name parameter followed by the single-parameter fixture.

    :param simple_string_type: The name parameter type.
    :type simple_string_type: Type
    :param single_param: The second parameter.
    :type single_param: ParamList
    :return: The parameter list.
    :rtype: List[ParamList]
    '''

    # Create and return the two-parameter list.
    return [
        ParamList(name='name', type=simple_string_type, required=True, default=None),
        single_param,
    ]

# *** tests

# ** test: type_kind_members
def test_type_kind_members() -> None:
    '''
    Test that every TypeKind member exists with its string value and that there are no extras.
    '''

    # Define the expected type-kind vocabulary.
    expected = {
        'UNKNOWN': 'unknown',
        'NONE': 'None',
        'BOOL': 'bool',
        'STR': 'str',
        'INT': 'int',
        'FLOAT': 'float',
        'LIST': 'list',
        'DICT': 'dict',
        'CLASS': 'class',
        'FUNC': 'func',
        'ARTIFACT': 'artifact',
        'MODULE': 'module',
    }

    # Assert the member count and each string value.
    assert len(TypeKind) == 12
    assert {member.name: member.value for member in TypeKind} == expected
    for name, value in expected.items():
        assert TypeKind[name] == value

# ** test: statement_kind_members
def test_statement_kind_members() -> None:
    '''
    Test that every StatementKind member exists with its string value and that there are no extras.
    '''

    # Define the expected statement-kind vocabulary.
    expected = {
        'DECL': 'decl',
        'EXPR': 'expr',
        'IF_ELSE': 'if_else',
        'FOR': 'for',
        'WHILE': 'while',
        'PRINT': 'print',
        'RETURN': 'return',
        'BLOCK': 'block',
        'IMPORT': 'import',
        'IMPORT_FROM': 'import_from',
        'ARTIFACT': 'artifact',
        'COMMENT': 'comment',
        'SNIPPET': 'snippet',
        'TRY_EXCEPT': 'try_except',
        'WITH': 'with',
        'RAISE': 'raise',
        'ASSERT': 'assert',
        'PASS': 'pass',
        'CONTINUE': 'continue',
        'BREAK': 'break',
        'DEL': 'del',
    }

    # Assert the member count and each string value.
    assert len(StatementKind) == 21
    assert {member.name: member.value for member in StatementKind} == expected
    for name, value in expected.items():
        assert StatementKind[name] == value

# ** test: expr_kind_members
def test_expr_kind_members() -> None:
    '''
    Test that every ExprKind member exists with its string value and that there are no extras.
    '''

    # Define the expected expression-kind vocabulary.
    expected = {
        'ADD': 'add',
        'SUB': 'sub',
        'MUL': 'mul',
        'DIV': 'div',
        'MOD': 'mod',
        'EXP': 'exp',
        'FLOORDIV': 'floordiv',
        'EQ': 'eq',
        'NEQ': 'neq',
        'LT': 'lt',
        'LTE': 'lte',
        'GT': 'gt',
        'GTE': 'gte',
        'NAME': 'name',
        'NUM_VAL': 'num_val',
        'INT_VAL': 'int_val',
        'STR_VAL': 'str_val',
        'BOOL_VAL': 'bool_val',
        'NONE_VAL': 'none_val',
        'ELLIPSIS_VAL': 'ellipsis_val',
        'ASSIGN': 'assign',
        'ARGS_LIST': 'args_list',
        'CALL': 'call',
        'ATTRIBUTE': 'attribute',
        'IMPORT': 'import',
        'IMPORT_AS': 'import_as',
        'IMPORT_MULTI': 'import_multi',
        'ARTIFACT': 'artifact',
        'COMMENT': 'comment',
        'NOT': 'not',
        'AND': 'and',
        'OR': 'or',
        'IS': 'is',
        'IS_NOT': 'is_not',
        'IN': 'in',
        'NOT_IN': 'not_in',
        'UNARY_MINUS': 'unary_minus',
        'LIST_LITERAL': 'list_literal',
        'DICT_LITERAL': 'dict_literal',
        'SET_LITERAL': 'set_literal',
        'TUPLE': 'tuple',
        'SUBSCRIPT': 'subscript',
        'SLICE': 'slice',
        'TERNARY': 'ternary',
        'COMPREHENSION': 'comprehension',
        'FOR_COMP': 'for_comp',
        'FSTRING': 'fstring',
        'AWAIT': 'await',
        'KWARG': 'kwarg',
        'STAR_EXPR': 'star_expr',
        'DOUBLE_STAR_EXPR': 'double_star_expr',
        'DICT_ENTRY': 'dict_entry',
    }

    # Assert the member count and each string value.
    assert len(ExprKind) == 52
    assert {member.name: member.value for member in ExprKind} == expected
    for name, value in expected.items():
        assert ExprKind[name] == value

# ** test: type_creation_and_validation
def test_type_creation_and_validation(simple_string_type: Type, list_of_str_type: Type) -> None:
    '''
    Test that constructed types store kind, name, and subtype.

    :param simple_string_type: The string type fixture.
    :type simple_string_type: Type
    :param list_of_str_type: The list-of-string type fixture.
    :type list_of_str_type: Type
    '''

    # Assert the string type stores its kind, name, and absent subtype.
    assert simple_string_type.kind == TypeKind.STR
    assert simple_string_type.name == 'str'
    assert simple_string_type.subtype is None

    # Assert the list type stores its kind, name, and string subtype.
    assert list_of_str_type.kind == TypeKind.LIST
    assert list_of_str_type.name == 'list'
    assert list_of_str_type.subtype == simple_string_type

# ** test: type_all_kinds_accepted
def test_type_all_kinds_accepted() -> None:
    '''
    Test that Type constructs for every TypeKind.
    '''

    # Construct a type for every kind.
    for kind in TypeKind:
        type_obj = Type(kind=kind)
        assert type_obj.kind == kind

# ** test: type_validation_missing_required
def test_type_validation_missing_required() -> None:
    '''
    Test that Type without a kind raises ValidationError.
    '''

    # Omitting the required kind must raise ValidationError.
    with pytest.raises(ValidationError):
        Type()

# ** test: param_list_creation_and_validation
def test_param_list_creation_and_validation(
    single_param: ParamList,
    two_params: List[ParamList],
    simple_string_type: Type,
) -> None:
    '''
    Test that constructed parameters store name, type, and required.

    :param single_param: The single-parameter fixture.
    :type single_param: ParamList
    :param two_params: The two-parameter fixture.
    :type two_params: List[ParamList]
    :param simple_string_type: The shared string type.
    :type simple_string_type: Type
    '''

    # Assert the single parameter stores its name, type, and requiredness.
    assert single_param.name == 'id'
    assert single_param.type == simple_string_type
    assert single_param.required is True

    # Assert both parameters in the list store name, type, and requiredness.
    assert [param.name for param in two_params] == ['name', 'id']
    assert all(param.type == simple_string_type for param in two_params)
    assert all(param.required is True for param in two_params)

# ** test: param_list_validation_missing_required
def test_param_list_validation_missing_required() -> None:
    '''
    Test that ParamList without a name raises ValidationError.
    '''

    # Omitting the required name must raise ValidationError.
    with pytest.raises(ValidationError):
        ParamList()

# ** test: type_class_func_properties
def test_type_class_func_properties() -> None:
    '''
    Test that class and function kinds set the matching classification flags.
    '''

    # A class type is a class and not a function.
    class_type = Type(kind=TypeKind.CLASS)
    assert class_type.is_class is True
    assert class_type.is_func is False

    # A function type is a function and not a class.
    func_type = Type(kind=TypeKind.FUNC)
    assert func_type.is_class is False
    assert func_type.is_func is True

# ** test: type_is_primitive
def test_type_is_primitive() -> None:
    '''
    Test that primitive kinds are marked primitive and class-like kinds are not.
    '''

    # Each primitive kind yields is_primitive True.
    for kind in Type._PRIMITIVE_KINDS:
        assert Type(kind=kind).is_primitive is True

    # Class, function, artifact, and module kinds are not primitive.
    for kind in (TypeKind.CLASS, TypeKind.FUNC, TypeKind.ARTIFACT, TypeKind.MODULE):
        assert Type(kind=kind).is_primitive is False

# ** test: type_is_valid_return_type
def test_type_is_valid_return_type() -> None:
    '''
    Test that valid return kinds are accepted and function-like kinds are not.
    '''

    # Each valid return kind yields is_valid_return_type True.
    for kind in Type._VALID_RETURN_KINDS:
        assert Type(kind=kind).is_valid_return_type is True

    # Function, artifact, and module kinds are not valid return types.
    for kind in (TypeKind.FUNC, TypeKind.ARTIFACT, TypeKind.MODULE):
        assert Type(kind=kind).is_valid_return_type is False

# ** test: type_type_name
def test_type_type_name() -> None:
    '''
    Test that type_name returns the enum value, an explicit class name, or unknown.
    '''

    # A non-class kind reports its enum value.
    assert Type(kind=TypeKind.STR).type_name == 'str'

    # A named class reports that name.
    assert Type(kind=TypeKind.CLASS, name='Error').type_name == 'Error'

    # An unnamed class reports unknown.
    assert Type(kind=TypeKind.CLASS).type_name == 'unknown'

# ** test: type_classification_rederives_on_assignment
def test_type_classification_rederives_on_assignment() -> None:
    '''
    Test that assigning kind rederives is_class.
    '''

    # Start from a non-class kind.
    type_obj = Type(kind=TypeKind.STR)
    assert type_obj.is_class is False

    # Assigning a class kind rederives is_class.
    type_obj.kind = TypeKind.CLASS
    assert type_obj.is_class is True
