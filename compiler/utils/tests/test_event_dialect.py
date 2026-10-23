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
from .parser_test_helpers import (
    load_grammar_rules,
    load_production_rules,
    load_token_rules,
)
from ..lexer import TiferetLexer
from ..parser import TiferetParser
from ..semantic import SymbolTableBuilder
from ...blueprints.core import build_cache
from ...contexts.provision import COMPILER_PROVISION_CACHE_PREFIX
from ..typecheck import ConformanceChecker

# *** constants

# ** constant: event_group_probe
_EVENT_GROUP_PROBE = '''"""Events group probe"""

# *** imports

# ** app
from .core import DomainEvent

# *** models

# ** event: probe_event
class ProbeEvent(DomainEvent):
    \'\'\'
    A probe event.
    \'\'\'

    # * method: execute
    def execute(self, id: str, **kwargs) -> str:
        \'\'\'
        Return the id.

        :param id: The id.
        :type id: str
        :return: The id.
        :rtype: str
        \'\'\'

        # Return the id.
        return id
'''

# ** constant: helper_function_section
_HELPER_FUNCTION_SECTION = '''# ** function: helper
def helper() -> str:
    \'\'\'
    Return a value.

    :return: The value.
    :rtype: str
    \'\'\'

    # Return the value.
    return 'value'

'''

# *** classes

# ** class: _parser_harness
class _ParserHarness:
    '''
    Load the declared catalogues and parse source text.
    '''

    # * init
    def __init__(self) -> None:
        '''
        Load the declared token, grammar, and production catalogues.
        '''

        # Catalogues stay on the harness. The adapter does not read them itself.
        self.tokens = load_token_rules()
        self.grammars = load_grammar_rules()
        self.productions = load_production_rules()
        self._parser = TiferetParser()

    # * method: parse_source
    def parse_source(self, source: str):
        '''
        Tokenize source text and parse it to a module AST.

        :param source: The module source text.
        :type source: str
        :return: The root module AST.
        :rtype: Any
        '''

        # Layout injection stays in the lexer. The parser receives tokens only.
        tokens = TiferetLexer().tokenize(source, self.tokens, self.grammars)
        return self._parser.parse(
            'probe',
            tokens,
            self.grammars,
            self.tokens,
            self.productions,
            source_text=source,
        )

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
    cache = _provision_cache()
    builder = SymbolTableBuilder(cache, COMPILER_PROVISION_CACHE_PREFIX)
    builder.build(module)
    return ConformanceChecker(
        builder.scopes,
        cache,
        'event.',
        COMPILER_PROVISION_CACHE_PREFIX,
    ).check(module)

# ** function: _parser
def _parser() -> _ParserHarness:
    '''
    Return one harness for the module.

    :return: The parser harness.
    :rtype: _ParserHarness
    '''

    # Catalogues are loaded once. Each parse still gets a fresh token stream.
    if not hasattr(_parser, 'harness'):
        _parser.harness = _ParserHarness()
    return _parser.harness

# ** function: check_event_source
def check_event_source(source: str) -> list:
    '''
    Parse source text and check it with the common and event rule sets.

    :param source: The module source text.
    :type source: str
    :return: Finding dicts, common first, then event.
    :rtype: list
    '''

    # The semantic pipeline runs the common selector before the event one.
    module = _parser().parse_source(source)
    cache = _provision_cache()
    builder = SymbolTableBuilder(cache, COMPILER_PROVISION_CACHE_PREFIX)
    builder.build(module)
    findings = []
    for selector in ('common.', 'event.'):
        findings.extend(ConformanceChecker(
            builder.scopes,
            cache,
            selector,
            COMPILER_PROVISION_CACHE_PREFIX,
        ).check(module))
    return findings

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

# ** test: event_rule_set_rows
def test_event_rule_set_rows() -> None:
    '''
    Test that the event rule set is the event section, permitted group, and agreement rows.
    '''

    # The event selector attaches three specifications. It is not a checker subclass.
    checker = ConformanceChecker(
        {},
        _provision_cache(),
        'event.',
        COMPILER_PROVISION_CACHE_PREFIX,
    )
    assert [provision.id for provision in checker.provisions] == [
        'event.section',
        'event.permitted_group',
        'event.group_section_agreement',
    ]

# ** test: event_permitted_group_violated_for_widgets
def test_event_permitted_group_violated_for_widgets() -> None:
    '''
    Test that a widgets group yields one DISALLOWED_EVENT_GROUP at the group line.
    '''

    # widgets is not a permitted events group.
    source = _EVENT_GROUP_PROBE.replace('# *** models', '# *** widgets')
    findings = check_event_source(source)

    # The disallowed group is the only finding, with the shared message template.
    assert [(item['error_code'], item['lineno']) for item in findings] == [
        ('DISALLOWED_EVENT_GROUP', 8),
    ]
    assert findings[0]['message'] == (
        "Group 'widgets' is not permitted in an events module. "
        'Permitted groups are: classes, constants, events, exports, functions, imports.'
    )

# ** test: event_permitted_group_violated_for_models
def test_event_permitted_group_violated_for_models() -> None:
    '''
    Test that a models group yields DISALLOWED_EVENT_GROUP at the group line.
    '''

    # models is not permitted. It also expects model sections, so agreement may fire too.
    findings = check_event_source(_EVENT_GROUP_PROBE)

    # The disallowed group is reported at the group line.
    assert ('DISALLOWED_EVENT_GROUP', 8) in [
        (item['error_code'], item['lineno']) for item in findings
    ]

# ** test: event_group_section_agreement_violated_for_function_section
def test_event_group_section_agreement_violated_for_function_section() -> None:
    '''
    Test that a function section under the events group yields SECTION_GROUP_MISMATCH.
    '''

    # A helper function section sits under events next to the event section.
    source = _EVENT_GROUP_PROBE.replace('# *** models', '# *** events').replace(
        '# ** event: probe_event',
        _HELPER_FUNCTION_SECTION + '# ** event: probe_event',
    )
    findings = check_event_source(source)

    # The function section is the only mismatch.
    assert [item['error_code'] for item in findings] == ['SECTION_GROUP_MISMATCH']
    assert findings[0]['expected_keyword'] == 'event'
    assert findings[0]['actual_keyword'] == 'function'

# ** test: event_groups_satisfied_for_events_group
def test_event_groups_satisfied_for_events_group() -> None:
    '''
    Test that the probe under the events group yields no findings.
    '''

    # events is permitted, and its section is an event section.
    source = _EVENT_GROUP_PROBE.replace('# *** models', '# *** events')

    # No rule fires.
    assert check_event_source(source) == []
