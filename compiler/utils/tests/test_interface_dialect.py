"""Compiler Interface Dialect Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest

# ** app
from ...mappers.artifact import (
    ArtifactDeclarationAggregate,
    ArtifactStatementAggregate,
    SnippetStatementAggregate,
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
from ..typecheck import INTERFACE_RULE_SET, ConformanceChecker

# *** constants

# ** constant: fixtures_dir
_FIXTURES_DIR = Path(__file__).resolve().parent / 'fixtures' / 'interfaces'

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
    return DeclarationAggregate.new_module_decl(name='interfaces', code=code)

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

# ** function: _decorator
def _decorator(name: str) -> StatementAggregate:
    '''
    Create a bare decorator expression statement.

    :param name: The decorator name.
    :type name: str
    :return: The expression statement.
    :rtype: StatementAggregate
    '''

    # A bare name encodes as the decorator string the abstract-method rule matches.
    return StatementAggregate.new_expr_stmt(ExpressionAggregate.new_name_expr(name))

# ** function: _raise_not_implemented
def _raise_not_implemented() -> SnippetStatementAggregate:
    '''
    Create a snippet whose body is exactly raise NotImplementedError(...).

    :return: The snippet statement.
    :rtype: SnippetStatementAggregate
    '''

    # The callee name is what the abstract-method rule matches.
    return SnippetStatementAggregate.new_snippet_stmt(
        code=StatementAggregate.new_raise_stmt(
            expr=ExpressionAggregate.new_call_expr(
                ExpressionAggregate.new_name_expr('NotImplementedError'),
            ),
        ),
    )

# ** function: _func
def _func(name: str, body: list = None) -> DeclarationAggregate:
    '''
    Create a function declaration.

    :param name: The function name.
    :type name: str
    :param body: The body statements, or None.
    :type body: list
    :return: The function declaration.
    :rtype: DeclarationAggregate
    '''

    # The function type is what marks the declaration as a function.
    return DeclarationAggregate.new_func_decl(
        name=name,
        type=TypeAggregate.new_func_type(params=[]),
        body=body or [],
    )

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

# ** function: _interface
def _interface(name: str, members: list, base: str = 'Service') -> DeclarationAggregate:
    '''
    Create an interfaces group containing one interface section.

    :param name: The interface name.
    :type name: str
    :param members: The class members.
    :type members: list
    :param base: The base class name, or None for no base.
    :type base: str
    :return: The module declaration.
    :rtype: DeclarationAggregate
    '''

    # The section keyword is what the abstract-method rule matches.
    return _module([
        _group('interfaces', [
            _section('** interface', name, [
                _decl(_class(name.capitalize(), members, base=base)),
            ]),
        ]),
    ])

# ** function: check_interface
def check_interface(module) -> list:
    '''
    Check a module with the interface rule set.

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
        rule_set=INTERFACE_RULE_SET,
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
    return [item['error_code'] for item in check_interface(module)]

# *** tests

# ** test: conformant_modules_report_no_findings
@pytest.mark.parametrize('filename', [
    'app.py',
    'cli.py',
    'core.py',
    'di.py',
    'error.py',
    'feature.py',
    'file.py',
    'logging.py',
    'middleware.py',
    'sqlite.py',
])
def test_conformant_modules_report_no_findings(filename: str) -> None:
    '''
    Test that each interface fixture yields no findings.

    :param filename: The fixture file name.
    :type filename: str
    '''

    # Parse the fixture, then check it with the interface rule set.
    module = _parser().parse_file(_FIXTURES_DIR / filename)

    # A conformant module has nothing to report.
    assert check_interface(module) == []

# ** test: disallowed_group_reported
def test_disallowed_group_reported() -> None:
    '''
    Test that a group outside the permitted set yields DISALLOWED_INTERFACE_GROUP.
    '''

    # models is not a permitted interfaces group.
    module = _module([
        _group('models', []),
    ])

    # The disallowed group is the only finding.
    assert _codes(module) == ['DISALLOWED_INTERFACE_GROUP']

# ** test: invalid_app_import_reported
def test_invalid_app_import_reported() -> None:
    '''
    Test that a non-sibling, non-mappers app import yields INVALID_INTERFACE_APP_IMPORT.
    '''

    # repos is neither a sibling nor the mappers component.
    module = _module([
        _group('imports', [
            _import_section('app', [
                _import_from('..repos.core', 'Repo'),
            ]),
        ]),
    ])

    # The disallowed path is the only finding.
    assert _codes(module) == ['INVALID_INTERFACE_APP_IMPORT']

# ** test: mappers_and_sibling_app_imports_allowed
@pytest.mark.parametrize('module_path', [
    '.core',
    '..mappers.app',
])
def test_mappers_and_sibling_app_imports_allowed(module_path: str) -> None:
    '''
    Test that sibling and mappers app imports yield no app-import finding.

    :param module_path: An allowed sibling or mappers path.
    :type module_path: str
    '''

    # Each path is a sibling or names the mappers component.
    module = _module([
        _group('imports', [
            _import_section('app', [
                _import_from(module_path, 'Service'),
            ]),
        ]),
    ])

    # The allowed path is satisfactory.
    assert _codes(module) == []

# ** test: missing_abstractmethod_reported
def test_missing_abstractmethod_reported() -> None:
    '''
    Test that an interface method without abstractmethod yields a finding.
    '''

    # The raise body is present so the missing decorator is the only finding.
    module = _interface('app_service', [
        _member('method', [
            _decl(_func('exists', body=[_raise_not_implemented()])),
        ]),
    ])

    # The missing decorator is the only finding.
    assert _codes(module) == ['INTERFACE_METHOD_MISSING_ABSTRACTMETHOD']

# ** test: pass_body_instead_of_not_implemented_reported
def test_pass_body_instead_of_not_implemented_reported() -> None:
    '''
    Test that an abstract method whose body is pass yields a finding.
    '''

    # pass is not exactly raise NotImplementedError(...).
    module = _interface('app_service', [
        _member('method', [
            _decorator('abstractmethod'),
            _decl(_func('exists', body=[
                SnippetStatementAggregate.new_snippet_stmt(
                    code=StatementAggregate.new_pass_stmt(),
                ),
            ])),
        ]),
    ])

    # The missing raise is the only finding.
    assert _codes(module) == ['INTERFACE_METHOD_MISSING_NOT_IMPLEMENTED']

# ** test: root_marker_interface_exempt
def test_root_marker_interface_exempt() -> None:
    '''
    Test that an interface whose sole base is ABC yields no interface-method findings.
    '''

    # The method is neither abstract nor a raise. The root marker is exempt.
    module = _interface('service', [
        _member('method', [
            _decl(_func('exists', body=[
                SnippetStatementAggregate.new_snippet_stmt(
                    code=StatementAggregate.new_pass_stmt(),
                ),
            ])),
        ]),
    ], base='ABC')

    # The exemption is satisfactory.
    assert check_interface(module) == []
