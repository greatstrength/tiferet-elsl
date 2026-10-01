"""Compiler Domain Dialect Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest
from tiferet_ly.repos.grammar import GrammarConfigRepository
from tiferet_ly.repos.production import ProductionConfigRepository
from tiferet_ly.repos.token import TokenConfigRepository

# ** app
from ...domain.ast import ExprKind
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
from ..typecheck import DOMAIN_RULE_SET, ConformanceChecker

# *** constants

# ** constant: fixtures_dir
_FIXTURES_DIR = Path(__file__).resolve().parent / 'fixtures' / 'domain'

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
    return DeclarationAggregate.new_module_decl(name='domain', code=code)

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

# ** function: _field
def _field(description: str = None) -> ExpressionAggregate:
    '''
    Create a Field call, optionally with a description keyword.

    :param description: The description text, or None.
    :type description: str
    :return: The call expression.
    :rtype: ExpressionAggregate
    '''

    # A missing description is a Field call with no keyword arguments.
    arguments = None
    if description is not None:
        arguments = ExpressionAggregate.new_args_list_expr(
            ExpressionAggregate.new_kwarg_expr(
                name='description',
                value=ExpressionAggregate(kind=ExprKind.STR_VAL, value=description),
            ),
        )
    return ExpressionAggregate.new_call_expr(
        ExpressionAggregate.new_name_expr('Field'),
        arguments,
    )

# ** function: _model
def _model(name: str, members: list, base: str = 'DomainObject') -> ArtifactStatementAggregate:
    '''
    Create a models group containing one model section.

    :param name: The model name.
    :type name: str
    :param members: The class members.
    :type members: list
    :param base: The base class name, or None for no base.
    :type base: str
    :return: The models group.
    :rtype: ArtifactStatementAggregate
    '''

    # The group name is what the attribute rule reads from the walk.
    return _group('models', [
        _section('** model', name, [
            _decl(_class(name.capitalize(), members, base=base)),
        ]),
    ])

# ** function: check_domain
def check_domain(module) -> list:
    '''
    Check a module with the domain rule set.

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
        rule_set=DOMAIN_RULE_SET,
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
    return [item['error_code'] for item in check_domain(module)]

# *** tests

# ** test: conformant_modules_report_no_findings
@pytest.mark.parametrize('filename', [
    'di.py',
    'error.py',
    'logging.py',
    'request.py',
])
def test_conformant_modules_report_no_findings(filename: str) -> None:
    '''
    Test that each domain fixture yields no findings.

    :param filename: The fixture file name.
    :type filename: str
    '''

    # Parse the fixture, then check it with the domain rule set.
    module = _parser().parse_file(_FIXTURES_DIR / filename)

    # A conformant module has nothing to report.
    assert check_domain(module) == []

# ** test: disallowed_group_reported
def test_disallowed_group_reported() -> None:
    '''
    Test that a utilities group yields DISALLOWED_DOMAIN_GROUP.
    '''

    # utilities is not a permitted domain group.
    module = _module([
        _group('utilities', []),
    ])

    # The disallowed group is the only finding.
    assert _codes(module) == ['DISALLOWED_DOMAIN_GROUP']

# ** test: section_group_mismatch_reported
def test_section_group_mismatch_reported() -> None:
    '''
    Test that a class section under models yields SECTION_GROUP_MISMATCH.
    '''

    # models expects model sections, not class sections.
    module = _module([
        _group('models', [
            _section('** class', 'error', [
                _decl(_class('Error', [], base='DomainObject')),
            ]),
        ]),
    ])

    # The keyword mismatch is the only finding.
    assert _codes(module) == ['SECTION_GROUP_MISMATCH']

# ** test: invalid_app_import_reported
def test_invalid_app_import_reported() -> None:
    '''
    Test that a non-sibling, non-assets app import yields INVALID_DOMAIN_APP_IMPORT.
    '''

    # repos is neither a sibling nor the assets component.
    module = _module([
        _group('imports', [
            _import_section('app', [
                _import_from('..repos.core', 'Repo'),
            ]),
        ]),
    ])

    # The disallowed path is the only finding.
    assert _codes(module) == ['INVALID_DOMAIN_APP_IMPORT']

# ** test: sibling_app_import_allowed
def test_sibling_app_import_allowed() -> None:
    '''
    Test that a same-package sibling app import yields no app-import finding.
    '''

    # A single leading dot is a sibling import.
    module = _module([
        _group('imports', [
            _import_section('app', [
                _import_from('.error', 'Error'),
            ]),
        ]),
    ])

    # The sibling path is satisfactory.
    assert _codes(module) == []

# ** test: domain_app_import_satisfied_for_assets_reference
def test_domain_app_import_satisfied_for_assets_reference() -> None:
    '''
    Test that an assets app import yields no app-import finding.
    '''

    # assets is the component type this dialect permits.
    module = _module([
        _group('imports', [
            _import_section('app', [
                _import_from('..assets.core', 'X'),
            ]),
        ]),
    ])

    # The assets path is satisfactory.
    assert _codes(module) == []

# ** test: domain_model_base_class_satisfied_for_any_base
def test_domain_model_base_class_satisfied_for_any_base() -> None:
    '''
    Test that a model class with any base yields no missing-base finding.
    '''

    # Any declared base satisfies. DomainObject is not required by name.
    module = _module([
        _model('ping', [], base='Other'),
    ])

    # A present base is satisfactory.
    assert 'MODEL_MISSING_DOMAIN_OBJECT_BASE' not in _codes(module)

# ** test: domain_model_base_class_violated_for_no_base
def test_domain_model_base_class_violated_for_no_base() -> None:
    '''
    Test that a model class with no base yields MODEL_MISSING_DOMAIN_OBJECT_BASE.
    '''

    # Omitting the base is the violation. The section name is the model name.
    module = _module([
        _model('ping', [], base=None),
    ])
    findings = check_domain(module)

    # The missing base cites the model name.
    assert len(findings) == 1
    assert findings[0]['error_code'] == 'MODEL_MISSING_DOMAIN_OBJECT_BASE'
    assert findings[0]['model_name'] == 'ping'

# ** test: domain_attribute_satisfied_for_typed_field_with_description
def test_domain_attribute_satisfied_for_typed_field_with_description() -> None:
    '''
    Test that a typed Field attribute with description yields no findings.
    '''

    # The attribute has a type, a Field call, and a description keyword.
    module = _module([
        _model('error', [
            _member('attribute', [
                _decl(_attr(
                    'code',
                    type_name='str',
                    value=_field(description='The stable error code.'),
                )),
            ]),
        ]),
    ])

    # A complete domain attribute is satisfactory.
    assert check_domain(module) == []

# ** test: domain_attribute_ignored_outside_models_group
def test_domain_attribute_ignored_outside_models_group() -> None:
    '''
    Test that an untyped attribute outside models yields no domain-attribute finding.
    '''

    # classes is not the models group, so the attribute rule does not apply.
    module = _module([
        _group('classes', [
            _section('** class', 'helper', [
                _decl(_class('Helper', [
                    _member('attribute', [
                        _decl(_attr('code')),
                    ]),
                ], base='object')),
            ]),
        ]),
    ])

    # An attribute outside models is not a domain-attribute finding.
    assert 'DOMAIN_ATTRIBUTE_MISSING_TYPE' not in _codes(module)
    assert check_domain(module) == []

# ** test: domain_attribute_exempt_for_classvar
def test_domain_attribute_exempt_for_classvar() -> None:
    '''
    Test that a ClassVar attribute under models yields no domain-attribute finding.
    '''

    # ClassVar is exempt even without a Field call.
    module = _module([
        _model('error', [
            _member('attribute', [
                _decl(_attr('model_name', type_name='ClassVar')),
            ]),
        ]),
    ])

    # The exemption is satisfactory.
    assert check_domain(module) == []

# ** test: domain_attribute_exempt_for_leading_underscore
def test_domain_attribute_exempt_for_leading_underscore() -> None:
    '''
    Test that a private attribute under models yields no domain-attribute finding.
    '''

    # A leading underscore is exempt even when the attribute is untyped.
    module = _module([
        _model('error', [
            _member('attribute', [
                _decl(_attr('_private')),
            ]),
        ]),
    ])

    # The exemption is satisfactory.
    assert check_domain(module) == []

# ** test: domain_attribute_violated_for_missing_type
def test_domain_attribute_violated_for_missing_type() -> None:
    '''
    Test that an untyped models attribute yields DOMAIN_ATTRIBUTE_MISSING_TYPE.
    '''

    # The Field call is present so the missing type is the only finding.
    module = _module([
        _model('error', [
            _member('attribute', [
                _decl(_attr('code', value=_field(description='The code.'))),
            ]),
        ]),
    ])

    # The missing annotation is the only finding.
    assert _codes(module) == ['DOMAIN_ATTRIBUTE_MISSING_TYPE']

# ** test: domain_attribute_violated_for_missing_field_call
def test_domain_attribute_violated_for_missing_field_call() -> None:
    '''
    Test that a typed models attribute without Field yields DOMAIN_ATTRIBUTE_MISSING_FIELD.
    '''

    # The type is present. The initializer is not a Field call.
    module = _module([
        _model('error', [
            _member('attribute', [
                _decl(_attr('code', type_name='str')),
            ]),
        ]),
    ])

    # The missing Field call is the only finding.
    assert _codes(module) == ['DOMAIN_ATTRIBUTE_MISSING_FIELD']

# ** test: domain_attribute_violated_for_missing_description
def test_domain_attribute_violated_for_missing_description() -> None:
    '''
    Test that a Field call without description yields DOMAIN_ATTRIBUTE_MISSING_DESCRIPTION.
    '''

    # Field is present, but it carries no description keyword.
    module = _module([
        _model('error', [
            _member('attribute', [
                _decl(_attr('code', type_name='str', value=_field())),
            ]),
        ]),
    ])

    # The missing description is the only finding.
    assert _codes(module) == ['DOMAIN_ATTRIBUTE_MISSING_DESCRIPTION']
