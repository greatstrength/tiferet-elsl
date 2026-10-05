"""Compiler Repos Dialect Tests"""

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
from ...blueprints.core import build_cache
from ...contexts.provision import COMPILER_PROVISION_CACHE_PREFIX
from ..typecheck import ConformanceChecker

# *** constants

# ** constant: fixtures_dir
_FIXTURES_DIR = Path(__file__).resolve().parent / 'fixtures' / 'repos'

# ** constant: crud_methods
_CRUD_METHODS = (
    'exists',
    'get',
    'list',
    'save',
    'delete',
)

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
    return DeclarationAggregate.new_module_decl(name='repos', code=code)

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

# ** function: _method
def _method(name: str) -> StatementAggregate:
    '''
    Create a public method member.

    :param name: The method name.
    :type name: str
    :return: The member statement.
    :rtype: StatementAggregate
    '''

    # A method member is what the CRUD rule counts.
    return _member('method', [_decl(_func(name))])

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

# ** function: _repo
def _repo(members: list, base: str = 'FeatureService',
          name: str = 'feature') -> DeclarationAggregate:
    '''
    Create a repos group containing one repo section.

    :param members: The class members.
    :type members: list
    :param base: The base class name, or None for no base.
    :type base: str
    :param name: The repo section name.
    :type name: str
    :return: The module declaration.
    :rtype: DeclarationAggregate
    '''

    # The section keyword is what the base and CRUD rules match.
    return _module([
        _group('repos', [
            _section('** repo', name, [
                _decl(_class('FeatureRepository', members, base=base)),
            ]),
        ]),
    ])

# ** function: _crud
def _crud(extra: str = None) -> list:
    '''
    Create the repos CRUD method members, plus an optional extra method.

    :param extra: An additional public method name, or None.
    :type extra: str
    :return: The method members.
    :rtype: list
    '''

    # The vocabulary is the five required names, in declaration order.
    members = [_method(name) for name in _CRUD_METHODS]
    if extra is not None:
        members.append(_method(extra))
    return members

# ** function: check_repos
def check_repos(module) -> list:
    '''
    Check a module with the repos rule set.

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
        'repos.',
        COMPILER_PROVISION_CACHE_PREFIX,
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
    return [item['error_code'] for item in check_repos(module)]

# *** tests

# ** test: conformant_modules_report_no_findings
def test_conformant_modules_report_no_findings() -> None:
    '''
    Test that the repos fixture yields no findings.
    '''

    # Parse the fixture, then check it with the repos rule set.
    module = _parser().parse_file(_FIXTURES_DIR / 'feature.py')

    # A conformant module has nothing to report.
    assert check_repos(module) == []

# ** test: disallowed_group_reported
def test_disallowed_group_reported() -> None:
    '''
    Test that a group outside the permitted set yields DISALLOWED_REPOS_GROUP.
    '''

    # constants is not a permitted repos group.
    module = _module([
        _group('constants', []),
    ])

    # The disallowed group is the only finding.
    assert _codes(module) == ['DISALLOWED_REPOS_GROUP']

# ** test: invalid_app_import_reported
def test_invalid_app_import_reported() -> None:
    '''
    Test that a disallowed app import yields INVALID_REPOS_APP_IMPORT.
    '''

    # domain is not a sibling and is not interfaces, mappers, or utils.
    module = _module([
        _group('imports', [
            _import_section('app', [
                _import_from('..domain.feature', 'Feature'),
            ]),
        ]),
    ])

    # The disallowed path is the only finding.
    assert _codes(module) == ['INVALID_REPOS_APP_IMPORT']

# ** test: interfaces_mappers_utils_and_sibling_app_imports_allowed
@pytest.mark.parametrize('module_path', [
    '.core',
    '..interfaces.feature',
    '..mappers.feature',
    '..utils.file',
])
def test_interfaces_mappers_utils_and_sibling_app_imports_allowed(module_path: str) -> None:
    '''
    Test that sibling, interfaces, mappers, and utils app imports yield no finding.

    :param module_path: An allowed sibling or component path.
    :type module_path: str
    '''

    # Each path is a sibling or names a component this dialect permits.
    module = _module([
        _group('imports', [
            _import_section('app', [
                _import_from(module_path, 'Feature'),
            ]),
        ]),
    ])

    # The allowed path is satisfactory.
    assert _codes(module) == []

# ** test: repo_missing_base_reported
def test_repo_missing_base_reported() -> None:
    '''
    Test that a repo class with no base yields REPO_MISSING_BASE and repo_name.
    '''

    # The CRUD methods are present so the missing base is the only finding.
    module = _repo(_crud(), base=None)
    findings = check_repos(module)

    # The missing base cites the repo name.
    assert len(findings) == 1
    assert findings[0]['error_code'] == 'REPO_MISSING_BASE'
    assert findings[0]['repo_name'] == 'feature'

# ** test: repo_with_any_base_not_flagged
def test_repo_with_any_base_not_flagged() -> None:
    '''
    Test that a repo class with any base yields no REPO_MISSING_BASE.
    '''

    # Any declared base satisfies. FeatureService is not required by name.
    module = _repo(_crud(), base='Other')

    # A present base is satisfactory.
    assert 'REPO_MISSING_BASE' not in _codes(module)
    assert check_repos(module) == []

# ** test: repo_missing_crud_method_reported
def test_repo_missing_crud_method_reported() -> None:
    '''
    Test that each missing CRUD method yields REPO_MISSING_CRUD_METHOD in sorted order.
    '''

    # No public methods means every required name is missing.
    findings = check_repos(_repo([]))

    # Missing names are reported in sorted order.
    assert [item['error_code'] for item in findings] == ['REPO_MISSING_CRUD_METHOD'] * 5
    assert [item['method_name'] for item in findings] == [
        'delete',
        'exists',
        'get',
        'list',
        'save',
    ]

# ** test: repo_unexpected_public_method_reported
def test_repo_unexpected_public_method_reported() -> None:
    '''
    Test that an extra public method yields REPO_UNEXPECTED_PUBLIC_METHOD.
    '''

    # purge is not part of the CRUD vocabulary.
    findings = check_repos(_repo(_crud(extra='purge')))

    # The extra method is the only finding.
    assert len(findings) == 1
    assert findings[0]['error_code'] == 'REPO_UNEXPECTED_PUBLIC_METHOD'
    assert findings[0]['method_name'] == 'purge'
