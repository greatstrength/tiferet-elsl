"""Compiler Default Provision Catalog Tests"""

# *** imports

# ** core
import ast
import inspect
import re
from importlib import import_module
from pathlib import Path

# ** app
from compiler.assets.core import create_default_provision_data
from ..provision import COMPILER_DEFAULT_PROVISIONS
from compiler.utils.core import Specification
from compiler.utils.semantic import Production

# *** constants

# ** constant: core_path
_CORE_PATH = Path(__file__).resolve().parent.parent / 'core.py'

# ** constant: provision_path
_PROVISION_PATH = Path(__file__).resolve().parent.parent / 'provision.py'

# ** constant: value_keys
_VALUE_KEYS = (
    'kind',
    'applies_to',
    'module_path',
    'class_name',
    'parameters',
)

# ** constant: forbidden_names
_FORBIDDEN_NAMES = (
    'COMMON_RULE_SET',
    'AllOf',
    'AnyOf',
    'Not',
    'optimizer.evt_grp_envelope',
    'generator.imports_group',
    'create_service_dependency',
    'create_default_error_data',
    'CORE_DEFAULT_FEATURES',
    'get_feature',
    'build_app',
)

# ** constant: forbidden_imports
_FORBIDDEN_IMPORTS = (
    'yaml',
    'tiferet',
    'tiferet_ly',
    'compiler.domain',
    'compiler.events',
    'compiler.mappers',
    'compiler.utils',
    'compiler.contexts',
    'compiler.blueprints',
    'compiler.interfaces',
    '..domain',
    '..events',
    '..mappers',
    '..utils',
    '..contexts',
    '..blueprints',
    '..interfaces',
)

