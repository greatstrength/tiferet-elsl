"""Compiler Common Conformance Checker Tests"""

# *** imports

# ** core
import inspect

# ** app
from ...domain.ast import ExprKind, TypeKind
from ...mappers.artifact import (
    ArtifactDeclarationAggregate,
    ArtifactStatementAggregate,
)
from ...mappers.ast import (
    DeclarationAggregate,
    ExpressionAggregate,
    ParamListAggregate,
    StatementAggregate,
    TypeAggregate,
)
from ..semantic import SymbolTableBuilder
from ...blueprints.core import build_cache
from ...contexts.provision import COMPILER_PROVISION_CACHE_PREFIX
from ..typecheck import ConformanceChecker
import compiler.utils.typecheck as typecheck

# *** functions

# ** function: _provision_cache
def _provision_cache():
    '''
    Return one cache seeded by the compiler blueprint.

    :return: The seeded cache.
    :rtype: Any
    '''

    # Dialect tests read the seed. They do not rebuild the deleted lists.
    if not hasattr(_provision_cache, 'cache'):
        _provision_cache.cache = build_cache()
    return _provision_cache.cache

# ** function: _module
def _module(code: list) -> DeclarationAggregate:
    '''
    Create a module declaration.

    :param code: The module statements.
    :type code: list
    :return: The module declaration.
    :rtype: DeclarationAggregate
    '''

    # The module body is the statement list the checker starts from.
    return DeclarationAggregate.new_module_decl(name='sample', code=code)

# ** function: _decl
def _decl(decl) -> StatementAggregate:
    '''
    Wrap a declaration in a declaration statement.

    :param decl: The declaration.
    :type decl: DeclarationAggregate
    :return: The declaration statement.
    :rtype: StatementAggregate
    '''

    # Walkers dispatch declaration statements, not bare declarations.
    return StatementAggregate.new_decl_stmt(decl)

# ** function: _group
def _group(name: str, body: list) -> ArtifactStatementAggregate:
    '''
    Create a tier-1 artifact group.

    :param name: The group name.
    :type name: str
    :param body: The group body.
    :type body: list
    :return: The artifact statement.
    :rtype: ArtifactStatementAggregate
    '''

    # A tier-1 header uses the triple-star marker.
    header = ArtifactDeclarationAggregate.new_artifact_decl(
        name=name,
        artifact_type='***',
    )
    return ArtifactStatementAggregate.new_artifact_stmt(header, body)

# ** function: _section
def _section(artifact_type: str, name: str,
             body: list) -> ArtifactStatementAggregate:
    '''
    Create a tier-2 artifact section.

    :param artifact_type: The section marker, including its keyword.
    :type artifact_type: str
    :param name: The section name.
    :type name: str
    :param body: The section body.
    :type body: list
    :return: The artifact statement.
    :rtype: ArtifactStatementAggregate
    '''

    # The marker carries the section keyword. The name is the declared identifier.
    header = ArtifactDeclarationAggregate.new_artifact_decl(
        name=name,
        artifact_type=artifact_type,
    )
    return ArtifactStatementAggregate.new_artifact_stmt(header, body)

# ** function: _import_section
def _import_section(name: str, body: list) -> ArtifactStatementAggregate:
    '''
    Create an import-group section.

    :param name: The import group name.
    :type name: str
    :param body: The section body.
    :type body: list
    :return: The artifact statement.
    :rtype: ArtifactStatementAggregate
    '''

    # Import sections are bare tier-2 headers, not keyword sections.
    header = ArtifactDeclarationAggregate.new_artifact_decl(
        name=name,
        artifact_type='**',
    )
    return ArtifactStatementAggregate.new_artifact_stmt(header, body)

# ** function: _import
def _import(name: str) -> StatementAggregate:
    '''
    Create a plain import statement.

    :param name: The imported name.
    :type name: str
    :return: The import statement.
    :rtype: StatementAggregate
    '''

    # The imported name is a name expression.
    return StatementAggregate.new_import_stmt(
        ExpressionAggregate.new_name_expr(name),
    )

