"""Domain – AST Domain Objects Tests"""

# *** imports

# ** core
from typing import List

# ** infra
import pytest
from pydantic import ValidationError

# ** app
from ..artifact import ArtifactDeclaration
from ..ast import (
    Declaration,
    ExprKind,
    Expression,
    ParamList,
    Statement,
    StatementKind,
    Type,
    TypeKind,
    encode_block,
    encode_handlers,
)

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

# ** fixture: simple_expression_name
@pytest.fixture
def simple_expression_name() -> Expression:
    '''
    Fixture for a name expression.

    :return: The Expression instance.
    :rtype: Expression
    '''

    # Create and return a name expression.
    return Expression(kind=ExprKind.NAME, name='value')

# ** fixture: simple_expression_int
@pytest.fixture
def simple_expression_int() -> Expression:
    '''
    Fixture for an integer literal expression.

    :return: The Expression instance.
    :rtype: Expression
    '''

    # Create and return an integer literal.
    return Expression(kind=ExprKind.INT_VAL, value='1')

# ** fixture: binary_add_expression
@pytest.fixture
def binary_add_expression(
    simple_expression_name: Expression,
    simple_expression_int: Expression,
) -> Expression:
    '''
    Fixture for an addition of a name and an integer literal.

    :param simple_expression_name: The left operand.
    :type simple_expression_name: Expression
    :param simple_expression_int: The right operand.
    :type simple_expression_int: Expression
    :return: The Expression instance.
    :rtype: Expression
    '''

    # Create and return the addition expression.
    return Expression(
        kind=ExprKind.ADD,
        left=simple_expression_name,
        right=simple_expression_int,
    )

# ** fixture: basic_declaration
@pytest.fixture
def basic_declaration() -> Declaration:
    '''
    Fixture for a declaration with only its required name.

    :return: The Declaration instance.
    :rtype: Declaration
    '''

    # Create and return a named declaration.
    return Declaration(name='answer')

# ** fixture: simple_statement_expr
@pytest.fixture
def simple_statement_expr(simple_expression_name: Expression) -> Statement:
    '''
    Fixture for an expression statement.

    :param simple_expression_name: The statement expression.
    :type simple_expression_name: Expression
    :return: The Statement instance.
    :rtype: Statement
    '''

    # Create and return an expression statement.
    return Statement(kind=StatementKind.EXPR, expr=simple_expression_name)

# ** fixture: simple_statement_decl
@pytest.fixture
def simple_statement_decl(basic_declaration: Declaration) -> Statement:
    '''
    Fixture for a declaration statement.

    :param basic_declaration: The nested declaration.
    :type basic_declaration: Declaration
    :return: The Statement instance.
    :rtype: Statement
    '''

    # Create and return a declaration statement.
    return Statement(kind=StatementKind.DECL, decl=basic_declaration)

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

# ** test: declaration_creation_and_validation
def test_declaration_creation_and_validation(basic_declaration: Declaration) -> None:
    '''
    Test that a declaration stores its required name and optional defaults.

    :param basic_declaration: The declaration fixture.
    :type basic_declaration: Declaration
    '''

    # The required name persists.
    assert basic_declaration.name == 'answer'

    # Optional fields use their defaults.
    assert basic_declaration.type is None
    assert basic_declaration.metadata == {}
    assert basic_declaration.doc_string is None
    assert basic_declaration.value is None
    assert basic_declaration.code == []
    assert basic_declaration.lineno is None
    assert basic_declaration.col is None
    assert basic_declaration.is_class is False
    assert basic_declaration.is_func is False

# ** test: declaration_with_optional_fields
def test_declaration_with_optional_fields(
    simple_expression_int: Expression,
    simple_statement_expr: Statement,
) -> None:
    '''
    Test that optional declaration fields persist.

    :param simple_expression_int: The initializer expression.
    :type simple_expression_int: Expression
    :param simple_statement_expr: A body statement.
    :type simple_statement_expr: Statement
    '''

    # Construct a declaration with every optional field set.
    declaration = Declaration(
        name='answer',
        doc_string='The answer.',
        value=simple_expression_int,
        code=[simple_statement_expr],
        lineno=4,
        col=2,
    )

    # Each optional field persists.
    assert declaration.doc_string == 'The answer.'
    assert declaration.value == simple_expression_int
    assert declaration.code == [simple_statement_expr]
    assert declaration.lineno == 4
    assert declaration.col == 2