# ** constant: rows
_ROWS = (
    (
        'common.import_group',
        'specification',
        'compiler.utils.core',
        'ImportGroupSpecification',
        'artifact_header',
        {},
    ),
    (
        'common.section_class_name',
        'specification',
        'compiler.utils.core',
        'SectionClassNameSpecification',
        'artifact_header',
        {},
    ),
    (
        'common.function_section_name',
        'specification',
        'compiler.utils.core',
        'FunctionSectionNameSpecification',
        'artifact_header',
        {},
    ),
    (
        'common.attribute_member',
        'specification',
        'compiler.utils.core',
        'AttributeMemberSpecification',
        'member',
        {},
    ),
    (
        'common.method_member',
        'specification',
        'compiler.utils.core',
        'MethodMemberSpecification',
        'member',
        {},
    ),
    (
        'common.assignment_type',
        'specification',
        'compiler.utils.core',
        'AssignmentTypeSpecification',
        'expression',
        {},
    ),
    (
        'common.binary_op_expression',
        'specification',
        'compiler.utils.core',
        'BinaryOpTypeSpecification',
        'expression',
        {},
    ),
    (
        'common.binary_op_return',
        'specification',
        'compiler.utils.core',
        'ReturnBinaryOpTypeSpecification',
        'return',
        {},
    ),
    (
        'event.section',
        'specification',
        'compiler.utils.core',
        'EventSectionSpecification',
        'artifact_header',
        {},
    ),
    (
        'domain.permitted_group',
        'specification',
        'compiler.utils.core',
        'PermittedGroupSpecification',
        'artifact_header',
        {
            'permitted_groups': [
                'imports',
                'constants',
                'functions',
                'classes',
                'models',
                'exports',
            ],
            'error_code': 'DISALLOWED_DOMAIN_GROUP',
            'module_label': 'a domain module',
        },
    ),
    (
        'domain.app_import',
        'specification',
        'compiler.utils.core',
        'AppImportSpecification',
        'artifact_header',
        {
            'error_code': 'INVALID_DOMAIN_APP_IMPORT',
            'message': (
                "Domain 'app' import group may only import same-package "
                "sibling modules or the assets component type; found '{module_path}'."
            ),
            'allowed_components': [
                'assets',
            ],
        },
    ),
    (
        'domain.group_section_agreement',
        'specification',
        'compiler.utils.core',
        'GroupSectionAgreementSpecification',
        'artifact_header',
        {},
    ),
    (
        'domain.model_base_class',
        'specification',
        'compiler.utils.core',
        'RequiredBaseSpecification',
        'artifact_header',
        {
            'section_keyword': 'model',
            'error_code': 'MODEL_MISSING_DOMAIN_OBJECT_BASE',
            'message': (
                "Model '{header_name}' class '{class_name}' declares no base "
                "class; it must extend DomainObject"
            ),
            'name_key': 'model_name',
        },
    ),
    (
        'domain.attribute',
        'specification',
        'compiler.utils.core',
        'DomainAttributeSpecification',
        'member',
        {},
    ),
    (
        'di.permitted_group',
        'specification',
        'compiler.utils.core',
        'PermittedGroupSpecification',
        'artifact_header',
        {
            'permitted_groups': [
                'imports',
                'constants',
                'functions',
                'classes',
                'exports',
            ],
            'error_code': 'DISALLOWED_DI_GROUP',
            'module_label': 'a di module',
        },
    ),
    (
        'di.app_import',
        'specification',
        'compiler.utils.core',
        'AppImportSpecification',
        'artifact_header',
        {
            'error_code': 'INVALID_DI_APP_IMPORT',
            'message': (
                "DI 'app' import group may only import same-package sibling "
                "modules or the domain/interfaces component types; found '{module_path}'."
            ),
            'allowed_components': [
                'domain',
                'interfaces',
            ],
        },
    ),
    (
        'di.abstract_method',
        'specification',
        'compiler.utils.core',
        'DIAbstractMethodSpecification',
        'artifact_header',
        {},
    ),
    (
        'interface.permitted_group',
        'specification',
        'compiler.utils.core',
        'PermittedGroupSpecification',
        'artifact_header',
        {
            'permitted_groups': [
                'imports',
                'classes',
                'interfaces',
                'exports',
            ],
            'error_code': 'DISALLOWED_INTERFACE_GROUP',
            'module_label': 'an interfaces module',
        },
    ),
    (
        'interface.app_import',
        'specification',
        'compiler.utils.core',
        'AppImportSpecification',
        'artifact_header',
        {
            'error_code': 'INVALID_INTERFACE_APP_IMPORT',
            'message': (
                "Interface 'app' import group may only import same-package "
                "sibling modules or the mappers component type; found '{module_path}'."
            ),
            'allowed_components': [
                'mappers',
            ],
        },
    ),
    (
        'interface.abstract_method',
        'specification',
        'compiler.utils.core',
        'InterfaceAbstractMethodSpecification',
        'artifact_header',
        {},
    ),
    (
        'mapper.permitted_group',
        'specification',
        'compiler.utils.core',
        'PermittedGroupSpecification',
        'artifact_header',
        {
            'permitted_groups': [
                'imports',
                'constants',
                'mappers',
                'exports',
            ],
            'error_code': 'DISALLOWED_MAPPER_GROUP',
            'module_label': 'a mappers module',
        },
    ),
    (
        'mapper.app_import',
        'specification',
        'compiler.utils.core',
        'AppImportSpecification',
        'artifact_header',
        {
            'error_code': 'INVALID_MAPPER_APP_IMPORT',
            'message': (
                "Mapper 'app' import group may only import same-package "
                "sibling modules or the domain/events component types; found '{module_path}'."
            ),
            'allowed_components': [
                'domain',
                'events',
            ],
        },
    ),
    (
        'mapper.group_section_agreement',
        'specification',
        'compiler.utils.core',
        'GroupSectionAgreementSpecification',
        'artifact_header',
        {},
    ),
    (
        'mapper.roles_attribute',
        'specification',
        'compiler.utils.core',
        'MapperRolesAttributeSpecification',
        'member',
        {},
    ),
    (
        'utils.permitted_group',
        'specification',
        'compiler.utils.core',
        'PermittedGroupSpecification',
        'artifact_header',
        {
            'permitted_groups': [
                'imports',
                'constants',
                'utils',
                'exports',
            ],
            'error_code': 'DISALLOWED_UTILS_GROUP',
            'module_label': 'a utils module',
        },
    ),
    (
        'utils.app_import',
        'specification',
        'compiler.utils.core',
        'AppImportSpecification',
        'artifact_header',
        {
            'error_code': 'INVALID_UTILS_APP_IMPORT',
            'message': (
                "Utils 'app' import group may only import same-package sibling "
                "modules or the interfaces/mappers component types; found '{module_path}'."
            ),
            'allowed_components': [
                'interfaces',
                'mappers',
            ],
        },
    ),
    (
        'utils.context_manager_pairing',
        'specification',
        'compiler.utils.core',
        'ContextManagerPairingSpecification',
        'artifact_header',
        {},
    ),
    (
        'repos.permitted_group',
        'specification',
        'compiler.utils.core',
        'PermittedGroupSpecification',
        'artifact_header',
        {
            'permitted_groups': [
                'imports',
                'repos',
                'exports',
            ],
            'error_code': 'DISALLOWED_REPOS_GROUP',
            'module_label': 'a repos module',
        },
    ),
    (
        'repos.app_import',
        'specification',
        'compiler.utils.core',
        'AppImportSpecification',
        'artifact_header',
        {
            'error_code': 'INVALID_REPOS_APP_IMPORT',
            'message': (
                "Repos 'app' import group may only import same-package sibling "
                "modules or the interfaces/mappers/utils component types; found "
                "'{module_path}'."
            ),
            'allowed_components': [
                'interfaces',
                'mappers',
                'utils',
            ],
        },
    ),
    (
        'repos.base_class',
        'specification',
        'compiler.utils.core',
        'RequiredBaseSpecification',
        'artifact_header',
        {
            'section_keyword': 'repo',
            'error_code': 'REPO_MISSING_BASE',
            'message': (
                "Repo '{header_name}' class '{class_name}' must declare a base class"
            ),
            'name_key': 'repo_name',
        },
    ),
    (
        'repos.crud_method',
        'specification',
        'compiler.utils.core',
        'ReposCrudMethodSpecification',
        'artifact_header',
        {},
    ),
    (
        'asset.permitted_group',
        'specification',
        'compiler.utils.core',
        'PermittedGroupSpecification',
        'artifact_header',
        {
            'permitted_groups': [
                'imports',
                'constants',
                'functions',
                'classes',
                'exports',
            ],
            'error_code': 'DISALLOWED_ASSET_GROUP',
            'module_label': 'an assets module',
        },
    ),
    (
        'asset.import_sibling',
        'specification',
        'compiler.utils.core',
        'AppImportSpecification',
        'artifact_header',
        {
            'error_code': 'INVALID_ASSET_APP_IMPORT',
            'message': (
                "Assets 'app' import group may only import same-package sibling "
                "modules (e.g. 'from .core import ...'); found '{module_path}'."
            ),
            'allowed_components': [],
            'allow_siblings': True,
            'allow_framework_root_alias': False,
        },
    ),
    (
        'asset.group_section_agreement',
        'specification',
        'compiler.utils.core',
        'GroupSectionAgreementSpecification',
        'artifact_header',
        {},
    ),
    (
        'asset.constant_section_name',
        'specification',
        'compiler.utils.core',
        'ConstantSectionNameSpecification',
        'artifact_header',
        {},
    ),
    (
        'contexts.permitted_group',
        'specification',
        'compiler.utils.core',
        'PermittedGroupSpecification',
        'artifact_header',
        {
            'permitted_groups': [
                'imports',
                'contexts',
                'exports',
                'classes',
                'constants',
                'functions',
            ],
            'error_code': 'DISALLOWED_CONTEXTS_GROUP',
            'module_label': 'a contexts module',
        },
    ),
    (
        'contexts.app_import',
        'specification',
        'compiler.utils.core',
        'AppImportSpecification',
        'artifact_header',
        {
            'error_code': 'INVALID_CONTEXTS_APP_IMPORT',
            'message': (
                "Contexts 'app' import group may only import same-package sibling "
                "modules or the assets/domain/events component types; found '{module_path}'."
            ),
            'allowed_components': [
                'assets',
                'domain',
                'events',
            ],
            'allow_siblings': True,
            'allow_framework_root_alias': True,
        },
    ),
    (
        'contexts.base_class',
        'specification',
        'compiler.utils.core',
        'RequiredBaseSpecification',
        'artifact_header',
        {
            'section_keyword': 'context',
            'error_code': 'CONTEXT_MISSING_BASE_CONTEXT',
            'message': (
                "Context class '{class_name}' declares 'domain_type' and must "
                "extend 'BaseContext'"
            ),
            'required_base': 'BaseContext',
            'predicate': 'compiler.utils.core.declares_bound_domain_type',
        },
    ),
    (
        'blueprints.permitted_group',
        'specification',
        'compiler.utils.core',
        'PermittedGroupSpecification',
        'artifact_header',
        {
            'permitted_groups': [
                'imports',
                'constants',
                'functions',
                'blueprints',
                'exports',
            ],
            'error_code': 'DISALLOWED_BLUEPRINTS_GROUP',
            'module_label': 'a blueprints module',
        },
    ),
    (
        'blueprints.app_import',
        'specification',
        'compiler.utils.core',
        'AppImportSpecification',
        'artifact_header',
        {
            'error_code': 'INVALID_BLUEPRINTS_APP_IMPORT',
            'message': (
                "Blueprints 'app' import group may only import same-package sibling "
                "modules or the assets/contexts/di/events component types; found "
                "'{module_path}'."
            ),
            'allowed_components': [
                'assets',
                'contexts',
                'di',
                'events',
            ],
            'allow_siblings': True,
            'allow_framework_root_alias': True,
        },
    ),
    (
        'blueprints.group_section_agreement',
        'specification',
        'compiler.utils.core',
        'GroupSectionAgreementSpecification',
        'artifact_header',
        {},
    ),
    (
        'builder.import_from',
        'production',
        'compiler.utils.semantic',
        'ImportFromProduction',
        'import_from',
        {},
    ),
    (
        'builder.import',
        'production',
        'compiler.utils.semantic',
        'ImportProduction',
        'import',
        {},
    ),
    (
        'builder.class_decl',
        'production',
        'compiler.utils.semantic',
        'ClassDeclProduction',
        'class_decl',
        {},
    ),
    (
        'builder.func_decl',
        'production',
        'compiler.utils.semantic',
        'FuncDeclProduction',
        'func_decl',
        {},
    ),
    (
        'builder.attr_decl',
        'production',
        'compiler.utils.semantic',
        'AttrDeclProduction',
        'attr_decl',
        {},
    ),
    (
        'builder.self_attr_assign',
        'production',
        'compiler.utils.semantic',
        'SelfAttrAssignProduction',
        'expression',
        {},
    ),
    (
        'resolver.name',
        'production',
        'compiler.utils.semantic',
        'NameProduction',
        'name',
        {},
    ),
    (
        'resolver.self_attr',
        'production',
        'compiler.utils.semantic',
        'SelfAttrProduction',
        'self_attr',
        {},
    ),
)