# ** function: _func
def _func(name: str, params: list = None,
          return_kind: TypeKind = None) -> DeclarationAggregate:
    '''
    Create a function declaration.

    :param name: The function name.
    :type name: str
    :param params: The parameters, or None.
    :type params: list
    :param return_kind: The optional return-type kind.
    :type return_kind: TypeKind
    :return: The function declaration.
    :rtype: DeclarationAggregate
    '''

    # A missing return kind leaves the return type unset.
    return_type = None
    if return_kind is not None:
        return_type = TypeAggregate.new(kind=return_kind)

    # The function type is what marks the declaration as a function.
    return DeclarationAggregate.new_func_decl(
        name=name,
        type=TypeAggregate.new_func_type(
            params=params or [],
            return_type=return_type,
        ),
        body=[],
    )

# ** function: _attr
def _attr(name: str, kind: TypeKind = None,
          class_name: str = None) -> DeclarationAggregate:
    '''
    Create an attribute declaration.

    :param name: The attribute name.
    :type name: str
    :param kind: The optional primitive type kind.
    :type kind: TypeKind
    :param class_name: The optional class type name.
    :type class_name: str
    :return: The attribute declaration.
    :rtype: DeclarationAggregate
    '''

    # A class name wins over a primitive kind.
    types = None
    if class_name is not None:
        types = TypeAggregate.new_class_type(name=class_name)
    elif kind is not None:
        types = TypeAggregate.new(kind=kind)

    # The annotation is what the builder records.
    return DeclarationAggregate.new_attr_decl(name=name, types=types)

# ** function: _member
def _member(role: str, body: list,
            qualifier: str = None) -> StatementAggregate:
    '''
    Wrap an artifact member in a declaration statement.

    :param role: The member role.
    :type role: str
    :param body: The member body statements.
    :type body: list
    :param qualifier: The optional parenthetical qualifier.
    :type qualifier: str
    :return: The declaration statement.
    :rtype: StatementAggregate
    '''

    # The role is both the member name and the artifact role.
    return _decl(ArtifactDeclarationAggregate.new_member_decl(
        role,
        member_body=body,
        qualifier=qualifier,
    ))

# ** function: _decorator
def _decorator(name: str) -> StatementAggregate:
    '''
    Create a bare decorator expression statement.

    :param name: The decorator name.
    :type name: str
    :return: The expression statement.
    :rtype: StatementAggregate
    '''

    # A bare name encodes as the decorator string the member rule matches.
    return StatementAggregate.new_expr_stmt(
        ExpressionAggregate.new_name_expr(name),
    )

# ** function: _model_validator
def _model_validator() -> StatementAggregate:
    '''
    Create a ``@model_validator`` decorator expression statement.

    :return: The expression statement.
    :rtype: StatementAggregate
    '''

    # The call encoding starts with Call(model_validator.
    return StatementAggregate.new_expr_stmt(
        ExpressionAggregate.new_call_expr(
            ExpressionAggregate.new_name_expr('model_validator'),
        ),
    )

# ** function: _int
def _int(value: str) -> ExpressionAggregate:
    '''
    Create an integer literal.

    :param value: The literal text.
    :type value: str
    :return: The integer expression.
    :rtype: ExpressionAggregate
    '''

    # INT_VAL infers as int. NUM_VAL would infer as float.
    return ExpressionAggregate(kind=ExprKind.INT_VAL, value=value)

# ** function: _str
def _str(value: str) -> ExpressionAggregate:
    '''
    Create a string literal.

    :param value: The literal text.
    :type value: str
    :return: The string expression.
    :rtype: ExpressionAggregate
    '''

    # The stored text is the inferred string value.
    return ExpressionAggregate(kind=ExprKind.STR_VAL, value=value)

# ** function: _assign
def _assign(name: str, value: ExpressionAggregate) -> StatementAggregate:
    '''
    Create an assignment expression statement.

    :param name: The target name.
    :type name: str
    :param value: The assigned expression.
    :type value: ExpressionAggregate
    :return: The expression statement.
    :rtype: StatementAggregate
    '''

    # The target is a name so lookup can read its declared type.
    return StatementAggregate.new_expr_stmt(
        ExpressionAggregate.new_assign_expr(
            target=ExpressionAggregate.new_name_expr(name),
            value=value,
        ),
    )

