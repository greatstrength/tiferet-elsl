"""Compiler Assets Dialect Tests"""

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
from ..typecheck import ASSET_RULE_SET, ConformanceChecker

# *** constants

# ** constant: fixtures_dir
_FIXTURES_DIR = Path(__file__).resolve().parent / 'fixtures' / 'assets'

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
    return DeclarationAggregate.new_module_decl(name='assets', code=code)

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
    Create an attribute declaration.

    :param name: The attribute name.
    :type name: str
    :return: The attribute declaration.
    :rtype: DeclarationAggregate
    '''

    # The name is the assignment target the constant rule compares.
    return DeclarationAggregate.new_attr_decl(name=name)

# ** function: check_assets
def check_assets(module) -> list:
    '''
    Check a module with the assets rule set.

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
        rule_set=ASSET_RULE_SET,
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
    return [item['error_code'] for item in check_assets(module)]

# *** tests

# ** test: conformant_modules_report_no_findings
@pytest.mark.parametrize('filename', [
    'core.py',
    'error.py',
    'exceptions.py',
])
def test_conformant_modules_report_no_findings(filename: str) -> None:
    '''
    Test that each assets fixture yields no findings.

    :param filename: The fixture file name.
    :type filename: str
    '''

    # Parse the fixture, then check it with the assets rule set.
    module = _parser().parse_file(_FIXTURES_DIR / filename)

    # A conformant module has nothing to report.
    assert check_assets(module) == []

# ** test: disallowed_group_reported
def test_disallowed_group_reported() -> None:
    '''
    Test that a group outside the permitted set yields DISALLOWED_ASSET_GROUP.
    '''

    # models is not a permitted assets group.
    module = _module([
        _group('models', []),
    ])

    # The disallowed group is the only finding.
    assert _codes(module) == ['DISALLOWED_ASSET_GROUP']

# ** test: section_group_mismatch_reported
def test_section_group_mismatch_reported() -> None:
    '''
    Test that a non-constant section under constants yields SECTION_GROUP_MISMATCH.
    '''

    # constants expects constant sections, not class sections.
    module = _module([
        _group('constants', [
            _section('** class', 'foo', [
                _decl(_class('Foo', [])),
            ]),
        ]),
    ])

    # The keyword mismatch is the only finding.
    assert _codes(module) == ['SECTION_GROUP_MISMATCH']

# ** test: constant_name_mismatch_reported
def test_constant_name_mismatch_reported() -> None:
    '''
    Test that a constant whose target is not the uppercased section name yields a finding.
    '''

    # foo expects assignment target FOO.
    module = _module([
        _group('constants', [
            _section('** constant', 'foo', [
                _decl(_attr('BAR')),
            ]),
        ]),
    ])

    # The mismatched target is the only finding.
    assert _codes(module) == ['ASSET_CONSTANT_NAME_MISMATCH']

# ** test: invalid_app_import_reported
def test_invalid_app_import_reported() -> None:
    '''
    Test that a non-sibling app import yields INVALID_ASSET_APP_IMPORT.
    '''

    # A component path is not a same-package sibling.
    module = _module([
        _group('imports', [
            _import_section('app', [
                _import_from('..domain.error', 'Error'),
            ]),
        ]),
    ])

    # The disallowed path is the only finding.
    assert _codes(module) == ['INVALID_ASSET_APP_IMPORT']

# ** test: sibling_app_import_allowed
def test_sibling_app_import_allowed() -> None:
    '''
    Test that a same-package sibling app import yields no app-import finding.
    '''

    # A single leading dot is a sibling import.
    module = _module([
        _group('imports', [
            _import_section('app', [
                _import_from('.core', 'X'),
            ]),
        ]),
    ])

    # The sibling path is satisfactory.
    assert _codes(module) == []