# ** test: declaration_validation_missing_required
def test_declaration_validation_missing_required() -> None:
    '''
    Test that Declaration without a name raises ValidationError.
    '''

    # Omitting the required name must raise ValidationError.
    with pytest.raises(ValidationError):
        Declaration()

# ** test: expression_creation_and_validation
def test_expression_creation_and_validation(
    simple_expression_name: Expression,
    simple_expression_int: Expression,
) -> None:
    '''
    Test that name and integer expressions store kind, name, and value.

    :param simple_expression_name: The name expression fixture.
    :type simple_expression_name: Expression
    :param simple_expression_int: The integer expression fixture.
    :type simple_expression_int: Expression
    '''

    # A name stores its kind and name.
    assert simple_expression_name.kind == ExprKind.NAME
    assert simple_expression_name.name == 'value'
    assert simple_expression_name.value is None

    # An integer literal stores its kind and value.
    assert simple_expression_int.kind == ExprKind.INT_VAL
    assert simple_expression_int.value == '1'
    assert simple_expression_int.name is None

# ** test: expression_all_kinds_accepted
def test_expression_all_kinds_accepted() -> None:
    '''
    Test that Expression constructs for every ExprKind.
    '''

    # Construct an expression for every kind.
    for kind in ExprKind:
        expression = Expression(kind=kind)
        assert expression.kind == kind

# ** test: statement_creation_and_validation
def test_statement_creation_and_validation(
    simple_statement_expr: Statement,
    simple_statement_decl: Statement,
    simple_expression_name: Expression,
    basic_declaration: Declaration,
) -> None:
    '''
    Test that expression and declaration statements store kind and nested nodes.

    :param simple_statement_expr: The expression statement fixture.
    :type simple_statement_expr: Statement
    :param simple_statement_decl: The declaration statement fixture.
    :type simple_statement_decl: Statement
    :param simple_expression_name: The nested expression.
    :type simple_expression_name: Expression
    :param basic_declaration: The nested declaration.
    :type basic_declaration: Declaration
    '''

    # An expression statement stores its kind and expression.
    assert simple_statement_expr.kind == StatementKind.EXPR
    assert simple_statement_expr.expr == simple_expression_name

    # A declaration statement stores its kind and declaration.
    assert simple_statement_decl.kind == StatementKind.DECL
    assert simple_statement_decl.decl == basic_declaration

# ** test: statement_all_kinds_accepted
def test_statement_all_kinds_accepted() -> None:
    '''
    Test that Statement constructs for every StatementKind.
    '''

    # Construct a statement for every kind.
    for kind in StatementKind:
        statement = Statement(kind=kind)
        assert statement.kind == kind

# ** test: recursive_structures_work
def test_recursive_structures_work(
    simple_expression_name: Expression,
    simple_expression_int: Expression,
    basic_declaration: Declaration,
) -> None:
    '''
    Test that nested expression children and declaration bodies round-trip.

    :param simple_expression_name: The left operand.
    :type simple_expression_name: Expression
    :param simple_expression_int: The right operand.
    :type simple_expression_int: Expression
    :param basic_declaration: The nested declaration.
    :type basic_declaration: Declaration
    '''

    # Nested left and right children round-trip.
    expression = Expression(
        kind=ExprKind.ADD,
        left=simple_expression_name,
        right=simple_expression_int,
    )
    assert expression.left == simple_expression_name
    assert expression.right == simple_expression_int
    assert expression.left.name == 'value'
    assert expression.right.value == '1'

    # A declaration body list round-trips a nested declaration.
    nested = Statement(kind=StatementKind.DECL, decl=basic_declaration)
    outer = Declaration(name='outer', code=[nested])
    assert outer.code == [nested]
    assert outer.code[0].decl == basic_declaration
    assert outer.code[0].decl.code == []

    # A parameter default can hold an expression.
    param = ParamList(name='n', default=simple_expression_int)
    assert param.default == simple_expression_int