# ** function: _binop
def _binop(operator: str, left: ExpressionAggregate,
           right: ExpressionAggregate) -> StatementAggregate:
    '''
    Create a binary-operation expression statement.

    :param operator: The operator text.
    :type operator: str
    :param left: The left operand.
    :type left: ExpressionAggregate
    :param right: The right operand.
    :type right: ExpressionAggregate
    :return: The expression statement.
    :rtype: StatementAggregate
    '''

    # The operator text selects the expression kind.
    return StatementAggregate.new_expr_stmt(
        ExpressionAggregate.new_operator_expr(
            operator=operator,
            left=left,
            right=right,
        ),
    )

# ** function: _codes
def _codes(module: DeclarationAggregate) -> list:
    '''
    Build a symbol table, then check the module with the common rule set.

    :param module: The module declaration.
    :type module: DeclarationAggregate
    :return: Finding codes, in walk order.
    :rtype: list
    '''

    # Typing lookup reads the live registry, not the dumped build dict.
    cache = _provision_cache()
    builder = SymbolTableBuilder(cache, COMPILER_PROVISION_CACHE_PREFIX)
    builder.build(module)
    findings = ConformanceChecker(
        builder.scopes,
        cache,
        'common.',
        COMPILER_PROVISION_CACHE_PREFIX,
    ).check(module)
    return [item['error_code'] for item in findings]

# *** tests

# ** test: import_group_satisfied_for_core_infra_app
def test_import_group_satisfied_for_core_infra_app() -> None:
    '''
    Test that core, infra, and app import sections yield no findings.
    '''

    # Each permitted group contains only an import.
    module = _module([
        _group('imports', [
            _import_section('core', [_import('typing')]),
            _import_section('infra', [_import('yaml')]),
            _import_section('app', [_import('compiler')]),
        ]),
    ])

    # Valid groups and import-only content are satisfactory.
    assert _codes(module) == []

# ** test: import_group_violated_for_unknown_group
def test_import_group_violated_for_unknown_group() -> None:
    '''
    Test that an unknown import section name yields INVALID_IMPORT_GROUP.
    '''

    # The section contains an import, so only the group name is wrong.
    module = _module([
        _group('imports', [
            _import_section('vendor', [_import('yaml')]),
        ]),
    ])

    # The unknown group is the only finding.
    assert _codes(module) == ['INVALID_IMPORT_GROUP']

# ** test: import_group_violated_for_non_import_content
def test_import_group_violated_for_non_import_content() -> None:
    '''
    Test that a non-import statement in an import section yields INVALID_IMPORT_CONTENT.
    '''

    # The group name is permitted. The pass statement is not an import.
    module = _module([
        _group('imports', [
            _import_section('core', [StatementAggregate.new_pass_stmt()]),
        ]),
    ])

    # Non-import content is the only finding.
    assert _codes(module) == ['INVALID_IMPORT_CONTENT']

# ** test: section_class_name_satisfied_on_match
def test_section_class_name_satisfied_on_match() -> None:
    '''
    Test that a snake-case section and a matching PascalCase class yield no findings.
    '''

    # ping expects class Ping.
    module = _module([
        _section('** model', 'ping', [
            _decl(DeclarationAggregate.new_class_decl(
                name='Ping',
                subclasses=None,
                doc_string=None,
                members=[],
            )),
        ]),
    ])

    # The class name matches the section name.
    assert _codes(module) == []

# ** test: section_class_name_violated_on_mismatch
def test_section_class_name_violated_on_mismatch() -> None:
    '''
    Test that a section and class name mismatch yields ARTIFACT_CLASS_NAME_MISMATCH.
    '''

    # ping expects Ping, not Other.
    module = _module([
        _section('** model', 'ping', [
            _decl(DeclarationAggregate.new_class_decl(
                name='Other',
                subclasses=None,
                doc_string=None,
                members=[],
            )),
        ]),
    ])

    # The mismatch is the only finding.
    assert _codes(module) == ['ARTIFACT_CLASS_NAME_MISMATCH']