# *** tests

# ** test: compiler_default_provisions_match_inventory
def test_compiler_default_provisions_match_inventory() -> None:
    '''
    Test that the catalog is the 49 employed rows, in list order.
    '''

    # Insertion order is the inventory order, not a sorted order.
    assert list(COMPILER_DEFAULT_PROVISIONS) == [row[0] for row in _ROWS]
    assert len(COMPILER_DEFAULT_PROVISIONS) == 49

    # Each value is the five registration fields. The id stays the key.
    for key, kind, module_path, class_name, applies_to, parameters in _ROWS:
        value = COMPILER_DEFAULT_PROVISIONS[key]
        assert list(value) == list(_VALUE_KEYS)
        assert 'id' not in value
        assert 'id' not in value['parameters']
        assert value['kind'] == kind
        assert value['kind'] in ('specification', 'production')
        assert value['kind'] != 'rewrite'
        assert value['module_path'] == module_path
        assert value['class_name'] == class_name
        assert value['applies_to'] == applies_to
        assert value['parameters'] == parameters
        assert list(value['parameters']) == list(parameters)

    # Written kwargs stay as written. Unwritten defaults stay absent.
    domain_import = COMPILER_DEFAULT_PROVISIONS['domain.app_import']['parameters']
    sibling_import = COMPILER_DEFAULT_PROVISIONS['asset.import_sibling']['parameters']
    assert 'allow_siblings' not in domain_import
    assert sibling_import['allow_siblings'] is True
    assert sibling_import['allow_framework_root_alias'] is False
    assert sibling_import['allowed_components'] == []

    # The contexts group list keeps the written order.
    context_groups = COMPILER_DEFAULT_PROVISIONS[
        'contexts.permitted_group'
    ]['parameters']['permitted_groups']
    assert context_groups == [
        'imports',
        'contexts',
        'exports',
        'classes',
        'constants',
        'functions',
    ]
    assert context_groups != sorted(context_groups)

