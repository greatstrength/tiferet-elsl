"""Conformance Checking Domain Event Tests"""

# *** imports

# ** infra
import pytest
from tiferet.contexts.feature import FeatureContext
from tiferet.contexts.request import RequestContext

# ** app
from ..settings import DomainEvent, TiferetError
from ..typecheck import (
    CheckAssetConformance,
    CheckBlueprintsConformance,
    CheckCommonConformance,
    CheckContextsConformance,
    CheckDIConformance,
    CheckDomainConformance,
    CheckEventConformance,
    CheckInterfaceConformance,
    CheckMapperConformance,
    CheckReposConformance,
    CheckUtilsConformance,
)
from ...domain.ast import TypeKind
from ...mappers.artifact import (
    ArtifactDeclarationAggregate,
    ArtifactStatementAggregate,
)
from ...mappers.ast import (
    DeclarationAggregate,
    ExpressionAggregate,
    StatementAggregate,
    TypeAggregate,
)
from ...utils.semantic import SymbolTableBuilder
from ...utils.typecheck import (
    ASSET_RULE_SET,
    BLUEPRINTS_RULE_SET,
    COMMON_RULE_SET,
    CONTEXTS_RULE_SET,
    DI_RULE_SET,
    DOMAIN_RULE_SET,
    EVENT_RULE_SET,
    INTERFACE_RULE_SET,
    MAPPER_RULE_SET,
    REPOS_RULE_SET,
    UTILS_RULE_SET,
)
import compiler.events.typecheck as typecheck

# *** functions

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
def _section(artifact_type: str, name: str, body: list) -> ArtifactStatementAggregate:
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

# ** function: _import_from
def _import_from(module_path: str, name: str) -> StatementAggregate:
    '''
    Create an import-from statement.

    :param module_path: The imported module path.
    :type module_path: str
    :param name: The imported name.
    :type name: str
    :return: The import-from statement.
    :rtype: StatementAggregate
    '''

    # The module path and the imported name stay on separate expressions.
    return StatementAggregate.new_import_stmt_from(
        from_expr=ExpressionAggregate.new_name_expr(module_path),
        import_expr=ExpressionAggregate.new_name_expr(name),
    )

# ** function: _member
def _member(role: str, body: list) -> StatementAggregate:
    '''
    Wrap an artifact member in a declaration statement.

    :param role: The member role.
    :type role: str
    :param body: The member body statements.
    :type body: list
    :return: The declaration statement.
    :rtype: StatementAggregate
    '''

    # The role is both the member name and the artifact role.
    return _decl(ArtifactDeclarationAggregate.new_member_decl(role, member_body=body))

# ** function: _class
def _class(name: str, members: list, base: str = None) -> DeclarationAggregate:
    '''
    Create a class declaration.

    :param name: The class name.
    :type name: str
    :param members: The body statements.
    :type members: list
    :param base: The optional base class name.
    :type base: str
    :return: The class declaration.
    :rtype: DeclarationAggregate
    '''

    # A base name is stored as the class type's subtype.
    subclasses = None
    if base is not None:
        subclasses = TypeAggregate.new_class_type(name=base)

    # Members are the class body.
    return DeclarationAggregate.new_class_decl(
        name=name,
        subclasses=subclasses,
        doc_string=None,
        members=members,
    )

# ** function: _attr
def _attr(name: str) -> DeclarationAggregate:
    '''
    Create a string attribute declaration.

    :param name: The attribute name.
    :type name: str
    :return: The attribute declaration.
    :rtype: DeclarationAggregate
    '''

    # pong: str is a variable, not a nested class or function.
    return DeclarationAggregate.new_attr_decl(
        name=name,
        types=TypeAggregate.new(kind=TypeKind.STR),
    )

# ** function: _fail_ping
def _fail_ping() -> DeclarationAggregate:
    '''
    Build the nonconforming events module named fail_ping.

    :return: The module declaration.
    :rtype: DeclarationAggregate
    '''

    # The section is ping. The class is WrongName and has no execute method.
    return DeclarationAggregate.new_module_decl(
        name='fail_ping',
        code=[
            _group('imports', [
                _import_section('app', [
                    _import_from('.settings', 'DomainEvent'),
                ]),
            ]),
            _group('events', [
                _section('** event', 'ping', [
                    _decl(_class('WrongName', [
                        _member('attribute', [
                            _decl(_attr('pong')),
                        ]),
                    ], base='DomainEvent')),
                ]),
            ]),
        ],
    )

# ** function: _semantic
def _semantic(ast: DeclarationAggregate) -> dict:
    '''
    Build the semantic dict the conformance events read.

    :param ast: The module declaration to index.
    :type ast: DeclarationAggregate
    :return: The symbol table under ``symbol_table``.
    :rtype: dict
    '''

    # The event reconstructs scopes from the dumped build dict.
    return {
        'symbol_table': SymbolTableBuilder().build(ast),
    }

# ** function: _codes
def _codes(findings: list) -> list:
    '''
    Return finding codes in list order.

    :param findings: Finding dicts.
    :type findings: list
    :return: Error codes.
    :rtype: list
    '''

    # Codes are enough when the test does not cite other finding keys.
    return [item['error_code'] for item in findings]

# *** tests

# ** test: check_common_conformance_seeds_findings
def test_check_common_conformance_seeds_findings() -> None:
    '''
    Test that common conformance seeds the class-name mismatch and not the event rule.
    '''

    # Build the nonconforming events module and its dumped symbol table.
    ast = _fail_ping()
    semantic = _semantic(ast)

    # Invoke the event only through the domain event handler.
    findings = DomainEvent.handle(
        CheckCommonConformance,
        ast=ast,
        semantic=semantic,
    )
    codes = _codes(findings)

    # Common rules see the name mismatch. The event rule is a later step.
    assert 'ARTIFACT_CLASS_NAME_MISMATCH' in codes
    assert 'EVENT_MISSING_EXECUTE' not in codes