# ** test: expression_is_binary_op
def test_expression_is_binary_op() -> None:
    '''
    Test that addition is a binary op and floor division and names are not.
    '''

    # Floor division is intentionally outside the binary-op set.
    assert ExprKind.FLOORDIV not in Expression._BINARY_OPS
    assert Expression(kind=ExprKind.ADD).is_binary_op is True
    assert Expression(kind=ExprKind.FLOORDIV).is_binary_op is False
    assert Expression(kind=ExprKind.NAME).is_binary_op is False

# ** test: expression_is_assignment
def test_expression_is_assignment() -> None:
    '''
    Test that only an assignment kind sets is_assignment.
    '''

    # Assignment is the only kind that sets the flag.
    assert Expression(kind=ExprKind.ASSIGN).is_assignment is True
    for kind in ExprKind:
        if kind != ExprKind.ASSIGN:
            assert Expression(kind=kind).is_assignment is False

# ** test: expression_is_name_ref
def test_expression_is_name_ref() -> None:
    '''
    Test that only a name kind sets is_name_ref.
    '''

    # Name is the only kind that sets the flag.
    assert Expression(kind=ExprKind.NAME).is_name_ref is True
    for kind in ExprKind:
        if kind != ExprKind.NAME:
            assert Expression(kind=kind).is_name_ref is False

# ** test: expression_is_self_attribute
def test_expression_is_self_attribute() -> None:
    '''
    Test that a name starting with self. is a self attribute and a bare name is not.
    '''

    # A dotted self name is a self attribute.
    assert Expression(kind=ExprKind.NAME, name='self.x').is_self_attribute is True

    # A bare name is a name reference but not a self attribute.
    bare = Expression(kind=ExprKind.NAME, name='x')
    assert bare.is_self_attribute is False
    assert bare.is_name_ref is True

# ** test: expression_is_literal
def test_expression_is_literal() -> None:
    '''
    Test that literal kinds set is_literal and a name does not.
    '''

    # Each literal kind is a literal.
    for kind in Expression._LITERAL_KINDS:
        assert Expression(kind=kind).is_literal is True

    # A name is not a literal.
    assert Expression(kind=ExprKind.NAME).is_literal is False

# ** test: expression_literal_type
def test_expression_literal_type() -> None:
    '''
    Test that literal kinds map to type strings, except none and ellipsis.
    '''

    # Integer, float, string, and bool literals infer a type string.
    expected = {
        ExprKind.INT_VAL: 'int',
        ExprKind.NUM_VAL: 'float',
        ExprKind.STR_VAL: 'str',
        ExprKind.BOOL_VAL: 'bool',
    }
    for kind, literal_type in expected.items():
        assert Expression(kind=kind).literal_type == literal_type

    # None and ellipsis are literals without an inferred type string.
    assert Expression(kind=ExprKind.NONE_VAL).is_literal is True
    assert Expression(kind=ExprKind.NONE_VAL).literal_type is None
    assert Expression(kind=ExprKind.ELLIPSIS_VAL).is_literal is True
    assert Expression(kind=ExprKind.ELLIPSIS_VAL).literal_type is None

# ** test: statement_kind_property_true
def test_statement_kind_property_true() -> None:
    '''
    Test that each statement flag is true for its kind, including both import kinds.
    '''

    # Map each flag to the kinds that set it.
    flag_kinds = {
        'is_artifact': (StatementKind.ARTIFACT,),
        'is_decl': (StatementKind.DECL,),
        'is_expr': (StatementKind.EXPR,),
        'is_snippet': (StatementKind.SNIPPET,),
        'is_return': (StatementKind.RETURN,),
        'is_comment': (StatementKind.COMMENT,),
        'is_import': (StatementKind.IMPORT, StatementKind.IMPORT_FROM),
        'is_import_from': (StatementKind.IMPORT_FROM,),
        'is_if_else': (StatementKind.IF_ELSE,),
        'is_for': (StatementKind.FOR,),
        'is_while': (StatementKind.WHILE,),
        'is_try_except': (StatementKind.TRY_EXCEPT,),
        'is_with': (StatementKind.WITH,),
        'is_raise': (StatementKind.RAISE,),
        'is_assert': (StatementKind.ASSERT,),
        'is_pass': (StatementKind.PASS,),
        'is_continue': (StatementKind.CONTINUE,),
        'is_break': (StatementKind.BREAK,),
        'is_del': (StatementKind.DEL,),
    }

    # Each listed kind sets its flag.
    for flag, kinds in flag_kinds.items():
        for kind in kinds:
            assert getattr(Statement(kind=kind), flag) is True