# ** test: provision_rows_resolve_without_construction
def test_provision_rows_resolve_without_construction() -> None:
    '''
    Test that each row names a specification or production class.
    '''

    # Resolve the class. Do not construct it or call it.
    for key, kind, module_path, class_name, _applies_to, _parameters in _ROWS:
        resolved = getattr(import_module(module_path), class_name)
        assert resolved.__name__ == class_name
        assert COMPILER_DEFAULT_PROVISIONS[key]['class_name'] == class_name
        if kind == 'specification':
            assert issubclass(resolved, Specification)
        else:
            assert issubclass(resolved, Production)

# ** test: catalog_values_contain_no_callable
def test_catalog_values_contain_no_callable() -> None:
    '''
    Test that catalog values store data, not callables or classes.
    '''

    # The predicate is the dotted string. It is not the function.
    predicate = COMPILER_DEFAULT_PROVISIONS[
        'contexts.base_class'
    ]['parameters']['predicate']
    assert predicate == 'compiler.utils.core.declares_bound_domain_type'
    assert callable(predicate) is False

    # Walk every nested value. Strings, lists, and dicts are data.
    pending = list(COMPILER_DEFAULT_PROVISIONS.values())
    while pending:
        value = pending.pop()
        assert callable(value) is False
        assert isinstance(value, type) is False
        if isinstance(value, dict):
            pending.extend(value.values())
        elif isinstance(value, list):
            pending.extend(value)

