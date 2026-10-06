"""Compiler Common Conformance Checker Tests"""

# *** imports

# ** core
import inspect
from pathlib import Path

# ** app
from ...assets.error import COMPILER_DEFAULT_ERRORS
from ...assets.provision import COMPILER_DEFAULT_PROVISIONS
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
def _group(name: str, body: list,
           qualifier: str = None) -> ArtifactStatementAggregate:
    '''
    Create a tier-1 artifact group.

    :param name: The group name.
    :type name: str
    :param body: The group body.
    :type body: list
    :param qualifier: The optional parenthetical qualifier.
    :type qualifier: str
    :return: The artifact statement.
    :rtype: ArtifactStatementAggregate
    '''

    # A tier-1 header uses the triple-star marker.
    header = ArtifactDeclarationAggregate.new_artifact_decl(
        name=name,
        artifact_type='***',
        qualifier=qualifier,
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
          return_kind: TypeKind = None,
          body: list = None) -> DeclarationAggregate:
    '''
    Create a function declaration.

    :param name: The function name.
    :type name: str
    :param params: The parameters, or None.
    :type params: list
    :param return_kind: The optional return-type kind.
    :type return_kind: TypeKind
    :param body: The optional function body.
    :type body: list
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
        body=body or [],
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

# ** function: _class
def _class(name: str, members: list) -> DeclarationAggregate:
    '''
    Create a class declaration.

    :param name: The class name.
    :type name: str
    :param members: The class body statements.
    :type members: list
    :return: The class declaration.
    :rtype: DeclarationAggregate
    '''

    # Members are the class body the order specification reads.
    return DeclarationAggregate.new_class_decl(
        name=name,
        subclasses=None,
        doc_string=None,
        members=members,
    )

# ** function: _self
def _self() -> ParamListAggregate:
    '''
    Create a self parameter.

    :return: The self parameter.
    :rtype: ParamListAggregate
    '''

    # A property and an ordinary method both take self.
    return ParamListAggregate.new('self')

# ** function: _property
def _property(name: str = 'label',
              body: list = None) -> StatementAggregate:
    '''
    Create a legal property method.

    :param name: The property name.
    :type name: str
    :param body: The optional function body.
    :type body: list
    :return: The member statement.
    :rtype: StatementAggregate
    '''

    # The legal form is a bare property decorator and the property qualifier.
    return _member('method', [
        _decorator('property'),
        _decl(_func(name, params=[_self()], body=body)),
    ], qualifier='property')

# ** function: _hosted
def _hosted(group: str, members: list,
            class_name: str = 'Sample') -> DeclarationAggregate:
    '''
    Host a class in one tier-1 group.

    :param group: The tier-1 group name.
    :type group: str
    :param members: The class body statements.
    :type members: list
    :param class_name: The class name.
    :type class_name: str
    :return: The module declaration.
    :rtype: DeclarationAggregate
    '''

    # The group name is what a missing component uses for the property rule.
    return _module([
        _group(group, [
            _decl(_class(class_name, members)),
        ]),
    ])

# ** function: _findings
def _findings(module: DeclarationAggregate) -> list:
    '''
    Build a symbol table, then check the module through the public entry.

    :param module: The module declaration.
    :type module: DeclarationAggregate
    :return: Finding dicts, in walk order.
    :rtype: list
    '''

    # Typing lookup reads the live registry, not the dumped build dict.
    cache = _provision_cache()
    builder = SymbolTableBuilder(cache, COMPILER_PROVISION_CACHE_PREFIX)
    builder.build(module)
    return ConformanceChecker(
        builder.scopes,
        cache,
        'common.',
        COMPILER_PROVISION_CACHE_PREFIX,
    ).check(module)

# ** function: _codes
def _codes(module: DeclarationAggregate) -> list:
    '''
    Return finding codes for a module checked through the public entry.

    :param module: The module declaration.
    :type module: DeclarationAggregate
    :return: Finding codes, in walk order.
    :rtype: list
    '''

    # Codes are enough when the test does not cite a message.
    return [item['error_code'] for item in _findings(module)]

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

    # The common selector attaches the three order rows, then the published eight.
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
        ('common.section_order', 'module', 'SectionOrderSpecification'),
        ('common.member_order', 'class', 'MemberOrderSpecification'),
        ('common.property_member', 'member', 'PropertyMemberSpecification'),
        ('common.import_group', 'artifact_header', 'ImportGroupSpecification'),
        ('common.section_class_name', 'artifact_header', 'SectionClassNameSpecification'),
        ('common.function_section_name', 'artifact_header', 'FunctionSectionNameSpecification'),
        ('common.attribute_member', 'member', 'AttributeMemberSpecification'),
        ('common.method_member', 'member', 'MethodMemberSpecification'),
        ('common.assignment_type', 'expression', 'AssignmentTypeSpecification'),
        ('common.binary_op_expression', 'expression', 'BinaryOpTypeSpecification'),
        ('common.binary_op_return', 'return', 'ReturnBinaryOpTypeSpecification'),
    ]

# ** test: provisions_prepend_artifact_order_rows
def test_provisions_prepend_artifact_order_rows() -> None:
    '''
    Test that the catalog begins with the three order rows and empty parameters.
    '''

    # The published 49 keys stay after the three new rows.
    keys = list(COMPILER_DEFAULT_PROVISIONS)
    assert keys[:4] == [
        'common.section_order',
        'common.member_order',
        'common.property_member',
        'common.import_group',
    ]
    assert len(keys) == 52
    for key in keys[:3]:
        value = COMPILER_DEFAULT_PROVISIONS[key]
        assert value['parameters'] == {}
        assert value['kind'] == 'specification'
        assert value['module_path'] == 'compiler.utils.core'

# ** test: artifact_order_errors_join_the_catalog
def test_artifact_order_errors_join_the_catalog() -> None:
    '''
    Test that the four order codes are catalog keys and errors.yml stays absent.
    '''

    # The codes join the default error dict. They do not restore the YAML file.
    for key in (
        'ARTIFACT_SECTION_ORDER',
        'ARTIFACT_MEMBER_ORDER',
        'INVALID_PROPERTY_MEMBER',
        'PROPERTY_NOT_DESCRIPTIVE',
    ):
        assert key in COMPILER_DEFAULT_ERRORS
    assets = Path(__file__).resolve().parents[2] / 'assets'
    assert not (assets / 'errors.yml').exists()

# ** test: in_order_module_has_no_artifact_order_finding
def test_in_order_module_has_no_artifact_order_finding() -> None:
    '''
    Test that an in-order module yields no finding from these specifications.
    '''

    # Preamble, then construct groups, with members in band order.
    module = _module([
        _group('imports', [
            _import_section('core', [_import('typing')]),
        ]),
        _group('constants', []),
        _group('functions', []),
        _group('classes', []),
        _group('models', [
            _decl(_class('Sample', [
                _member('attribute', [_decl(_attr('count', kind=TypeKind.INT))]),
                _member('init', [_decl(_func('__init__', params=[_self()]))]),
                _property(),
                _member('method', [_decl(_func('run', params=[_self()]))]),
            ])),
        ]),
        _group('events', []),
    ])

    # Section order, member order, and the property form are satisfactory.
    assert _codes(module) == []

# ** test: construct_group_before_constants_is_out_of_order
def test_construct_group_before_constants_is_out_of_order() -> None:
    '''
    Test that a construct group before constants yields ARTIFACT_SECTION_ORDER.
    '''

    # models is a construct group. constants is a preamble section.
    module = _module([
        _group('models', []),
        _group('constants', []),
    ])

    # The later preamble section is the finding.
    assert _codes(module) == ['ARTIFACT_SECTION_ORDER']

# ** test: qualified_section_before_plain_section_is_out_of_order
def test_qualified_section_before_plain_section_is_out_of_order() -> None:
    '''
    Test that a sub-group before its plain section yields ARTIFACT_SECTION_ORDER.
    '''

    # The qualified constants section appears before the plain constants section.
    module = _module([
        _group('constants', [], qualifier='error'),
        _group('constants', []),
    ])
    findings = _findings(module)

    # The message says the plain section must precede its sub-group.
    assert [item['error_code'] for item in findings] == ['ARTIFACT_SECTION_ORDER']
    assert 'the plain section must precede its sub-group' in findings[0]['message']

# ** test: missing_functions_section_is_not_a_finding
def test_missing_functions_section_is_not_a_finding() -> None:
    '''
    Test that a missing functions section yields no section-order finding.
    '''

    # functions is absent. The sections that are present stay in order.
    module = _module([
        _group('imports', [
            _import_section('core', [_import('typing')]),
        ]),
        _group('constants', []),
        _group('classes', []),
    ])

    # A missing band is not a finding.
    assert 'ARTIFACT_SECTION_ORDER' not in _codes(module)
    assert _codes(module) == []

# ** test: construct_groups_have_no_relative_order
def test_construct_groups_have_no_relative_order() -> None:
    '''
    Test that models and events may appear in either order.
    '''

    # Both names are construct groups, so neither rank is lower.
    forward = _module([
        _group('models', []),
        _group('events', []),
    ])
    reverse = _module([
        _group('events', []),
        _group('models', []),
    ])

    # Equal rank is not a finding.
    assert _codes(forward) == []
    assert _codes(reverse) == []

# ** test: tests_before_fixtures_is_out_of_order
def test_tests_before_fixtures_is_out_of_order() -> None:
    '''
    Test that tests before fixtures yields ARTIFACT_SECTION_ORDER.
    '''

    # fixtures ranks before tests.
    module = _module([
        _group('tests', []),
        _group('fixtures', []),
    ])

    # The later fixtures section is the finding.
    assert _codes(module) == ['ARTIFACT_SECTION_ORDER']

# ** test: production_member_bands_in_order_have_no_order_finding
def test_production_member_bands_in_order_have_no_order_finding() -> None:
    '''
    Test that attribute, init, property, then method yields no order finding.
    '''

    # Each band is strictly higher than the one before it.
    module = _hosted('models', [
        _member('attribute', [_decl(_attr('count', kind=TypeKind.INT))]),
        _member('init', [_decl(_func('__init__', params=[_self()]))]),
        _property(),
        _member('method', [_decl(_func('run', params=[_self()]))]),
    ])

    # The property form is legal, so the module has no findings.
    assert 'ARTIFACT_MEMBER_ORDER' not in _codes(module)
    assert _codes(module) == []

# ** test: method_before_property_is_out_of_order
def test_method_before_property_is_out_of_order() -> None:
    '''
    Test that a standard method before a property yields ARTIFACT_MEMBER_ORDER.
    '''

    # A property is read before every other method.
    module = _hosted('models', [
        _member('method', [_decl(_func('run', params=[_self()]))]),
        _property(),
    ])

    # The later property is the finding.
    assert _codes(module) == ['ARTIFACT_MEMBER_ORDER']

# ** test: property_before_init_is_out_of_order
def test_property_before_init_is_out_of_order() -> None:
    '''
    Test that a property before init yields ARTIFACT_MEMBER_ORDER.
    '''

    # init ranks before the property band.
    module = _hosted('models', [
        _property(),
        _member('init', [_decl(_func('__init__', params=[_self()]))]),
    ])

    # The later init is the finding.
    assert _codes(module) == ['ARTIFACT_MEMBER_ORDER']

# ** test: method_before_attribute_is_out_of_order
def test_method_before_attribute_is_out_of_order() -> None:
    '''
    Test that a method before an attribute yields ARTIFACT_MEMBER_ORDER.
    '''

    # An attribute ranks before every method.
    module = _hosted('models', [
        _member('method', [_decl(_func('run', params=[_self()]))]),
        _member('attribute', [_decl(_attr('count', kind=TypeKind.INT))]),
    ])

    # The later attribute is the finding.
    assert _codes(module) == ['ARTIFACT_MEMBER_ORDER']

# ** test: static_method_after_property_has_no_order_finding
def test_static_method_after_property_has_no_order_finding() -> None:
    '''
    Test that a static method after a property yields no order finding.
    '''

    # A static qualifier does not leave the ordinary method band.
    module = _hosted('models', [
        _property(),
        _member('method', [
            _decorator('staticmethod'),
            _decl(_func('build')),
        ], qualifier='static'),
    ])

    # The static method ranks after the property.
    assert 'ARTIFACT_MEMBER_ORDER' not in _codes(module)
    assert _codes(module) == []

# ** test: attribute_after_init_is_out_of_order
def test_attribute_after_init_is_out_of_order() -> None:
    '''
    Test that an attribute after init yields ARTIFACT_MEMBER_ORDER.
    '''

    # An attribute ranks before init.
    module = _hosted('models', [
        _member('init', [_decl(_func('__init__', params=[_self()]))]),
        _member('attribute', [_decl(_attr('count', kind=TypeKind.INT))]),
    ])

    # The later attribute is the finding.
    assert _codes(module) == ['ARTIFACT_MEMBER_ORDER']

# ** test: property_decorator_on_attribute_is_invalid
def test_property_decorator_on_attribute_is_invalid() -> None:
    '''
    Test that @property on an attribute member yields INVALID_PROPERTY_MEMBER.
    '''

    # The property band is the qualifier, not a decorator on an attribute.
    module = _hosted('models', [
        _member('attribute', [
            _decorator('property'),
            _decl(_func('count', params=[_self()])),
        ]),
    ])

    # The wrong label is the finding.
    assert _codes(module) == ['INVALID_PROPERTY_MEMBER']

# ** test: setter_decorator_is_an_ordinary_method
def test_setter_decorator_is_an_ordinary_method() -> None:
    '''
    Test that a setter decorator yields INVALID_PROPERTY_MEMBER.
    '''

    # There is no setter qualifier. The decorator is the miss.
    module = _hosted('models', [
        _member('method', [
            _decorator('count.setter'),
            _decl(_func('count', params=[_self()])),
        ]),
    ])
    findings = _findings(module)

    # The message says a write is an ordinary method.
    assert [item['error_code'] for item in findings] == ['INVALID_PROPERTY_MEMBER']
    assert 'a write is an ordinary method' in findings[0]['message']

# ** test: property_on_events_class_is_invalid
def test_property_on_events_class_is_invalid() -> None:
    '''
    Test that a property on an events class yields INVALID_PROPERTY_MEMBER.
    '''

    # events is not models, mappers, or contexts.
    module = _hosted('events', [
        _property('name'),
    ], class_name='Ping')

    # The illegal group is the finding. The form itself is legal.
    assert _codes(module) == ['INVALID_PROPERTY_MEMBER']

# ** test: property_on_domain_mapper_or_context_is_not_a_finding
def test_property_on_domain_mapper_or_context_is_not_a_finding() -> None:
    '''
    Test that a bare property on a domain, mapper, or context class yields no property finding.
    '''

    # Those components are the groups models, mappers, and contexts when component is absent.
    for group in ('models', 'mappers', 'contexts'):
        module = _hosted(group, [
            _property(),
        ])
        assert _codes(module) == [], group

# ** test: property_that_assigns_through_self_is_not_descriptive
def test_property_that_assigns_through_self_is_not_descriptive() -> None:
    '''
    Test that a property body assigning through self yields PROPERTY_NOT_DESCRIPTIVE.
    '''

    # The assignment target is a self attribute. The form is otherwise legal.
    module = _hosted('models', [
        _member('attribute', [_decl(_attr('count', kind=TypeKind.INT))]),
        _property('count', body=[
            _assign('self.count', _int('1')),
        ]),
    ])

    # The mutating body is the finding.
    assert _codes(module) == ['PROPERTY_NOT_DESCRIPTIVE']

# ** test: tester_fixture_then_test_has_no_finding
def test_tester_fixture_then_test_has_no_finding() -> None:
    '''
    Test that fixture then test yields no finding.
    '''

    # The tester table ranks fixture before test.
    module = _module([
        _decl(_class('Sample', [
            _member('fixture', []),
            _member('test', []),
        ])),
    ])

    # That order is satisfactory.
    assert _codes(module) == []

# ** test: tester_test_before_fixture_is_out_of_order
def test_tester_test_before_fixture_is_out_of_order() -> None:
    '''
    Test that test before fixture yields ARTIFACT_MEMBER_ORDER.
    '''

    # fixture ranks before test.
    module = _module([
        _decl(_class('Sample', [
            _member('test', []),
            _member('fixture', []),
        ])),
    ])

    # The later fixture is the finding.
    assert _codes(module) == ['ARTIFACT_MEMBER_ORDER']

# ** test: mixed_attribute_and_fixture_does_not_order
def test_mixed_attribute_and_fixture_does_not_order() -> None:
    '''
    Test that a class mixing attribute and fixture yields no order finding.
    '''

    # The leftover harness is not this rule.
    module = _module([
        _decl(_class('Sample', [
            _member('attribute', [_decl(_attr('count', kind=TypeKind.INT))]),
            _member('fixture', []),
        ])),
    ])

    # The order specification does not fire.
    assert 'ARTIFACT_MEMBER_ORDER' not in _codes(module)
    assert _codes(module) == []

# ** test: import_group_order_is_not_these_specifications
def test_import_group_order_is_not_these_specifications() -> None:
    '''
    Test that core after app inside imports yields no finding from these specifications.
    '''

    # Import-group order is listed in the style and is not a section rank.
    module = _module([
        _group('imports', [
            _import_section('app', [_import('compiler')]),
            _import_section('core', [_import('typing')]),
        ]),
    ])

    # Neither the section rule nor the member rules judge that order.
    assert _codes(module) == []