# ** test: statement_kind_property_false
def test_statement_kind_property_false() -> None:
    '''
    Test that cross-kind flags are false and print has no is_print flag.
    '''

    # An expression statement does not set unrelated flags.
    expression = Statement(kind=StatementKind.EXPR)
    for flag in (
        'is_artifact',
        'is_decl',
        'is_snippet',
        'is_return',
        'is_comment',
        'is_import',
        'is_import_from',
        'is_if_else',
        'is_for',
        'is_while',
        'is_try_except',
        'is_with',
        'is_raise',
        'is_assert',
        'is_pass',
        'is_continue',
        'is_break',
        'is_del',
    ):
        assert getattr(expression, flag) is False

    # Print and block remain enum-only.
    assert 'is_print' not in Statement.model_fields
    assert 'is_block' not in Statement.model_fields
    assert not hasattr(Statement(kind=StatementKind.PRINT), 'is_print')

# ** test: statement_is_import
def test_statement_is_import() -> None:
    '''
    Test that import sets only is_import and import-from sets both flags.
    '''

    # A plain import is not an import-from.
    imported = Statement(kind=StatementKind.IMPORT)
    assert imported.is_import is True
    assert imported.is_import_from is False

    # An import-from is both.
    imported_from = Statement(kind=StatementKind.IMPORT_FROM)
    assert imported_from.is_import is True
    assert imported_from.is_import_from is True

# ** test: declaration_kind_properties
def test_declaration_kind_properties() -> None:
    '''
    Test that a declaration type kind drives is_class and is_func.
    '''

    # A class type drives is_class only.
    class_decl = Declaration(name='Foo', type=Type(kind=TypeKind.CLASS, name='Foo'))
    assert class_decl.is_class is True
    assert class_decl.is_func is False

    # A function type drives is_func only.
    func_decl = Declaration(name='run', type=Type(kind=TypeKind.FUNC))
    assert func_decl.is_class is False
    assert func_decl.is_func is True

    # A string type drives neither flag.
    value_decl = Declaration(name='answer', type=Type(kind=TypeKind.STR))
    assert value_decl.is_class is False
    assert value_decl.is_func is False

# ** test: expression_classification_rederives_on_assignment
def test_expression_classification_rederives_on_assignment() -> None:
    '''
    Test that assigning kind rederives expression classification flags.
    '''

    # Start from a self attribute name.
    expression = Expression(kind=ExprKind.NAME, name='self.x')
    assert expression.is_name_ref is True
    assert expression.is_self_attribute is True
    assert expression.is_binary_op is False

    # Assigning an addition kind rederives the flags.
    expression.kind = ExprKind.ADD
    assert expression.is_binary_op is True
    assert expression.is_name_ref is False
    assert expression.is_self_attribute is False
    assert expression.is_literal is False

# ** test: declaration_classification_rederives_on_assignment
def test_declaration_classification_rederives_on_assignment() -> None:
    '''
    Test that assigning type rederives declaration classification flags.
    '''

    # Start from a non-class type.
    declaration = Declaration(name='answer', type=Type(kind=TypeKind.STR))
    assert declaration.is_class is False
    assert declaration.is_func is False

    # Assigning a class type rederives is_class.
    declaration.type = Type(kind=TypeKind.CLASS, name='Answer')
    assert declaration.is_class is True
    assert declaration.is_func is False

    # Assigning a function type rederives is_func.
    declaration.type = Type(kind=TypeKind.FUNC)
    assert declaration.is_class is False
    assert declaration.is_func is True

# ** test: statement_classification_rederives_on_assignment
def test_statement_classification_rederives_on_assignment() -> None:
    '''
    Test that assigning kind rederives statement classification flags.
    '''

    # Start from an expression statement.
    statement = Statement(kind=StatementKind.EXPR)
    assert statement.is_expr is True
    assert statement.is_return is False

    # Assigning a return kind rederives the flags.
    statement.kind = StatementKind.RETURN
    assert statement.is_return is True
    assert statement.is_expr is False