# ** test: create_default_provision_data_omits_id
def test_create_default_provision_data_omits_id() -> None:
    '''
    Test that the core factory omits id and returns a fresh dict.
    '''

    # The id is the group-dict key, not a factory parameter.
    assert 'id' not in inspect.signature(create_default_provision_data).parameters

    # None and an empty dict both become a new parameters dict.
    omitted = create_default_provision_data(
        kind='specification',
        applies_to='artifact_header',
        module_path='compiler.utils.core',
        class_name='ImportGroupSpecification',
        parameters=None,
    )
    empty = create_default_provision_data(
        kind='specification',
        applies_to='artifact_header',
        module_path='compiler.utils.core',
        class_name='ImportGroupSpecification',
        parameters={},
    )
    assert list(omitted) == list(_VALUE_KEYS)
    assert 'id' not in omitted
    assert omitted['parameters'] == {}
    assert empty['parameters'] == {}
    assert isinstance(omitted['parameters'], dict)

    # Two calls do not share the returned dict.
    assert omitted is not empty
    assert omitted['parameters'] is not empty['parameters']

# ** test: provision_source_stays_dependency_light
def test_provision_source_stays_dependency_light() -> None:
    '''
    Test that the catalog module does not name excluded sources or imports.
    '''

    # Read the catalog and the core factory module.
    source = _PROVISION_PATH.read_text(encoding='utf-8')
    core_source = _CORE_PATH.read_text(encoding='utf-8')
    tree = ast.parse(source)
    core_tree = ast.parse(core_source)

    # The catalog is constants after imports. The factory module is functions after imports.
    assert source.index('# *** imports') < source.index('# *** constants')
    assert '# *** functions' not in source
    assert core_source.index('# *** imports') < core_source.index('# *** functions')
    assert '# *** constants' not in core_source

    # The catalog names the group dict. The factory is defined in core, not here.
    assigned = {
        target.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    core_functions = {
        node.name for node in ast.walk(core_tree) if isinstance(node, ast.FunctionDef)
    }
    assert assigned == {'COMPILER_DEFAULT_PROVISIONS'}
    assert not any(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))
    assert core_functions == {'create_default_provision_data'}
    assert not any(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
    assert not any(isinstance(node, ast.ClassDef) for node in ast.walk(core_tree))
    assert not any(
        name.endswith('_RULE_SET') or name.endswith('_PRODUCTION_SET')
        for name in assigned
    )

    # Excluded constructions are not named, even as comments.
    for scanned in (source, core_source):
        for name in _FORBIDDEN_NAMES:
            assert re.search(
                r'(?<![A-Za-z0-9_.])' + re.escape(name) + r'(?![A-Za-z0-9_])',
                scanned,
            ) is None

    # Import lines do not name the packages these modules must not load.
    import_lines = [
        line.strip()
        for line in source.splitlines()
        if line.strip().startswith(('import ', 'from '))
    ]
    core_import_lines = [
        line.strip()
        for line in core_source.splitlines()
        if line.strip().startswith(('import ', 'from '))
    ]
    assert import_lines == ['from .core import create_default_provision_data']
    assert core_import_lines == ['from typing import Any, Dict']
    for line in import_lines + core_import_lines:
        for forbidden in _FORBIDDEN_IMPORTS:
            assert forbidden not in line

    # Neither module source opens a file.
    assert 'open(' not in source
    assert 'open(' not in core_source

# ** test: assets_package_does_not_bind_provisions
def test_assets_package_does_not_bind_provisions() -> None:
    '''
    Test that the provision module is exported and the catalog stays on it.
    '''

    # The package import resolves the module. The dict stays on the module.
    import compiler.assets as assets
    from compiler.assets import core, provision

    assert provision.COMPILER_DEFAULT_PROVISIONS is COMPILER_DEFAULT_PROVISIONS
    assert core.create_default_provision_data is create_default_provision_data
    assert not hasattr(assets, 'COMPILER_DEFAULT_PROVISIONS')
