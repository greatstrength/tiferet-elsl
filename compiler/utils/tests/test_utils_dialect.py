"""Compiler Utils Dialect Tests"""

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
    ParamListAggregate,
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
_FIXTURES_DIR = Path(__file__).resolve().parent / 'fixtures' / 'utils'

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
    return DeclarationAggregate.new_module_decl(name='utils', code=code)

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
def _member(role: str, body: list, qualifier: str = None) -> StatementAggregate:
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

    # The role is the member name. The qualifier is what the pairing rule reads.
    return _decl(ArtifactDeclarationAggregate.new_member_decl(
        role,
        member_body=body,
        qualifier=qualifier,
    ))

# ** function: _func
def _func(name: str, params: list = None) -> DeclarationAggregate:
    '''
    Create a function declaration.

    :param name: The function name.
    :type name: str
    :param params: The optional parameter list.
    :type params: list
    :return: The function declaration.
    :rtype: DeclarationAggregate
    '''

    # The function type is what marks the declaration as a function.
    return DeclarationAggregate.new_func_decl(
        name=name,
        type=TypeAggregate.new_func_type(params=params or []),
        body=[],
    )

# ** function: _class
def _class(name: str, members: list, base: str = 'FileService') -> DeclarationAggregate:
    '''
    Create a class declaration.

    :param name: The class name.
    :type name: str
    :param members: The body statements.
    :type members: list
    :param base: The base class name.
    :type base: str
    :return: The class declaration.
    :rtype: DeclarationAggregate
    '''

    # A base name is stored as the class type's subtype.
    return DeclarationAggregate.new_class_decl(
        name=name,
        subclasses=TypeAggregate.new_class_type(name=base),
        doc_string=None,
        members=members,
    )

# ** function: _context_manager
def _context_manager(name: str, params: list = None) -> StatementAggregate:
    '''
    Create a method member labelled as a context manager.

    :param name: The method name.
    :type name: str
    :param params: The optional parameter list.
    :type params: list
    :return: The member statement.
    :rtype: StatementAggregate
    '''

    # The qualifier is the label the pairing rule matches.
    return _member(
        'method',
        [_decl(_func(name, params=params))],
        qualifier='context manager',
    )

# ** function: _util
def _util(members: list) -> DeclarationAggregate:
    '''
    Create a utils group containing one util section.

    :param members: The class members.
    :type members: list
    :return: The module declaration.
    :rtype: DeclarationAggregate
    '''

    # The section keyword is what the pairing rule matches.
    return _module([
        _group('utils', [
            _section('** util', 'file_loader', [
                _decl(_class('FileLoader', members)),
            ]),
        ]),
    ])

# ** function: _exit_params
def _exit_params() -> list:
    '''
    Create the four parameters an __exit__ method must declare.

    :return: self plus the three exception-info parameters.
    :rtype: list
    '''

    # Arity is the parameter count, including self.
    return [
        ParamListAggregate.new('self'),
        ParamListAggregate.new('exc_type'),
        ParamListAggregate.new('exc'),
        ParamListAggregate.new('tb'),
    ]

# ** function: check_utils
def check_utils(module) -> list:
    '''
    Check a module with the utils rule set.

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
        'utils.',
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
    return [item['error_code'] for item in check_utils(module)]

# *** tests

# ** test: conformant_modules_report_no_findings
@pytest.mark.parametrize('filename', [
    'file.py',
    'json.py',
    'sqlite.py',
    'yaml.py',
])
def test_conformant_modules_report_no_findings(filename: str) -> None:
    '''
    Test that each utils fixture yields no findings.

    :param filename: The fixture file name.
    :type filename: str
    '''

    # Parse the fixture, then check it with the utils rule set.
    module = _parser().parse_file(_FIXTURES_DIR / filename)

    # A conformant module has nothing to report.
    assert check_utils(module) == []

# ** test: disallowed_group_reported
def test_disallowed_group_reported() -> None:
    '''
    Test that a group outside the permitted set yields DISALLOWED_UTILS_GROUP.
    '''

    # models is not a permitted utils group.
    module = _module([
        _group('models', []),
    ])

    # The disallowed group is the only finding.
    assert _codes(module) == ['DISALLOWED_UTILS_GROUP']

# ** test: invalid_app_import_reported
def test_invalid_app_import_reported() -> None:
    '''
    Test that a disallowed app import yields INVALID_UTILS_APP_IMPORT.
    '''

    # repos is neither a sibling nor interfaces or mappers.
    module = _module([
        _group('imports', [
            _import_section('app', [
                _import_from('..repos.core', 'Repo'),
            ]),
        ]),
    ])

    # The disallowed path is the only finding.
    assert _codes(module) == ['INVALID_UTILS_APP_IMPORT']

# ** test: interfaces_and_mappers_app_import_allowed
@pytest.mark.parametrize('module_path', [
    '..interfaces.file',
    '..mappers.file',
])
def test_interfaces_and_mappers_app_import_allowed(module_path: str) -> None:
    '''
    Test that interfaces and mappers app imports yield no app-import finding.

    :param module_path: An allowed interfaces or mappers path.
    :type module_path: str
    '''

    # Each path names a component this dialect permits.
    module = _module([
        _group('imports', [
            _import_section('app', [
                _import_from(module_path, 'File'),
            ]),
        ]),
    ])

    # The allowed path is satisfactory.
    assert _codes(module) == []

# ** test: context_manager_pair_reports_no_findings
def test_context_manager_pair_reports_no_findings() -> None:
    '''
    Test that a labelled enter and exit pair with exit arity 4 yields no findings.
    '''

    # Both partners are labelled, and exit takes self plus three parameters.
    module = _util([
        _context_manager('__enter__'),
        _context_manager('__exit__', params=_exit_params()),
    ])

    # A complete pair is satisfactory.
    assert check_utils(module) == []

# ** test: lone_enter_without_exit_reported
def test_lone_enter_without_exit_reported() -> None:
    '''
    Test that only a labelled enter yields CONTEXT_MANAGER_MISSING_PAIR.
    '''

    # Exit is absent, so the pair is incomplete.
    module = _util([
        _context_manager('__enter__'),
    ])

    # The missing partner is the only finding.
    assert _codes(module) == ['CONTEXT_MANAGER_MISSING_PAIR']

# ** test: wrong_name_context_manager_member_reported
def test_wrong_name_context_manager_member_reported() -> None:
    '''
    Test that a context-manager label on another name yields a finding.
    '''

    # close is neither enter nor exit.
    module = _util([
        _context_manager('close'),
    ])

    # The illegal name is the only finding.
    assert _codes(module) == ['INVALID_CONTEXT_MANAGER_MEMBER']