# ** test: expression_children_and_visit_role
def test_expression_children_and_visit_role(binary_add_expression: Expression) -> None:
    '''
    Test that a binary expression walks left then right and reports its kind value.

    :param binary_add_expression: The addition fixture.
    :type binary_add_expression: Expression
    '''

    # Children are the left operand, then the right operand.
    assert binary_add_expression.children == [
        binary_add_expression.left,
        binary_add_expression.right,
    ]

    # The visit role is the kind value.
    assert binary_add_expression.visit_role == binary_add_expression.kind.value
    assert binary_add_expression.visit_role == 'add'

# ** test: flatten_call_args
def test_flatten_call_args() -> None:
    '''
    Test that a nested argument list flattens left to right and a non-list returns itself.
    '''

    # Build a nested argument list around three leaves.
    first = Expression(kind=ExprKind.NAME, name='a')
    second = Expression(kind=ExprKind.NAME, name='b')
    third = Expression(kind=ExprKind.NAME, name='c')
    nested = Expression(
        kind=ExprKind.ARGS_LIST,
        left=Expression(kind=ExprKind.ARGS_LIST, left=first, right=second),
        right=third,
    )

    # The list flattens left to right, and a leaf returns itself.
    assert nested.flatten_call_args() == [first, second, third]
    assert first.flatten_call_args() == [first]