# ** test: function_section_name_satisfied_on_match
def test_function_section_name_satisfied_on_match() -> None:
    '''
    Test that a function section whose def matches the header yields no findings.
    '''

    # The section name and the def name are the same.
    module = _module([
        _section('** function', 'build_app', [
            _decl(_func('build_app')),
        ]),
    ])

    # A matching def is satisfactory.
    assert _codes(module) == []

# ** test: function_section_name_violated_on_mismatch
def test_function_section_name_violated_on_mismatch() -> None:
    '''
    Test that a function section name mismatch yields FUNCTION_NAME_MISMATCH.
    '''

    # The section expects def build_app.
    module = _module([
        _section('** function', 'build_app', [
            _decl(_func('other')),
        ]),
    ])

    # The mismatch is the only finding.
    assert _codes(module) == ['FUNCTION_NAME_MISMATCH']

# ** test: attribute_member_satisfied_for_variable_declaration
def test_attribute_member_satisfied_for_variable_declaration() -> None:
    '''
    Test that a variable attribute member yields no findings.
    '''

    # An integer variable is a permitted attribute member.
    module = _module([
        _member('attribute', [_decl(_attr('count', kind=TypeKind.INT))]),
    ])

    # A variable member is satisfactory.
    assert _codes(module) == []

# ** test: attribute_member_satisfied_for_class_typed_variable
def test_attribute_member_satisfied_for_class_typed_variable() -> None:
    '''
    Test that a class-typed variable whose name differs from its type yields no findings.
    '''

    # The variable name is not the class name, so this is not a nested class.
    module = _module([
        _member('attribute', [
            _decl(_attr('service', class_name='ErrorService')),
        ]),
    ])

    # A class-typed variable is satisfactory.
    assert _codes(module) == []

# ** test: attribute_member_violated_for_function_declaration
def test_attribute_member_violated_for_function_declaration() -> None:
    '''
    Test that a function under attribute yields INVALID_ATTRIBUTE_MEMBER_TYPE.
    '''

    # An attribute member must wrap a variable, not a function.
    module = _module([
        _member('attribute', [_decl(_func('count'))]),
    ])

    # The illegal function is the only finding.
    assert _codes(module) == ['INVALID_ATTRIBUTE_MEMBER_TYPE']

# ** test: attribute_member_violated_for_nested_class_declaration
def test_attribute_member_violated_for_nested_class_declaration() -> None:
    '''
    Test that a nested class under attribute yields INVALID_ATTRIBUTE_MEMBER_TYPE.
    '''

    # A class whose name equals its type name is a nested class, not a variable.
    module = _module([
        _member('attribute', [
            _decl(DeclarationAggregate.new_class_decl(
                name='Inner',
                subclasses=None,
                doc_string=None,
                members=[],
            )),
        ]),
    ])

    # The nested class is the only finding.
    assert _codes(module) == ['INVALID_ATTRIBUTE_MEMBER_TYPE']

# ** test: method_member_undecorated_missing_self_violated
def test_method_member_undecorated_missing_self_violated() -> None:
    '''
    Test that an undecorated method without self yields METHOD_MISSING_SELF.
    '''

    # No decorator and no first parameter.
    module = _module([
        _member('method', [_decl(_func('execute'))]),
    ])

    # The missing receiver is the only finding.
    assert _codes(module) == ['METHOD_MISSING_SELF']

# ** test: method_member_not_func_violated
def test_method_member_not_func_violated() -> None:
    '''
    Test that a non-function under method yields INVALID_METHOD_MEMBER_TYPE.
    '''

    # A variable is not a method.
    module = _module([
        _member('method', [_decl(_attr('count', kind=TypeKind.INT))]),
    ])

    # The illegal member type is the only finding.
    assert _codes(module) == ['INVALID_METHOD_MEMBER_TYPE']

