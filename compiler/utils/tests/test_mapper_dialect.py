"""Compiler Mapper Dialect Tests"""

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
_FIXTURES_DIR = Path(__file__).resolve().parent / 'fixtures' / 'mappers'

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
    return DeclarationAggregate.new_module_decl(name='mappers', code=code)

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
def _attr(name: str, type_name: str = None,
          value: ExpressionAggregate = None) -> DeclarationAggregate:
    '''
    Create an attribute declaration.

    :param name: The attribute name.
    :type name: str
    :param type_name: The optional class type name.
    :type type_name: str
    :param value: The optional initializer.
    :type value: ExpressionAggregate
    :return: The attribute declaration.
    :rtype: DeclarationAggregate
    '''

    # A type name is a class type. A missing name leaves the annotation unset.
    types = None
    if type_name is not None:
        types = TypeAggregate.new_class_type(name=type_name)
    return DeclarationAggregate.new_attr_decl(name=name, types=types, value=value)

# ** function: _mapper
def _mapper(name: str, members: list) -> DeclarationAggregate:
    '''
    Create a mappers group containing one mapper section.

    :param name: The mapper name.
    :type name: str
    :param members: The class members.
    :type members: list
    :return: The module declaration.
    :rtype: DeclarationAggregate
    '''

    # The group name is what the roles rule reads from the walk.
    return _module([
        _group('mappers', [
            _section('** mapper', name, [
                _decl(_class(name.capitalize(), members, base='Aggregate')),
            ]),
        ]),
    ])

# ** function: check_mapper
def check_mapper(module) -> list:
    '''
    Check a module with the mapper rule set.

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
        'mapper.',
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
    return [item['error_code'] for item in check_mapper(module)]

# *** tests

# ** test: conformant_modules_report_no_findings
@pytest.mark.parametrize('filename', [
    'app.py',
    'di.py',
    'feature.py',
])
def test_conformant_modules_report_no_findings(filename: str) -> None:
    '''
    Test that each mapper fixture yields no findings.

    :param filename: The fixture file name.
    :type filename: str
    '''

    # Parse the fixture, then check it with the mapper rule set.
    module = _parser().parse_file(_FIXTURES_DIR / filename)

    # A conformant module has nothing to report.
    assert check_mapper(module) == []

# ** test: disallowed_group_reported
def test_disallowed_group_reported() -> None:
    '''
    Test that a group outside the permitted set yields DISALLOWED_MAPPER_GROUP.
    '''

    # classes is not a permitted mappers group.
    module = _module([
        _group('classes', []),
    ])

    # The disallowed group is the only finding.
    assert _codes(module) == ['DISALLOWED_MAPPER_GROUP']

# ** test: section_group_mismatch_reported
def test_section_group_mismatch_reported() -> None:
    '''
    Test that a non-mapper section under mappers yields SECTION_GROUP_MISMATCH.
    '''

    # mappers expects mapper sections, not class sections.
    module = _module([
        _group('mappers', [
            _section('** class', 'feature', [
                _decl(_class('Feature', [], base='Aggregate')),
            ]),
        ]),
    ])

    # The keyword mismatch is the only finding.
    assert _codes(module) == ['SECTION_GROUP_MISMATCH']

# ** test: invalid_app_import_reported
def test_invalid_app_import_reported() -> None:
    '''
    Test that a disallowed app import yields INVALID_MAPPER_APP_IMPORT.
    '''

    # repos is neither a sibling nor domain or events.
    module = _module([
        _group('imports', [
            _import_section('app', [
                _import_from('..repos.core', 'Repo'),
            ]),
        ]),
    ])

    # The disallowed path is the only finding.
    assert _codes(module) == ['INVALID_MAPPER_APP_IMPORT']

# ** test: domain_and_events_app_imports_allowed
@pytest.mark.parametrize('module_path', [
    '..domain.feature',
    '..events.feature',
])
def test_domain_and_events_app_imports_allowed(module_path: str) -> None:
    '''
    Test that domain and events app imports yield no app-import finding.

    :param module_path: An allowed domain or events path.
    :type module_path: str
    '''

    # Each path names a component this dialect permits.
    module = _module([
        _group('imports', [
            _import_section('app', [
                _import_from(module_path, 'Feature'),
            ]),
        ]),
    ])

    # The allowed path is satisfactory.
    assert _codes(module) == []

# ** test: roles_missing_classvar_type_reported
def test_roles_missing_classvar_type_reported() -> None:
    '''
    Test that _ROLES not typed ClassVar yields MAPPER_ROLES_MISSING_CLASSVAR_TYPE.
    '''

    # The dict literal is present so the missing ClassVar type is the only finding.
    module = _mapper('feature', [
        _member('attribute', [
            _decl(_attr(
                '_ROLES',
                type_name='str',
                value=ExpressionAggregate.new_dict_literal_expr(),
            )),
        ]),
    ])

    # The missing ClassVar type is the only finding.
    assert _codes(module) == ['MAPPER_ROLES_MISSING_CLASSVAR_TYPE']