# ** test: expression_encode_table
def test_expression_encode_table() -> None:
    '''
    Test every expression encode row, including the name-star hack and empty f-string.
    '''

    # Shared children so pair encodings are readable.
    left = Expression(kind=ExprKind.NAME, name='a')
    right = Expression(kind=ExprKind.NAME, name='b')

    def pair(kind: ExprKind) -> Expression:
        '''Build an expression with the shared children.'''

        return Expression(kind=kind, left=left, right=right)

    # Name forms, including the star hack.
    assert Expression(kind=ExprKind.NAME, value='**', left=left, right=right).encode() == 'Exp(a, b)'
    assert Expression(kind=ExprKind.NAME, name='foo', value='bar').encode() == 'foo'
    assert Expression(kind=ExprKind.NAME, value='bar').encode() == 'bar'
    assert Expression(kind=ExprKind.NAME).encode() == ''

    # Attribute and literal forms.
    assert Expression(kind=ExprKind.ATTRIBUTE, name='x', left=left).encode() == 'Attr(a, x)'
    assert Expression(kind=ExprKind.INT_VAL, value='1').encode() == '1'
    assert Expression(kind=ExprKind.NUM_VAL, value='1.5').encode() == '1.5'
    assert Expression(kind=ExprKind.STR_VAL, value='hi').encode() == 'hi'
    assert Expression(kind=ExprKind.BOOL_VAL, value='True').encode() == 'True'
    assert Expression(kind=ExprKind.NONE_VAL, value='None').encode() == 'None'
    assert Expression(kind=ExprKind.ELLIPSIS_VAL, value='...').encode() == '...'
    assert Expression(kind=ExprKind.INT_VAL).encode() == ''

    # Binary, comparison, and unary forms.
    assert pair(ExprKind.ASSIGN).encode() == 'Assign(a, b)'
    assert pair(ExprKind.ADD).encode() == 'Add(a, b)'
    assert pair(ExprKind.SUB).encode() == 'Sub(a, b)'
    assert pair(ExprKind.MUL).encode() == 'Mul(a, b)'
    assert pair(ExprKind.DIV).encode() == 'Div(a, b)'
    assert pair(ExprKind.MOD).encode() == 'Mod(a, b)'
    assert pair(ExprKind.EXP).encode() == 'Exp(a, b)'
    assert pair(ExprKind.FLOORDIV).encode() == 'FloorDiv(a, b)'
    assert pair(ExprKind.EQ).encode() == 'Eq(a, b)'
    assert pair(ExprKind.NEQ).encode() == 'Neq(a, b)'
    assert pair(ExprKind.LT).encode() == 'Lt(a, b)'
    assert pair(ExprKind.LTE).encode() == 'Lte(a, b)'
    assert pair(ExprKind.GT).encode() == 'Gt(a, b)'
    assert pair(ExprKind.GTE).encode() == 'Gte(a, b)'
    assert pair(ExprKind.AND).encode() == 'And(a, b)'
    assert pair(ExprKind.OR).encode() == 'Or(a, b)'
    assert Expression(kind=ExprKind.NOT, left=left).encode() == 'Not(a)'
    assert pair(ExprKind.IS).encode() == 'Is(a, b)'
    assert pair(ExprKind.IS_NOT).encode() == 'IsNot(a, b)'
    assert pair(ExprKind.IN).encode() == 'In(a, b)'
    assert pair(ExprKind.NOT_IN).encode() == 'NotIn(a, b)'
    assert Expression(kind=ExprKind.UNARY_MINUS, left=left).encode() == 'Neg(a)'
    assert Expression(kind=ExprKind.LIST_LITERAL, left=left).encode() == 'List(a)'
    assert Expression(kind=ExprKind.DICT_LITERAL, left=left).encode() == 'Dict(a)'
    assert Expression(kind=ExprKind.SET_LITERAL, left=left).encode() == 'Set(a)'
    assert pair(ExprKind.DICT_ENTRY).encode() == 'a: b'
    assert Expression(kind=ExprKind.TUPLE, left=left).encode() == 'Tuple(a)'
    assert pair(ExprKind.SUBSCRIPT).encode() == 'Subscript(a, b)'
    assert pair(ExprKind.SLICE).encode() == 'Slice(a:b)'
    assert pair(ExprKind.TERNARY).encode() == 'Ternary(a, b)'
    assert pair(ExprKind.COMPREHENSION).encode() == 'Comp(a, b)'
    assert pair(ExprKind.FOR_COMP).encode() == 'for a in b'
    assert Expression(kind=ExprKind.AWAIT, left=left).encode() == 'Await(a)'
    assert Expression(kind=ExprKind.KWARG, name='key', left=left).encode() == 'key=a'
    assert Expression(kind=ExprKind.STAR_EXPR, left=left).encode() == '*a'
    assert Expression(kind=ExprKind.DOUBLE_STAR_EXPR, left=left).encode() == '**a'

    # Import, call, argument-list, comment, and empty forms.
    assert pair(ExprKind.IMPORT_AS).encode() == 'a as b'
    assert Expression(kind=ExprKind.IMPORT_AS, left=left).encode() == 'a'
    assert pair(ExprKind.CALL).encode() == 'Call(a, b)'
    assert Expression(kind=ExprKind.CALL, left=left).encode() == 'Call(a)'
    assert pair(ExprKind.ARGS_LIST).encode() == 'a, b'
    assert Expression(kind=ExprKind.ARGS_LIST, left=left).encode() == 'a'
    assert Expression(kind=ExprKind.ARGS_LIST).encode() == ''
    assert Expression(kind=ExprKind.COMMENT, value='note').encode() == 'note'
    assert Expression(kind=ExprKind.COMMENT).encode() == ''
    assert Expression(kind=ExprKind.FSTRING).encode() == ''
    assert Expression(kind=ExprKind.ARTIFACT).encode() == ''
    assert Expression(kind=ExprKind.IMPORT).encode() == ''
    assert Expression(kind=ExprKind.IMPORT_MULTI).encode() == ''

