"""Compiler Event Dialect Tests"""

# *** imports

# ** app
from ...mappers.artifact import (
    ArtifactDeclarationAggregate,
    ArtifactStatementAggregate,
)
from ...mappers.ast import (
    DeclarationAggregate,
    StatementAggregate,
    TypeAggregate,
)
from ..semantic import SymbolTableBuilder
from ..typecheck import EVENT_RULE_SET, ConformanceChecker

# *** functions

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
    return DeclarationAggregate.new_module_decl(name='events', code=code)

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

# ** function: _func
def _func(name: str) -> DeclarationAggregate:
    '''
    Create a function declaration.

    :param name: The function name.
    :type name: str
    :return: The function declaration.
    :rtype: DeclarationAggregate
    '''

    # The function type is what marks the declaration as a function.
    return DeclarationAggregate.new_func_decl(
        name=name,
        type=TypeAggregate.new_func_type(params=[]),
        body=[],
    )

# ** function: check_event
def check_event(module: DeclarationAggregate) -> list:
    '''
    Check a module with the event rule set.

    :param module: The module declaration.
    :type module: DeclarationAggregate
    :return: Finding dicts.
    :rtype: list
    '''

    # The checker reads the live registry, not the dumped build dict.
    builder = SymbolTableBuilder()
    builder.build(module)
    return ConformanceChecker(
        scopes=builder.scopes,
        rule_set=EVENT_RULE_SET,
    ).check(module)

# *** tests

# ** test: event_section_satisfied_when_execute_present
def test_event_section_satisfied_when_execute_present() -> None:
    '''
    Test that an event class with execute yields no findings.
    '''

    # ping declares the required execute method.
    module = _module([
        _section('** event', 'ping', [
            _decl(_class('Ping', [
                _member('method', [_decl(_func('execute'))]),
            ], base='DomainEvent')),
        ]),
    ])

    # A present execute method is satisfactory.
    assert check_event(module) == []

# ** test: event_section_violated_when_execute_missing
def test_event_section_violated_when_execute_missing() -> None:
    '''
    Test that an event class without execute yields EVENT_MISSING_EXECUTE.
    '''

    # The class has no execute method.
    module = _module([
        _section('** event', 'ping', [
            _decl(_class('Ping', [], base='DomainEvent')),
        ]),
    ])
    findings = check_event(module)

    # The missing method is named on the finding.
    assert len(findings) == 1
    assert findings[0]['error_code'] == 'EVENT_MISSING_EXECUTE'
    assert findings[0]['event_name'] == 'ping'
    assert findings[0]['class_name'] == 'Ping'

# ** test: event_section_ignored_for_non_event_keyword
def test_event_section_ignored_for_non_event_keyword() -> None:
    '''
    Test that a non-event section with no execute yields no event findings.
    '''

    # A model section is not an event section.
    module = _module([
        _section('** model', 'ping', [
            _decl(_class('Ping', [])),
        ]),
    ])

    # The event rule does not judge other keywords.
    assert check_event(module) == []

# ** test: event_rule_set_is_exactly_event_section
def test_event_rule_set_is_exactly_event_section() -> None:
    '''
    Test that the event rule set is the single event section specification.
    '''

    # The actor event dialect is one rule, not a checker subclass.
    assert len(EVENT_RULE_SET) == 1
    assert EVENT_RULE_SET[0].id == 'event.section'
