"""Compiler Default Feature Catalog"""

# *** imports

# ** infra
from tiferet.assets.core import create_default_feature_data

# *** constants (ids)

# ** constant: scan_module_id
SCAN_MODULE_ID = 'scan.module'

# ** constant: parse_module_id
PARSE_MODULE_ID = 'parse.module'

# ** constant: semantic_module_id
SEMANTIC_MODULE_ID = 'semantic.module'

# ** constant: compile_module_id
COMPILE_MODULE_ID = 'compile.module'

# ** constant: compile_ast_id
COMPILE_AST_ID = 'compile.ast'

# *** constants (models)

# ** constant: scan_module_data
SCAN_MODULE_DATA = create_default_feature_data(
    name='Scan Module',
    group_id='scan',
    feature_key='module',
    steps=[
        {
            'name': 'Tokenize',
            'service_id': 'perform_lexical_analysis_event',
            'data_key': 'tokens',
        },
        {
            'name': 'Emit Scan Result',
            'service_id': 'emit_scan_result_event',
        },
    ],
    description='Tokenize a source file. This phase does not take a component type.',
)

# ** constant: parse_module_data
PARSE_MODULE_DATA = create_default_feature_data(
    name='Parse Module',
    group_id='parse',
    feature_key='module',
    steps=[
        {
            'name': 'Tokenize',
            'service_id': 'perform_lexical_analysis_event',
            'data_key': 'tokens',
        },
        {
            'name': 'Parse',
            'service_id': 'perform_syntactic_analysis_event',
            'data_key': 'ast',
        },
        {
            'name': 'Emit Parse Result',
            'service_id': 'emit_parse_result_event',
        },
    ],
    description='Parse a source file. This phase does not take a component type.',
)

# ** constant: semantic_module_data
SEMANTIC_MODULE_DATA = create_default_feature_data(
    name='Semantic Module',
    group_id='semantic',
    feature_key='module',
    steps=[
        {
            'name': 'Tokenize',
            'service_id': 'perform_lexical_analysis_event',
            'data_key': 'tokens',
        },
        {
            'name': 'Parse',
            'service_id': 'perform_syntactic_analysis_event',
            'data_key': 'ast',
        },
        {
            'name': 'Build Symbols',
            'service_id': 'perform_semantic_analysis_event',
            'data_key': 'semantic',
        },
        {
            'name': 'Check Common Conformance',
            'service_id': 'check_common_conformance_event',
            'data_key': 'findings',
        },
        {
            'name': 'Check Event Conformance',
            'service_id': 'check_event_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'events'",
        },
        {
            'name': 'Check Asset Conformance',
            'service_id': 'check_asset_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'assets'",
        },
        {
            'name': 'Check Domain Conformance',
            'service_id': 'check_domain_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'domain'",
        },
        {
            'name': 'Check Mapper Conformance',
            'service_id': 'check_mapper_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'mappers'",
        },
        {
            'name': 'Check Interface Conformance',
            'service_id': 'check_interface_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'interfaces'",
        },
        {
            'name': 'Check DI Conformance',
            'service_id': 'check_di_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'di'",
        },
        {
            'name': 'Check Utils Conformance',
            'service_id': 'check_utils_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'utils'",
        },
        {
            'name': 'Check Context Conformance',
            'service_id': 'check_context_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'contexts'",
        },
        {
            'name': 'Check Blueprints Conformance',
            'service_id': 'check_blueprints_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'blueprints'",
        },
        {
            'name': 'Check Repos Conformance',
            'service_id': 'check_repos_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'repos'",
        },
        {
            'name': 'Emit Semantic Result',
            'service_id': 'emit_semantic_result_event',
        },
    ],
    description='Analyze a source file. Dialect checks are gated on the requested component type.',
)