# ** test: declaration_inner_members_has_method_encode
def test_declaration_inner_members_has_method_encode() -> None:
    '''
    Test inner declarations, artifact members, has_method, and Def encoding.
    '''

    # The first declaration statement is the inner declaration, even if it is not a member.
    plain = Declaration(name='plain')
    run = Declaration(name='run')
    init = Declaration(name='__init__')
    method = ArtifactDeclaration(
        name='run_header',
        artifact_type='ARTIFACT_MEMBER',
        artifact_role='method',
        code=[Statement(kind=StatementKind.DECL, decl=run)],
    )
    initializer = ArtifactDeclaration(
        name='init_header',
        artifact_type='ARTIFACT_MEMBER',
        artifact_role='init',
        code=[Statement(kind=StatementKind.DECL, decl=init)],
    )
    attribute = ArtifactDeclaration(
        name='attr_header',
        artifact_type='ARTIFACT_MEMBER',
        artifact_role='attribute',
    )
    section = ArtifactDeclaration(name='events', artifact_type='** event')
    outer = Declaration(
        name='Foo',
        type=Type(
            kind=TypeKind.FUNC,
            params=[
                ParamList(name='self'),
                ParamList(name='a'),
                ParamList(name='b'),
            ],
        ),
        code=[
            Statement(kind=StatementKind.DECL, decl=plain),
            Statement(kind=StatementKind.DECL, decl=method),
            Statement(kind=StatementKind.DECL, decl=initializer),
            Statement(kind=StatementKind.DECL, decl=attribute),
            Statement(kind=StatementKind.EXPR),
        ],
    )

    # Inner declaration, members, and method lookup follow the body order.
    assert outer.inner_decl is plain
    assert outer.members == [method, initializer, attribute]
    assert outer.has_method('run') is True
    assert outer.has_method('__init__') is True
    assert outer.has_method('missing') is False
    assert outer.children == list(outer.code)

    # Encoding drops self and reports the remaining parameter names.
    assert outer.encode() == 'Def(Foo, [a, b])'
    assert Declaration(name='Foo').encode() == 'Def(Foo, [])'
    assert Declaration(name='').encode() == ''

    # Visit role uses an inherited artifact role or section keyword, not a new classification.
    assert outer.visit_role is None
    assert method.visit_role == 'method'
    assert section.visit_role == 'event'

# ** test: statement_children_visit_role_encode
def test_statement_children_visit_role_encode() -> None:
    '''
    Test statement walk order, visit role, class lookup, and every encode row.
    '''

    # Children follow scalar fields, then each body list.
    decl = Declaration(name='nested')
    init_expr = Expression(kind=ExprKind.NAME, name='init')
    expr = Expression(kind=ExprKind.NAME, name='expr')
    next_expr = Expression(kind=ExprKind.NAME, name='next')
    body_stmt = Statement(kind=StatementKind.PASS)
    else_stmt = Statement(kind=StatementKind.BREAK)
    finally_stmt = Statement(kind=StatementKind.CONTINUE)
    statement = Statement(
        kind=StatementKind.TRY_EXCEPT,
        decl=decl,
        init_expr=init_expr,
        expr=expr,
        next_expr=next_expr,
        body=[body_stmt],
        else_body=[else_stmt],
        finally_body=[finally_stmt],
    )
    assert statement.children == [
        decl,
        init_expr,
        expr,
        next_expr,
        body_stmt,
        else_stmt,
        finally_stmt,
    ]
    assert statement.visit_role == 'try_except'

    # find_class returns a class declaration and skips a class-typed variable.
    class_decl = Declaration(name='Foo', type=Type(kind=TypeKind.CLASS, name='Foo'))
    variable = Declaration(name='foo', type=Type(kind=TypeKind.CLASS, name='Foo'))
    wrapper = Statement(
        kind=StatementKind.BLOCK,
        body=[
            Statement(kind=StatementKind.DECL, decl=variable),
            Statement(kind=StatementKind.DECL, decl=class_decl),
        ],
    )
    assert wrapper.find_class() is class_decl
    assert Statement(kind=StatementKind.BLOCK).find_class() is None

    # Encode each statement row, including else, finally, and empty comment.
    cond = Expression(kind=ExprKind.NAME, name='cond')
    passed = Statement(kind=StatementKind.PASS)
    broken = Statement(kind=StatementKind.BREAK)
    continued = Statement(kind=StatementKind.CONTINUE)
    typed_handler = Statement(
        kind=StatementKind.EXPR,
        expr=Expression(kind=ExprKind.NAME, name='ValueError'),
        body=[passed],
    )
    bare_handler = Statement(kind=StatementKind.EXPR, body=[broken])
    assert Statement(kind=StatementKind.RETURN, expr=cond).encode() == 'Return(cond)'
    assert Statement(kind=StatementKind.RETURN).encode() == 'Return()'
    assert Statement(kind=StatementKind.EXPR, expr=cond).encode() == 'cond'
    assert Statement(kind=StatementKind.EXPR).encode() == ''
    assert Statement(
        kind=StatementKind.IF_ELSE,
        expr=cond,
        body=[passed],
        else_body=[broken],
    ).encode() == 'If(cond, [Pass()], else=[Break()])'
    assert Statement(kind=StatementKind.IF_ELSE, expr=cond, body=[passed]).encode() == 'If(cond, [Pass()])'
    assert Statement(
        kind=StatementKind.FOR,
        init_expr=Expression(kind=ExprKind.NAME, name='i'),
        expr=Expression(kind=ExprKind.NAME, name='items'),
        body=[passed],
    ).encode() == 'For(i, items, [Pass()])'
    assert Statement(kind=StatementKind.WHILE, expr=cond, body=[passed]).encode() == 'While(cond, [Pass()])'
    assert Statement(
        kind=StatementKind.TRY_EXCEPT,
        body=[passed],
        else_body=[typed_handler, bare_handler],
        finally_body=[continued],
    ).encode() == (
        'TryExcept(try=[Pass()], handlers=[Except(ValueError, [Pass()]), Except([Break()])], '
        'finally=[Continue()])'
    )
    assert Statement(
        kind=StatementKind.TRY_EXCEPT,
        body=[passed],
        else_body=[typed_handler],
    ).encode() == 'TryExcept(try=[Pass()], handlers=[Except(ValueError, [Pass()])])'
    assert Statement(
        kind=StatementKind.WITH,
        expr=Expression(kind=ExprKind.NAME, name='open'),
        init_expr=Expression(kind=ExprKind.NAME, name='fh'),
        body=[passed],
    ).encode() == 'With(open, fh, [Pass()])'
    assert Statement(
        kind=StatementKind.WITH,
        expr=Expression(kind=ExprKind.NAME, name='open'),
        body=[passed],
    ).encode() == 'With(open, [Pass()])'
    assert Statement(kind=StatementKind.RAISE, expr=cond).encode() == 'Raise(cond)'
    assert Statement(kind=StatementKind.RAISE).encode() == 'Raise()'
    assert Statement(
        kind=StatementKind.ASSERT,
        expr=cond,
        init_expr=Expression(kind=ExprKind.STR_VAL, value='nope'),
    ).encode() == 'Assert(cond, nope)'
    assert Statement(kind=StatementKind.ASSERT, expr=cond).encode() == 'Assert(cond)'
    assert passed.encode() == 'Pass()'
    assert Statement(kind=StatementKind.CONTINUE).encode() == 'Continue()'
    assert broken.encode() == 'Break()'
    assert Statement(kind=StatementKind.DEL, expr=cond).encode() == 'Del(cond)'
    assert Statement(kind=StatementKind.DECL, decl=Declaration(name='Foo')).encode() == 'Def(Foo, [])'
    assert Statement(kind=StatementKind.DECL).encode() == ''
    assert Statement(kind=StatementKind.COMMENT).encode() == ''
    assert Statement(kind=StatementKind.SNIPPET).encode() == ''
    assert Statement(kind=StatementKind.ARTIFACT).encode() == ''
    assert Statement(kind=StatementKind.IMPORT).encode() == ''
    assert Statement(kind=StatementKind.PRINT).encode() == ''
    assert Statement(kind=StatementKind.BLOCK).encode() == ''

