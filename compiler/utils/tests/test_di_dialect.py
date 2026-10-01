"""Compiler DI Dialect Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest
from tiferet_ly.repos.grammar import GrammarConfigRepository
from tiferet_ly.repos.production import ProductionConfigRepository
from tiferet_ly.repos.token import TokenConfigRepository

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
from ..lexer import TiferetLexer
from ..parser import TiferetParser
from ..semantic import SymbolTableBuilder
from ..typecheck import DI_RULE_SET, ConformanceChecker

# *** constants

# ** constant: fixtures_dir
_FIXTURES_DIR = Path(__file__).resolve().parent / 'fixtures' / 'di'

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
        self.tokens = TokenConfigRepository(
            token_config='compiler/assets/tokens.yml',
        ).list()
        self.grammars = GrammarConfigRepository(
            grammar_config='compiler/assets/grammars.yml',
        ).list()
        self.productions = ProductionConfigRepository(
            production_config='compiler/assets/productions.yml',
        ).list()
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
    return DeclarationAggregate.new_module_decl(name='di', code=code)

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

# ** function: _class_module
def _class_module(members: list, base: str = 'ABC') -> DeclarationAggregate:
    '''
    Create a classes group containing one class section.

    :param members: The class members.
    :type members: list
    :param base: The base class name.
    :type base: str
    :return: The module declaration.
    :rtype: DeclarationAggregate
    '''

    # The class section keyword is what the abstract-method rule matches.
    return _module([
        _group('classes', [
            _section('** class', 'container', [
                _decl(DeclarationAggregate.new_class_decl(
                    name='Container',
                    subclasses=TypeAggregate.new_class_type(name=base),
                    doc_string=None,
                    members=members,
                )),
            ]),
        ]),
    ])

# ** function: _abstract
def _abstract(name: str, body: list) -> StatementAggregate:
    '''
    Create an abstract method member.

    :param name: The method name.
    :type name: str
    :param body: The function body.
    :type body: list
    :return: The member statement.
    :rtype: StatementAggregate
    '''

    # The decorator precedes the inner declaration, as a parsed member does.
    return _member('method', [
        _decorator('abstractmethod'),
        _decl(_func(name, body=body)),
    ])

# ** function: check_di
def check_di(module) -> list:
    '''
    Check a module with the DI rule set.

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
        rule_set=DI_RULE_SET,
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
    return [item['error_code'] for item in check_di(module)]

# *** tests

# ** test: conformant_modules_report_no_findings
@pytest.mark.parametrize('filename', [
    'core.py',
    'dependency_injector.py',
])
def test_conformant_modules_report_no_findings(filename: str) -> None:
    '''
    Test that each DI fixture yields no findings.

    :param filename: The fixture file name.
    :type filename: str
    '''

    # Parse the fixture, then check it with the DI rule set.
    module = _parser().parse_file(_FIXTURES_DIR / filename)

    # A conformant module has nothing to report.
    assert check_di(module) == []

# ** test: pure_abstract_contract_reports_no_findings
def test_pure_abstract_contract_reports_no_findings() -> None:
    '''
    Test that a class whose methods are all abstract yields no findings.
    '''

    # Every method is abstract and raises NotImplementedError.
    module = _class_module([
        _abstract('get', [_raise_not_implemented()]),
        _abstract('has', [_raise_not_implemented()]),
    ])

    # An abstract contract is satisfactory.
    assert check_di(module) == []

# ** test: mixed_abstract_concrete_contract_reports_no_findings
def test_mixed_abstract_concrete_contract_reports_no_findings() -> None:
    '''
    Test that a mix of abstract and concrete methods yields no findings.
    '''

    # Only the abstract method is checked. The concrete method is ignored.
    module = _class_module([
        _abstract('get', [_raise_not_implemented()]),
        _member('method', [_decl(_func('has'))]),
    ])

    # A mixed contract is satisfactory.
    assert check_di(module) == []

# ** test: fully_concrete_implementation_reports_no_findings
def test_fully_concrete_implementation_reports_no_findings() -> None:
    '''
    Test that a class with no abstract methods yields no findings.
    '''

    # No abstractmethod decorator means the body rule does not apply.
    module = _class_module([
        _member('method', [_decl(_func('get'))]),
    ], base='Container')

    # A concrete implementation is satisfactory.
    assert check_di(module) == []

# ** test: abstract_method_missing_not_implemented_reported
def test_abstract_method_missing_not_implemented_reported() -> None:
    '''
    Test that an abstract method without the raise body yields a finding.
    '''

    # pass is not exactly raise NotImplementedError(...).
    module = _class_module([
        _abstract('get', [
            SnippetStatementAggregate.new_snippet_stmt(
                code=StatementAggregate.new_pass_stmt(),
            ),
        ]),
    ])

    # The missing raise is the only finding.
    assert _codes(module) == ['DI_ABSTRACT_METHOD_MISSING_NOT_IMPLEMENTED']

# ** test: disallowed_group_reported
def test_disallowed_group_reported() -> None:
    '''
    Test that a group outside the permitted set yields DISALLOWED_DI_GROUP.
    '''

    # models is not a permitted DI group.
    module = _module([
        _group('models', []),
    ])

    # The disallowed group is the only finding.
    assert _codes(module) == ['DISALLOWED_DI_GROUP']

# ** test: invalid_app_import_reported
def test_invalid_app_import_reported() -> None:
    '''
    Test that a disallowed app import yields INVALID_DI_APP_IMPORT.
    '''

    # repos is neither a sibling nor domain or interfaces.
    module = _module([
        _group('imports', [
            _import_section('app', [
                _import_from('..repos.core', 'Repo'),
            ]),
        ]),
    ])

    # The disallowed path is the only finding.
    assert _codes(module) == ['INVALID_DI_APP_IMPORT']

# ** test: domain_and_interfaces_app_imports_allowed
@pytest.mark.parametrize('module_path', [
    '..domain.error',
    '..interfaces.container',
])
def test_domain_and_interfaces_app_imports_allowed(module_path: str) -> None:
    '''
    Test that domain and interfaces app imports yield no app-import finding.

    :param module_path: An allowed component path.
    :type module_path: str
    '''

    # Each path names a component this dialect permits.
    module = _module([
        _group('imports', [
            _import_section('app', [
                _import_from(module_path, 'Service'),
            ]),
        ]),
    ])

    # The allowed path is satisfactory.
    assert _codes(module) == []
