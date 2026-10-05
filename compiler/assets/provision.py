"""Compiler Default Provision Catalog"""

# *** imports

# ** core
from typing import Any, Dict

# *** constants

# ** constant: compiler_default_provisions
COMPILER_DEFAULT_PROVISIONS = {
}

# *** functions

# ** function: create_default_provision_data
def create_default_provision_data(
        kind: str,
        applies_to: str,
        module_path: str,
        class_name: str,
        parameters: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
    '''
    Build one provision registration value.

    The id is omitted because the group-dict key is the id. Legal kinds are
    ``specification``, ``production``, and ``rewrite``. ``parameters`` holds
    constructor keyword arguments other than ``id`` and ``applies_to``.

    :param kind: The provision kind.
    :type kind: str
    :param applies_to: The visit hook this provision handles.
    :type applies_to: str
    :param module_path: The module that defines the class.
    :type module_path: str
    :param class_name: The class to resolve later.
    :type class_name: str
    :param parameters: Constructor keyword arguments other than id and applies_to.
    :type parameters: Dict[str, Any]
    :return: The five registration fields.
    :rtype: Dict[str, Any]
    '''

    # Copy parameters and return the five registration fields.
    return {
        'kind': kind,
        'applies_to': applies_to,
        'module_path': module_path,
        'class_name': class_name,
        'parameters': dict(parameters) if parameters else {},
    }

# ** function: _load_compiler_default_provisions
def _load_compiler_default_provisions() -> None:
    '''
    Apply the catalog rows after the factory is defined.

    The catalog constant is declared before this factory. These calls run
    here so the factory name resolves without moving either artifact.

    :return: None
    :rtype: None
    '''

    # Apply each row. The id stays the dict key.
    COMPILER_DEFAULT_PROVISIONS.update({
        'common.import_group': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='ImportGroupSpecification',
            parameters={},
        ),
        'common.section_class_name': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='SectionClassNameSpecification',
            parameters={},
        ),
        'common.function_section_name': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='FunctionSectionNameSpecification',
            parameters={},
        ),
        'common.attribute_member': create_default_provision_data(
            kind='specification',
            applies_to='member',
            module_path='compiler.utils.core',
            class_name='AttributeMemberSpecification',
            parameters={},
        ),
        'common.method_member': create_default_provision_data(
            kind='specification',
            applies_to='member',
            module_path='compiler.utils.core',
            class_name='MethodMemberSpecification',
            parameters={},
        ),
        'common.assignment_type': create_default_provision_data(
            kind='specification',
            applies_to='expression',
            module_path='compiler.utils.core',
            class_name='AssignmentTypeSpecification',
            parameters={},
        ),
        'common.binary_op_expression': create_default_provision_data(
            kind='specification',
            applies_to='expression',
            module_path='compiler.utils.core',
            class_name='BinaryOpTypeSpecification',
            parameters={},
        ),
        'common.binary_op_return': create_default_provision_data(
            kind='specification',
            applies_to='return',
            module_path='compiler.utils.core',
            class_name='ReturnBinaryOpTypeSpecification',
            parameters={},
        ),
        'event.section': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='EventSectionSpecification',
            parameters={},
        ),
        'domain.permitted_group': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='PermittedGroupSpecification',
            parameters={
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
        'domain.app_import': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='AppImportSpecification',
            parameters={
                'error_code': 'INVALID_DOMAIN_APP_IMPORT',
                'message': (
                    "Domain 'app' import group may only import same-package sibling "
                    "modules or the assets component type; found '{module_path}'."
                ),
                'allowed_components': [
                    'assets',
                ],
            },
        ),
        'domain.group_section_agreement': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='GroupSectionAgreementSpecification',
            parameters={},
        ),
        'domain.model_base_class': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='RequiredBaseSpecification',
            parameters={
                'section_keyword': 'model',
                'error_code': 'MODEL_MISSING_DOMAIN_OBJECT_BASE',
                'message': (
                    "Model '{header_name}' class '{class_name}' declares no base class; "
                    "it must extend DomainObject"
                ),
                'name_key': 'model_name',
            },
        ),
        'domain.attribute': create_default_provision_data(
            kind='specification',
            applies_to='member',
            module_path='compiler.utils.core',
            class_name='DomainAttributeSpecification',
            parameters={},
        ),
        'di.permitted_group': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='PermittedGroupSpecification',
            parameters={
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
        'di.app_import': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='AppImportSpecification',
            parameters={
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
        'di.abstract_method': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='DIAbstractMethodSpecification',
            parameters={},
        ),
        'interface.permitted_group': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='PermittedGroupSpecification',
            parameters={
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
        'interface.app_import': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='AppImportSpecification',
            parameters={
                'error_code': 'INVALID_INTERFACE_APP_IMPORT',
                'message': (
                    "Interface 'app' import group may only import same-package sibling "
                    "modules or the mappers component type; found '{module_path}'."
                ),
                'allowed_components': [
                    'mappers',
                ],
            },
        ),
        'interface.abstract_method': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='InterfaceAbstractMethodSpecification',
            parameters={},
        ),
        'mapper.permitted_group': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='PermittedGroupSpecification',
            parameters={
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
        'mapper.app_import': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='AppImportSpecification',
            parameters={
                'error_code': 'INVALID_MAPPER_APP_IMPORT',
                'message': (
                    "Mapper 'app' import group may only import same-package sibling "
                    "modules or the domain/events component types; found '{module_path}'."
                ),
                'allowed_components': [
                    'domain',
                    'events',
                ],
            },
        ),
        'mapper.group_section_agreement': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='GroupSectionAgreementSpecification',
            parameters={},
        ),
        'mapper.roles_attribute': create_default_provision_data(
            kind='specification',
            applies_to='member',
            module_path='compiler.utils.core',
            class_name='MapperRolesAttributeSpecification',
            parameters={},
        ),
        'utils.permitted_group': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='PermittedGroupSpecification',
            parameters={
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
        'utils.app_import': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='AppImportSpecification',
            parameters={
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
        'utils.context_manager_pairing': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='ContextManagerPairingSpecification',
            parameters={},
        ),
        'repos.permitted_group': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='PermittedGroupSpecification',
            parameters={
                'permitted_groups': [
                    'imports',
                    'repos',
                    'exports',
                ],
                'error_code': 'DISALLOWED_REPOS_GROUP',
                'module_label': 'a repos module',
            },
        ),
        'repos.app_import': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='AppImportSpecification',
            parameters={
                'error_code': 'INVALID_REPOS_APP_IMPORT',
                'message': (
                    "Repos 'app' import group may only import same-package sibling "
                    "modules or the interfaces/mappers/utils component types; found '{module_path}'."
                ),
                'allowed_components': [
                    'interfaces',
                    'mappers',
                    'utils',
                ],
            },
        ),
        'repos.base_class': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='RequiredBaseSpecification',
            parameters={
                'section_keyword': 'repo',
                'error_code': 'REPO_MISSING_BASE',
                'message': (
                    "Repo '{header_name}' class '{class_name}' must declare a base class"
                ),
                'name_key': 'repo_name',
            },
        ),
        'repos.crud_method': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='ReposCrudMethodSpecification',
            parameters={},
        ),
        'asset.permitted_group': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='PermittedGroupSpecification',
            parameters={
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
        'asset.import_sibling': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='AppImportSpecification',
            parameters={
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
        'asset.group_section_agreement': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='GroupSectionAgreementSpecification',
            parameters={},
        ),
        'asset.constant_section_name': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='ConstantSectionNameSpecification',
            parameters={},
        ),
        'contexts.permitted_group': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='PermittedGroupSpecification',
            parameters={
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
        'contexts.app_import': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='AppImportSpecification',
            parameters={
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
        'contexts.base_class': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='RequiredBaseSpecification',
            parameters={
                'section_keyword': 'context',
                'error_code': 'CONTEXT_MISSING_BASE_CONTEXT',
                'message': (
                    "Context class '{class_name}' declares 'domain_type' and must extend 'BaseContext'"
                ),
                'required_base': 'BaseContext',
                'predicate': 'compiler.utils.core.declares_bound_domain_type',
            },
        ),
        'blueprints.permitted_group': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='PermittedGroupSpecification',
            parameters={
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
        'blueprints.app_import': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='AppImportSpecification',
            parameters={
                'error_code': 'INVALID_BLUEPRINTS_APP_IMPORT',
                'message': (
                    "Blueprints 'app' import group may only import same-package sibling "
                    "modules or the assets/contexts/di/events component types; found '{module_path}'."
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
        'blueprints.group_section_agreement': create_default_provision_data(
            kind='specification',
            applies_to='artifact_header',
            module_path='compiler.utils.core',
            class_name='GroupSectionAgreementSpecification',
            parameters={},
        ),
        'builder.import_from': create_default_provision_data(
            kind='production',
            applies_to='import_from',
            module_path='compiler.utils.semantic',
            class_name='ImportFromProduction',
            parameters={},
        ),
        'builder.import': create_default_provision_data(
            kind='production',
            applies_to='import',
            module_path='compiler.utils.semantic',
            class_name='ImportProduction',
            parameters={},
        ),
        'builder.class_decl': create_default_provision_data(
            kind='production',
            applies_to='class_decl',
            module_path='compiler.utils.semantic',
            class_name='ClassDeclProduction',
            parameters={},
        ),
        'builder.func_decl': create_default_provision_data(
            kind='production',
            applies_to='func_decl',
            module_path='compiler.utils.semantic',
            class_name='FuncDeclProduction',
            parameters={},
        ),
        'builder.attr_decl': create_default_provision_data(
            kind='production',
            applies_to='attr_decl',
            module_path='compiler.utils.semantic',
            class_name='AttrDeclProduction',
            parameters={},
        ),
        'builder.self_attr_assign': create_default_provision_data(
            kind='production',
            applies_to='expression',
            module_path='compiler.utils.semantic',
            class_name='SelfAttrAssignProduction',
            parameters={},
        ),
        'resolver.name': create_default_provision_data(
            kind='production',
            applies_to='name',
            module_path='compiler.utils.semantic',
            class_name='NameProduction',
            parameters={},
        ),
        'resolver.self_attr': create_default_provision_data(
            kind='production',
            applies_to='self_attr',
            module_path='compiler.utils.semantic',
            class_name='SelfAttrProduction',
            parameters={},
        ),
    })

# Resolve the catalog once the factory exists.
_load_compiler_default_provisions()