# ** test: encode_block_and_handlers
def test_encode_block_and_handlers() -> None:
    '''
    Test that encode_block drops empty encodings and encode_handlers formats Except.
    '''

    # Empty input and empty encodings yield an empty block.
    comment = Statement(kind=StatementKind.COMMENT)
    passed = Statement(kind=StatementKind.PASS)
    assert encode_block(None) == '[]'
    assert encode_block([]) == '[]'
    assert encode_block([comment, passed, comment]) == '[Pass()]'

    # Handlers format with an exception type and without one.
    typed = Statement(
        kind=StatementKind.EXPR,
        expr=Expression(kind=ExprKind.NAME, name='ValueError'),
        body=[passed],
    )
    bare = Statement(kind=StatementKind.EXPR, body=[Statement(kind=StatementKind.BREAK)])
    assert encode_handlers(None) == '[]'
    assert encode_handlers([typed, bare]) == '[Except(ValueError, [Pass()]), Except([Break()])]'

# ** test: no_next_pointer
def test_no_next_pointer() -> None:
    '''
    Test that expression, declaration, and statement models do not declare next.
    '''

    # None of the structural models, nor the type models, declare next.
    for model in (Expression, Declaration, Statement, ParamList, Type):
        assert 'next' not in model.model_fields
        assert 'next' not in model.__annotations__