# ** test: staticmethod_needs_no_self_or_cls
def test_staticmethod_needs_no_self_or_cls() -> None:
    '''
    Test that a static method with no self or cls yields no findings.
    '''

    # The qualifier and the decorator agree, so no receiver is required.
    module = _module([
        _member('method', [
            _decorator('staticmethod'),
            _decl(_func('build')),
        ], qualifier='static'),
    ])

    # A matching static method is satisfactory.
    assert _codes(module) == []

# ** test: classmethod_with_cls_satisfied
def test_classmethod_with_cls_satisfied() -> None:
    '''
    Test that a classmethod with cls yields no findings.
    '''

    # cls is the required first parameter.
    module = _module([
        _member('method', [
            _decorator('classmethod'),
            _decl(_func('build', params=[ParamListAggregate.new('cls')])),
        ]),
    ])

    # A classmethod with cls is satisfactory.
    assert _codes(module) == []

# ** test: classmethod_missing_cls_violated
def test_classmethod_missing_cls_violated() -> None:
    '''
    Test that a classmethod without cls or mcs yields METHOD_MISSING_CLS.
    '''

    # The decorator requires cls. There is no first parameter.
    module = _module([
        _member('method', [
            _decorator('classmethod'),
            _decl(_func('build')),
        ]),
    ])

    # The missing cls receiver is the only finding.
    assert _codes(module) == ['METHOD_MISSING_CLS']

# ** test: validator_member_satisfied
def test_validator_member_satisfied() -> None:
    '''
    Test that a validator with both decorators and a non-None return yields no findings.
    '''

    # Both required decorators are present, and the return type is not None.
    module = _module([
        _member('method', [
            _model_validator(),
            _decorator('classmethod'),
            _decl(_func(
                'check',
                params=[ParamListAggregate.new('cls')],
                return_kind=TypeKind.STR,
            )),
        ], qualifier='validator'),
    ])

    # A well-formed validator is satisfactory.
    assert _codes(module) == []

# ** test: validator_member_missing_decorators_violated
def test_validator_member_missing_decorators_violated() -> None:
    '''
    Test that a validator without both decorators yields INVALID_VALIDATOR_MEMBER.
    '''

    # self avoids a receiver finding. Neither required decorator is present.
    module = _module([
        _member('method', [
            _decl(_func('check', params=[ParamListAggregate.new('self')])),
        ], qualifier='validator'),
    ])

    # The missing decorators are the only finding.
    assert _codes(module) == ['INVALID_VALIDATOR_MEMBER']

# ** test: assignment_type_mismatch
def test_assignment_type_mismatch() -> None:
    '''
    Test that an incompatible assignment yields TYPE_MISMATCH_ASSIGNMENT.
    '''

    # count is declared str and assigned an int.
    module = _module([
        _decl(_attr('count', kind=TypeKind.STR)),
        _assign('count', _int('1')),
    ])

    # The incompatible assignment is the only finding.
    assert _codes(module) == ['TYPE_MISMATCH_ASSIGNMENT']

# ** test: binary_op_incompatible
def test_binary_op_incompatible() -> None:
    '''
    Test that an unsupported operand pair yields TYPE_MISMATCH_OPERATION.
    '''

    # str + int is not a supported shallow pair.
    module = _module([
        _binop('+', _str('a'), _int('1')),
    ])

    # The unsupported pair is the only finding.
    assert _codes(module) == ['TYPE_MISMATCH_OPERATION']

# ** test: binary_op_int_add_valid
def test_binary_op_int_add_valid() -> None:
    '''
    Test that int + int yields no findings.
    '''

    # Two integers may be added.
    module = _module([
        _binop('+', _int('1'), _int('2')),
    ])

    # A numeric addition is satisfactory.
    assert _codes(module) == []

# ** test: binary_op_str_concat_valid
def test_binary_op_str_concat_valid() -> None:
    '''
    Test that str + str yields no findings.
    '''

    # Two strings may be concatenated.
    module = _module([
        _binop('+', _str('a'), _str('b')),
    ])

    # String concatenation is satisfactory.
    assert _codes(module) == []