# ** test: check_common_conformance_requires_ast
def test_check_common_conformance_requires_ast() -> None:
    '''
    Test that omitting ast raises via parameters_required.
    '''

    # A present semantic value does not satisfy the missing ast parameter.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            CheckCommonConformance,
            semantic=_semantic(_fail_ping()),
        )

    # The required-parameter check names the omitted argument.
    assert exc_info.value.error_code == 'COMMAND_PARAMETER_REQUIRED'
    assert 'ast' in exc_info.value.kwargs['parameters']

# ** test: check_event_conformance_detects_missing_execute
def test_check_event_conformance_detects_missing_execute() -> None:
    '''
    Test that event conformance reports the missing execute method.
    '''

    # Build the nonconforming events module and its dumped symbol table.
    ast = _fail_ping()
    semantic = _semantic(ast)

    # Invoke the event only through the domain event handler.
    findings = DomainEvent.handle(
        CheckEventConformance,
        ast=ast,
        semantic=semantic,
    )

    # The event rule names the section and the class that lacks execute.
    assert len(findings) == 1
    assert findings[0]['error_code'] == 'EVENT_MISSING_EXECUTE'
    assert findings[0]['event_name'] == 'ping'
    assert findings[0]['class_name'] == 'WrongName'

# ** test: check_event_conformance_accumulates_prior_findings
def test_check_event_conformance_accumulates_prior_findings() -> None:
    '''
    Test that prior findings prepend and the caller's list is not mutated.
    '''

    # Build the nonconforming events module and its dumped symbol table.
    ast = _fail_ping()
    semantic = _semantic(ast)
    prior = [{
        'error_code': 'PRIOR_FINDING',
        'message': 'seeded',
        'scope_path': 'module',
    }]

    # Invoke the event only through the domain event handler.
    findings = DomainEvent.handle(
        CheckEventConformance,
        ast=ast,
        semantic=semantic,
        findings=prior,
    )

    # The new list starts with the seed. The caller's list stays length 1.
    assert _codes(findings) == ['PRIOR_FINDING', 'EVENT_MISSING_EXECUTE']
    assert len(prior) == 1

# ** test: findings_accumulate_in_declaration_order
def test_findings_accumulate_in_declaration_order() -> None:
    '''
    Test that consecutive findings steps accumulate common then event codes.
    '''

    # The request carries the module, its symbol table, and the component type.
    ast = _fail_ping()
    semantic = _semantic(ast)
    request = RequestContext(data={
        'ast': ast,
        'semantic': semantic,
        'component': 'events',
    })
    feature = FeatureContext(get_dependency=lambda *args, **kwargs: None)

    # Common conformance seeds findings. The event step appends to that key.
    feature.execute_step(
        CheckCommonConformance(),
        request,
        merged_kwargs=dict(request.data),
        data_key='findings',
    )
    feature.execute_step(
        CheckEventConformance(),
        request,
        merged_kwargs=dict(request.data),
        data_key='findings',
    )

    # Declaration order is common, then the events dialect.
    assert _codes(request.data['findings']) == [
        'ARTIFACT_CLASS_NAME_MISMATCH',
        'EVENT_MISSING_EXECUTE',
    ]

# ** test: check_star_conformance_binds_named_rule_set
@pytest.mark.parametrize('event_cls,rule_set_constant', [
    (CheckCommonConformance, COMMON_RULE_SET),
    (CheckEventConformance, EVENT_RULE_SET),
    (CheckAssetConformance, ASSET_RULE_SET),
    (CheckDomainConformance, DOMAIN_RULE_SET),
    (CheckMapperConformance, MAPPER_RULE_SET),
    (CheckInterfaceConformance, INTERFACE_RULE_SET),
    (CheckDIConformance, DI_RULE_SET),
    (CheckUtilsConformance, UTILS_RULE_SET),
    (CheckContextsConformance, CONTEXTS_RULE_SET),
    (CheckBlueprintsConformance, BLUEPRINTS_RULE_SET),
    (CheckReposConformance, REPOS_RULE_SET),
])
def test_check_star_conformance_binds_named_rule_set(
        event_cls,
        rule_set_constant,
    ) -> None:
    '''
    Test that each conformance event binds its named rule-set constant.

    :param event_cls: The conformance event class.
    :type event_cls: type
    :param rule_set_constant: The rule-set constant that class must bind.
    :type rule_set_constant: list
    '''

    # Identity, not equality: the event must not copy the constant.
    assert event_cls.rule_set is rule_set_constant

# ** test: dialect_event_execute_does_not_read_component
def test_dialect_event_execute_does_not_read_component() -> None:
    '''
    Test that a mismatched component still reports the events finding.
    '''

    # Build the nonconforming events module and its dumped symbol table.
    ast = _fail_ping()
    semantic = _semantic(ast)

    # Invoke the event only through the domain event handler.
    findings = DomainEvent.handle(
        CheckEventConformance,
        ast=ast,
        semantic=semantic,
        component='domain',
    )

    # Gating is not inside execute, so the events rule still fires.
    assert 'EVENT_MISSING_EXECUTE' in _codes(findings)

# ** test: no_perform_type_check_event
def test_no_perform_type_check_event() -> None:
    '''
    Test that this module defines neither PerformTypeCheck nor TypeChecker.
    '''

    # Those names belong to an earlier shape. This module does not define them.
    assert not hasattr(typecheck, 'PerformTypeCheck')
    assert not hasattr(typecheck, 'TypeChecker')
