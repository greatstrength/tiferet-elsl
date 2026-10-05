"""Compiler Context Dialect Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest

# ** app
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
from .parser_test_helpers import (
    load_grammar_rules,
    load_production_rules,
    load_token_rules,
)
from ..lexer import TiferetLexer
from ..parser import TiferetParser
from ..semantic import SymbolTableBuilder
from ..typecheck import CONTEXTS_RULE_SET, ConformanceChecker

# *** constants

# ** constant: fixtures_dir
_FIXTURES_DIR = Path(__file__).resolve().parent / 'fixtures' / 'contexts'

# *** classes

# ** class: _parser_harness
class _ParserHarness:
    '''
    Load the declared catalogues and parse a fixture file.
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

    # * method: parse_file
    def parse_file(self, path: Path):
        '''
        Tokenize a fixture and parse it to a module AST.

        :param path: The fixture path.
        :type path: Path
        :return: The root module AST.
        :rtype: Any
        '''

        # Layout injection stays in the lexer. The parser receives tokens only.
        source = path.read_text(encoding='utf-8')
        tokens = TiferetLexer().tokenize(source, self.tokens, self.grammars)
        return self._parser.parse(
            path.stem,
            tokens,
            self.grammars,
            self.tokens,
            self.productions,
            source_text=source,
        )

# *** functions

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
    return DeclarationAggregate.new_module_decl(name='contexts', code=code)

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
def _attr(name: str, value: ExpressionAggregate = None) -> DeclarationAggregate:
    '''
    Create an attribute declaration.

    :param name: The attribute name.
    :type name: str
    :param value: The optional initializer.
    :type value: ExpressionAggregate
    :return: The attribute declaration.
    :rtype: DeclarationAggregate
    '''

    # A missing value leaves the initializer unset.
    return DeclarationAggregate.new_attr_decl(name=name, value=value)

# ** function: _context
def _context(class_name: str, members: list, base: str = None) -> DeclarationAggregate:
    '''
    Create a contexts group containing one context section.

    :param class_name: The class name.
    :type class_name: str
    :param members: The class members.
    :type members: list
    :param base: The base class name, or None for no base.
    :type base: str
    :return: The module declaration.
    :rtype: DeclarationAggregate
    '''

    # The section keyword is what the base-class rule matches.
    return _module([
        _group('contexts', [
            _section('** context', 'feature', [
                _decl(_class(class_name, members, base=base)),
            ]),
        ]),
    ])

# ** function: check_contexts
def check_contexts(module) -> list:
    '''
    Check a module with the contexts rule set.

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
        rule_set=CONTEXTS_RULE_SET,
    ).check(module)

# ** function: _codes
def _codes(module) -> list:
    '''
    Return finding codes for a module.

    :param module: The module declaration.
    :type module: DeclarationAggregate
    :return: Finding codes, in walk order.
    :rtype: list
    '''

    # Codes are enough when the test does not cite a finding key.
    return [item['error_code'] for item in check_contexts(module)]

# *** tests

# ** test: conformant_modules_report_no_findings
@pytest.mark.parametrize('filename', [
    'app.py',
    'cache.py',
    'cli.py',
    'core.py',
    'error.py',
    'feature.py',
    'logging.py',
    'request.py',
])
def test_conformant_modules_report_no_findings(filename: str) -> None:
    '''
    Test that each contexts fixture yields no findings.

    :param filename: The fixture file name.
    :type filename: str
    '''

    # Parse the fixture, then check it with the contexts rule set.
    module = _parser().parse_file(_FIXTURES_DIR / filename)

    # A conformant module has nothing to report.
    assert check_contexts(module) == []

# ** test: disallowed_group_reported
def test_disallowed_group_reported() -> None:
    '''
    Test that a group outside the permitted set yields DISALLOWED_CONTEXTS_GROUP.
    '''

    # repos is not a permitted contexts group.
    module = _module([
        _group('repos', []),
    ])

    # The disallowed group is the only finding.
    assert _codes(module) == ['DISALLOWED_CONTEXTS_GROUP']

# ** test: invalid_app_import_reported
@pytest.mark.parametrize('module_path', [
    '..repos.feature',
    '..utils.file',
    '..mappers.feature',
])
def test_invalid_app_import_reported(module_path: str) -> None:
    '''
    Test that a disallowed app import yields INVALID_CONTEXTS_APP_IMPORT.

    :param module_path: A repos, utils, or other disallowed path.
    :type module_path: str
    '''

    # Those component types are omitted from the contexts allowance.
    module = _module([
        _group('imports', [
            _import_section('app', [
                _import_from(module_path, 'Feature'),
            ]),
        ]),
    ])

    # The disallowed path is the only finding.
    assert _codes(module) == ['INVALID_CONTEXTS_APP_IMPORT']

# ** test: assets_domain_events_and_sibling_app_imports_allowed
@pytest.mark.parametrize('module_path,name', [
    ('.core', 'BaseContext'),
    ('..assets.error', 'ERROR_NOT_FOUND_ID'),
    ('..domain.feature', 'Feature'),
    ('..events.feature', 'CompileFeature'),
    ('..', 'a'),
])
def test_assets_domain_events_and_sibling_app_imports_allowed(
        module_path: str, name: str) -> None:
    '''
    Test that sibling, assets, domain, events, and the root alias yield no finding.

    :param module_path: An allowed sibling, component, or parent path.
    :type module_path: str
    :param name: The imported name.
    :type name: str
    '''

    # Each path is a sibling, a permitted component, or from .. import a.
    module = _module([
        _group('imports', [
            _import_section('app', [
                _import_from(module_path, name),
            ]),
        ]),
    ])

    # The allowed path is satisfactory.
    assert _codes(module) == []

# ** test: domain_bound_context_missing_base_context_reported
def test_domain_bound_context_missing_base_context_reported() -> None:
    '''
    Test that a bound domain_type without BaseContext yields CONTEXT_MISSING_BASE_CONTEXT.
    '''

    # The initializer is a name, so the binding is real, and no base is declared.
    module = _context('FeatureContext', [
        _member('attribute', [
            _decl(_attr(
                'domain_type',
                value=ExpressionAggregate.new_name_expr('Feature'),
            )),
        ]),
    ])

    # The missing base is the only finding.
    assert _codes(module) == ['CONTEXT_MISSING_BASE_CONTEXT']

# ** test: domain_bound_context_extending_base_context_reports_no_findings
def test_domain_bound_context_extending_base_context_reports_no_findings() -> None:
    '''
    Test that a bound domain_type extending BaseContext yields no base-class finding.
    '''

    # BaseContext is the required base for a bound domain type.
    module = _context('FeatureContext', [
        _member('attribute', [
            _decl(_attr(
                'domain_type',
                value=ExpressionAggregate.new_name_expr('Feature'),
            )),
        ]),
    ], base='BaseContext')

    # A present required base is satisfactory.
    assert 'CONTEXT_MISSING_BASE_CONTEXT' not in _codes(module)
    assert check_contexts(module) == []

# ** test: non_domain_bound_context_exempt_from_base_class_rule
def test_non_domain_bound_context_exempt_from_base_class_rule() -> None:
    '''
    Test that a context with no domain_type member yields no base-class finding.
    '''

    # No domain_type member means the base-class rule does not apply.
    module = _context('CacheContext', [
        _member('attribute', [
            _decl(_attr('cache')),
        ]),
    ], base='object')

    # The exemption is satisfactory.
    assert 'CONTEXT_MISSING_BASE_CONTEXT' not in _codes(module)

# ** test: subclass_without_own_domain_type_exempt_from_base_class_rule
def test_subclass_without_own_domain_type_exempt_from_base_class_rule() -> None:
    '''
    Test that a domain_type initialized to None yields no base-class finding.
    '''

    # A bare None is a type-hint placeholder, not a binding.
    module = _context('CliRequestContext', [
        _member('attribute', [
            _decl(_attr(
                'domain_type',
                value=ExpressionAggregate.new_none_expr(),
            )),
        ]),
    ], base='RequestContext')

    # The placeholder does not require BaseContext.
    assert 'CONTEXT_MISSING_BASE_CONTEXT' not in _codes(module)