# ** test: binary_op_int_to_float_widening
def test_binary_op_int_to_float_widening() -> None:
    '''
    Test that assigning an int to a float yields no findings.
    '''

    # float accepts int.
    module = _module([
        _decl(_attr('count', kind=TypeKind.FLOAT)),
        _assign('count', _int('1')),
    ])

    # Widening is satisfactory.
    assert _codes(module) == []

# ** test: binary_op_str_subtraction_invalid
def test_binary_op_str_subtraction_invalid() -> None:
    '''
    Test that str - str yields TYPE_MISMATCH_OPERATION.
    '''

    # String subtraction is not a supported shallow pair.
    module = _module([
        _binop('-', _str('a'), _str('b')),
    ])

    # The unsupported subtraction is the only finding.
    assert _codes(module) == ['TYPE_MISMATCH_OPERATION']

# ** test: checker_uses_apply_provisions
def test_checker_uses_apply_provisions() -> None:
    '''
    Test that ConformanceChecker.apply calls StatementWalker.apply_provisions.
    '''

    # The method dispatches through the shared loop. It does not copy attaches_to.
    source = inspect.getsource(ConformanceChecker.apply)
    assert 'apply_provisions' in source
    assert 'attaches_to' not in source

    # A tier-1 group applies its own header before the push, then the nested header.
    seen = []

    def _record(visit, candidate, context):
        '''
        Record the visit hook and the group name passed to apply_provisions.

        :param visit: The visit hook.
        :param candidate: The ignored candidate.
        :param context: The conformance context.
        :return: No findings.
        '''

        del candidate
        seen.append((visit, context.group_name))
        return []

    checker = ConformanceChecker(
        {},
        _provision_cache(),
        'missing.',
        COMPILER_PROVISION_CACHE_PREFIX,
    )
    checker.apply_provisions = _record
    group = _group('imports', [
        _import_section('core', []),
    ])
    checker.handle_artifact(group)

    # The nested header sees the pushed group name, and the stack is popped.
    assert seen == [
        ('artifact_header', None),
        ('artifact_header', 'imports'),
    ]
    assert checker._group_stack == []

# ** test: checker_missing_module_scope_returns_empty
def test_checker_missing_module_scope_returns_empty() -> None:
    '''
    Test that check with no module scope returns an empty list.
    '''

    # The body would violate import-group rules if it were walked.
    module = _module([
        _group('imports', [
            _import_section('vendor', [_import('yaml')]),
        ]),
    ])
    checker = ConformanceChecker(
        {},
        _provision_cache(),
        'common.',
        COMPILER_PROVISION_CACHE_PREFIX,
    )

    # A missing module scope returns before the walk.
    assert checker.check(module) == []

# ** test: no_type_checker_class
def test_no_type_checker_class() -> None:
    '''
    Test that compiler.utils.typecheck does not define TypeChecker.
    '''

    # The walker is ConformanceChecker. The common list is gone.
    assert not hasattr(typecheck, 'TypeChecker')
    assert not hasattr(typecheck, 'COMMON_RULE_SET')

    # The common selector attaches exactly the eight rows, in cache order.
    checker = ConformanceChecker(
        {},
        _provision_cache(),
        'common.',
        COMPILER_PROVISION_CACHE_PREFIX,
    )
    assert [
        (spec.id, spec.applies_to, type(spec).__name__)
        for spec in checker.provisions
    ] == [
        ('common.import_group', 'artifact_header', 'ImportGroupSpecification'),
        ('common.section_class_name', 'artifact_header', 'SectionClassNameSpecification'),
        ('common.function_section_name', 'artifact_header', 'FunctionSectionNameSpecification'),
        ('common.attribute_member', 'member', 'AttributeMemberSpecification'),
        ('common.method_member', 'member', 'MethodMemberSpecification'),
        ('common.assignment_type', 'expression', 'AssignmentTypeSpecification'),
        ('common.binary_op_expression', 'expression', 'BinaryOpTypeSpecification'),
        ('common.binary_op_return', 'return', 'ReturnBinaryOpTypeSpecification'),
    ]