# ** constant: compile_module_data
COMPILE_MODULE_DATA = create_default_feature_data(
    name='Compile Module',
    group_id='compile',
    feature_key='module',
    steps=[
        {
            'name': 'Tokenize',
            'service_id': 'perform_lexical_analysis_event',
            'data_key': 'tokens',
        },
        {
            'name': 'Parse',
            'service_id': 'perform_syntactic_analysis_event',
            'data_key': 'ast',
        },
        {
            'name': 'Build Symbols',
            'service_id': 'perform_semantic_analysis_event',
            'data_key': 'semantic',
        },
        {
            'name': 'Check Common Conformance',
            'service_id': 'check_common_conformance_event',
            'data_key': 'findings',
        },
        {
            'name': 'Check Event Conformance',
            'service_id': 'check_event_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'events'",
        },
        {
            'name': 'Check Asset Conformance',
            'service_id': 'check_asset_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'assets'",
        },
        {
            'name': 'Check Domain Conformance',
            'service_id': 'check_domain_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'domain'",
        },
        {
            'name': 'Check Mapper Conformance',
            'service_id': 'check_mapper_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'mappers'",
        },
        {
            'name': 'Check Interface Conformance',
            'service_id': 'check_interface_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'interfaces'",
        },
        {
            'name': 'Check DI Conformance',
            'service_id': 'check_di_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'di'",
        },
        {
            'name': 'Check Utils Conformance',
            'service_id': 'check_utils_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'utils'",
        },
        {
            'name': 'Check Context Conformance',
            'service_id': 'check_context_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'contexts'",
        },
        {
            'name': 'Check Blueprints Conformance',
            'service_id': 'check_blueprints_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'blueprints'",
        },
        {
            'name': 'Check Repos Conformance',
            'service_id': 'check_repos_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'repos'",
        },
        {
            'name': 'Generate Code',
            'service_id': 'generate_code_event',
            'data_key': 'codegen',
            'parameters': {
                'codegen_service': 'codegen_service',
            },
        },
        {
            'name': 'Optimize Code',
            'service_id': 'optimize_code_event',
            'data_key': 'codegen',
            'parameters': {
                'optimizer_service': 'optimizer_service',
            },
        },
        {
            'name': 'Emit Codegen Result',
            'service_id': 'emit_codegen_result_event',
        },
    ],
    description='Compile a source file. Dialect checks are gated on the requested component type.',
)

# ** constant: compile_ast_data
COMPILE_AST_DATA = create_default_feature_data(
    name='Compile AST',
    group_id='compile',
    feature_key='ast',
    steps=[
        {
            'name': 'Load From AST',
            'service_id': 'load_from_ast_event',
            'data_key': 'ast',
        },
        {
            'name': 'Build Symbols',
            'service_id': 'perform_semantic_analysis_event',
            'data_key': 'semantic',
        },
        {
            'name': 'Check Common Conformance',
            'service_id': 'check_common_conformance_event',
            'data_key': 'findings',
        },
        {
            'name': 'Check Event Conformance',
            'service_id': 'check_event_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'events'",
        },
        {
            'name': 'Check Asset Conformance',
            'service_id': 'check_asset_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'assets'",
        },
        {
            'name': 'Check Domain Conformance',
            'service_id': 'check_domain_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'domain'",
        },
        {
            'name': 'Check Mapper Conformance',
            'service_id': 'check_mapper_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'mappers'",
        },
        {
            'name': 'Check Interface Conformance',
            'service_id': 'check_interface_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'interfaces'",
        },
        {
            'name': 'Check DI Conformance',
            'service_id': 'check_di_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'di'",
        },
        {
            'name': 'Check Utils Conformance',
            'service_id': 'check_utils_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'utils'",
        },
        {
            'name': 'Check Context Conformance',
            'service_id': 'check_context_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'contexts'",
        },
        {
            'name': 'Check Blueprints Conformance',
            'service_id': 'check_blueprints_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'blueprints'",
        },
        {
            'name': 'Check Repos Conformance',
            'service_id': 'check_repos_conformance_event',
            'data_key': 'findings',
            'condition': "$r.component == 'repos'",
        },
        {
            'name': 'Generate Code',
            'service_id': 'generate_code_event',
            'data_key': 'codegen',
            'parameters': {
                'codegen_service': 'codegen_service',
            },
        },
        {
            'name': 'Optimize Code',
            'service_id': 'optimize_code_event',
            'data_key': 'codegen',
            'parameters': {
                'optimizer_service': 'optimizer_service',
            },
        },
        {
            'name': 'Emit Codegen Result',
            'service_id': 'emit_codegen_result_event',
        },
    ],
    description='Compile a saved AST. Dialect checks are gated on the requested component type.',
)

# *** constants (groups)

# ** constant: compiler_default_features
COMPILER_DEFAULT_FEATURES = {
    SCAN_MODULE_ID: SCAN_MODULE_DATA,
    PARSE_MODULE_ID: PARSE_MODULE_DATA,
    SEMANTIC_MODULE_ID: SEMANTIC_MODULE_DATA,
    COMPILE_MODULE_ID: COMPILE_MODULE_DATA,
    COMPILE_AST_ID: COMPILE_AST_DATA,
}
