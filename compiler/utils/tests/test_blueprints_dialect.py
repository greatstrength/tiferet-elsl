"""Compiler Blueprints Dialect Tests"""

# *** imports

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
)
from ..semantic import SymbolTableBuilder
from ..typecheck import BLUEPRINTS_RULE_SET, ConformanceChecker

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
    return DeclarationAggregate.new_module_decl(name='blueprints', code=code)

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

# ** function: check_blueprints
def check_blueprints(module) -> list:
    '''
    Check a module with the blueprints rule set.

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
        rule_set=BLUEPRINTS_RULE_SET,
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
    return [item['error_code'] for item in check_blueprints(module)]

# *** tests

# ** test: blueprints_permitted_group_accepts_function_composition_groups
def test_blueprints_permitted_group_accepts_function_composition_groups() -> None:
    '''
    Test that the composition groups yield no DISALLOWED_BLUEPRINTS_GROUP.
    '''

    # These are the tier-1 groups a blueprints module may declare.
    module = _module([
        _group('imports', []),
        _group('constants', []),
        _group('functions', []),
        _group('blueprints', []),
        _group('exports', []),
    ])

    # Each permitted group is satisfactory.
    assert 'DISALLOWED_BLUEPRINTS_GROUP' not in _codes(module)
    assert check_blueprints(module) == []

# ** test: blueprints_permitted_group_rejects_classes
def test_blueprints_permitted_group_rejects_classes() -> None:
    '''
    Test that a classes group yields DISALLOWED_BLUEPRINTS_GROUP.
    '''

    # classes is not a permitted blueprints group.
    module = _module([
        _group('classes', []),
    ])

    # The disallowed group is the only finding.
    assert _codes(module) == ['DISALLOWED_BLUEPRINTS_GROUP']

# ** test: blueprints_app_import_permits_composition_dependencies
@pytest.mark.parametrize('module_path,name', [
    ('..assets.core', 'EN_US'),
    ('..contexts.feature', 'FeatureContext'),
    ('..di.container', 'Container'),
    ('..events.app', 'GetApp'),
    ('.core', 'build_app'),
    ('..', 'a'),
])
def test_blueprints_app_import_permits_composition_dependencies(
        module_path: str, name: str) -> None:
    '''
    Test that composition dependencies and the root alias yield no app-import finding.

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

# ** test: blueprints_app_import_rejects_infrastructure_dependencies
@pytest.mark.parametrize('module_path', [
    '..mappers.feature',
    '..utils.file',
    '..repos.feature',
])
def test_blueprints_app_import_rejects_infrastructure_dependencies(
        module_path: str) -> None:
    '''
    Test that a mappers, utils, or repos app import yields INVALID_BLUEPRINTS_APP_IMPORT.

    :param module_path: A disallowed infrastructure path.
    :type module_path: str
    '''

    # Those component types are omitted from the blueprints allowance.
    module = _module([
        _group('imports', [
            _import_section('app', [
                _import_from(module_path, 'Feature'),
            ]),
        ]),
    ])

    # The disallowed path is the only finding.
    assert _codes(module) == ['INVALID_BLUEPRINTS_APP_IMPORT']

# ** test: blueprints_group_requires_blueprint_sections
def test_blueprints_group_requires_blueprint_sections() -> None:
    '''
    Test that a non-blueprint section under blueprints yields SECTION_GROUP_MISMATCH.
    '''

    # blueprints expects blueprint sections, not function sections.
    module = _module([
        _group('blueprints', [
            _section('** function', 'build_app', []),
        ]),
    ])

    # The keyword mismatch is the only finding.
    assert _codes(module) == ['SECTION_GROUP_MISMATCH']
