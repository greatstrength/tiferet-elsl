"""Compiler Default Application Catalog"""

# *** imports

# ** infra
from tiferet.assets.core import (
    create_app_service_dependency_data,
    create_default_app_session_data,
)

# *** constants (ids)

# ** constant: token_service_id
TOKEN_SERVICE_ID = 'token_service'

# ** constant: grammar_service_id
GRAMMAR_SERVICE_ID = 'grammar_service'

# ** constant: production_service_id
PRODUCTION_SERVICE_ID = 'production_service'

# ** constant: lexer_service_id
LEXER_SERVICE_ID = 'lexer_service'

# ** constant: parser_service_id
PARSER_SERVICE_ID = 'parser_service'

# ** constant: codegen_service_id
CODEGEN_SERVICE_ID = 'codegen_service'

# ** constant: optimizer_service_id
OPTIMIZER_SERVICE_ID = 'optimizer_service'

# ** constant: perform_lexical_analysis_event_id
PERFORM_LEXICAL_ANALYSIS_EVENT_ID = 'perform_lexical_analysis_event'

# ** constant: emit_scan_result_event_id
EMIT_SCAN_RESULT_EVENT_ID = 'emit_scan_result_event'

# ** constant: perform_syntactic_analysis_event_id
PERFORM_SYNTACTIC_ANALYSIS_EVENT_ID = 'perform_syntactic_analysis_event'

# ** constant: emit_parse_result_event_id
EMIT_PARSE_RESULT_EVENT_ID = 'emit_parse_result_event'

# ** constant: perform_semantic_analysis_event_id
PERFORM_SEMANTIC_ANALYSIS_EVENT_ID = 'perform_semantic_analysis_event'

# ** constant: check_common_conformance_event_id
CHECK_COMMON_CONFORMANCE_EVENT_ID = 'check_common_conformance_event'

# ** constant: check_event_conformance_event_id
CHECK_EVENT_CONFORMANCE_EVENT_ID = 'check_event_conformance_event'

# ** constant: check_asset_conformance_event_id
CHECK_ASSET_CONFORMANCE_EVENT_ID = 'check_asset_conformance_event'

# ** constant: check_domain_conformance_event_id
CHECK_DOMAIN_CONFORMANCE_EVENT_ID = 'check_domain_conformance_event'

# ** constant: check_mapper_conformance_event_id
CHECK_MAPPER_CONFORMANCE_EVENT_ID = 'check_mapper_conformance_event'

# ** constant: check_interface_conformance_event_id
CHECK_INTERFACE_CONFORMANCE_EVENT_ID = 'check_interface_conformance_event'

# ** constant: check_di_conformance_event_id
CHECK_DI_CONFORMANCE_EVENT_ID = 'check_di_conformance_event'

# ** constant: check_utils_conformance_event_id
CHECK_UTILS_CONFORMANCE_EVENT_ID = 'check_utils_conformance_event'

# ** constant: check_context_conformance_event_id
CHECK_CONTEXT_CONFORMANCE_EVENT_ID = 'check_context_conformance_event'

# ** constant: check_blueprints_conformance_event_id
CHECK_BLUEPRINTS_CONFORMANCE_EVENT_ID = 'check_blueprints_conformance_event'

# ** constant: check_repos_conformance_event_id
CHECK_REPOS_CONFORMANCE_EVENT_ID = 'check_repos_conformance_event'

# ** constant: emit_semantic_result_event_id
EMIT_SEMANTIC_RESULT_EVENT_ID = 'emit_semantic_result_event'

# ** constant: generate_code_event_id
GENERATE_CODE_EVENT_ID = 'generate_code_event'

# ** constant: optimize_code_event_id
OPTIMIZE_CODE_EVENT_ID = 'optimize_code_event'

# ** constant: emit_codegen_result_event_id
EMIT_CODEGEN_RESULT_EVENT_ID = 'emit_codegen_result_event'

# ** constant: load_from_ast_event_id
LOAD_FROM_AST_EVENT_ID = 'load_from_ast_event'

# ** constant: compiler_session_id
COMPILER_SESSION_ID = 'compiler'

# ** constant: compiler_cli_session_id
COMPILER_CLI_SESSION_ID = 'compiler_cli'

# *** constants (models)

# ** constant: token_service_data
TOKEN_SERVICE_DATA = create_app_service_dependency_data(
    'tiferet_ly.repos.token',
    'TokenConfigRepository',
)

# ** constant: grammar_service_data
GRAMMAR_SERVICE_DATA = create_app_service_dependency_data(
    'tiferet_ly.repos.grammar',
    'GrammarConfigRepository',
)

# ** constant: production_service_data
PRODUCTION_SERVICE_DATA = create_app_service_dependency_data(
    'tiferet_ly.repos.production',
    'ProductionConfigRepository',
)

# ** constant: lexer_service_data
LEXER_SERVICE_DATA = create_app_service_dependency_data(
    'compiler.utils.lexer',
    'TiferetLexer',
)

# ** constant: parser_service_data
PARSER_SERVICE_DATA = create_app_service_dependency_data(
    'compiler.utils.parser',
    'TiferetParser',
)

# ** constant: codegen_service_data
CODEGEN_SERVICE_DATA = create_app_service_dependency_data(
    'compiler.utils.codegen',
    'TiferetGenerator',
)

# ** constant: optimizer_service_data
OPTIMIZER_SERVICE_DATA = create_app_service_dependency_data(
    'compiler.utils.optimizer',
    'YamlAnchorOptimizer',
)

# ** constant: perform_lexical_analysis_event_data
PERFORM_LEXICAL_ANALYSIS_EVENT_DATA = create_app_service_dependency_data(
    'compiler.events.lexer',
    'PerformLexicalAnalysis',
)

# ** constant: emit_scan_result_event_data
EMIT_SCAN_RESULT_EVENT_DATA = create_app_service_dependency_data(
    'compiler.events.lexer',
    'EmitScanResult',
)

# ** constant: perform_syntactic_analysis_event_data
PERFORM_SYNTACTIC_ANALYSIS_EVENT_DATA = create_app_service_dependency_data(
    'compiler.events.parser',
    'PerformSyntacticAnalysis',
)

# ** constant: emit_parse_result_event_data
EMIT_PARSE_RESULT_EVENT_DATA = create_app_service_dependency_data(
    'compiler.events.parser',
    'EmitParseResult',
)

# ** constant: perform_semantic_analysis_event_data
PERFORM_SEMANTIC_ANALYSIS_EVENT_DATA = create_app_service_dependency_data(
    'compiler.events.semantic',
    'PerformSemanticAnalysis',
)

# ** constant: check_common_conformance_event_data
CHECK_COMMON_CONFORMANCE_EVENT_DATA = create_app_service_dependency_data(
    'compiler.events.typecheck',
    'CheckCommonConformance',
)

# ** constant: check_event_conformance_event_data
CHECK_EVENT_CONFORMANCE_EVENT_DATA = create_app_service_dependency_data(
    'compiler.events.typecheck',
    'CheckEventConformance',
)

# ** constant: check_asset_conformance_event_data
CHECK_ASSET_CONFORMANCE_EVENT_DATA = create_app_service_dependency_data(
    'compiler.events.typecheck',
    'CheckAssetConformance',
)

# ** constant: check_domain_conformance_event_data
CHECK_DOMAIN_CONFORMANCE_EVENT_DATA = create_app_service_dependency_data(
    'compiler.events.typecheck',
    'CheckDomainConformance',
)

# ** constant: check_mapper_conformance_event_data
CHECK_MAPPER_CONFORMANCE_EVENT_DATA = create_app_service_dependency_data(
    'compiler.events.typecheck',
    'CheckMapperConformance',
)

# ** constant: check_interface_conformance_event_data
CHECK_INTERFACE_CONFORMANCE_EVENT_DATA = create_app_service_dependency_data(
    'compiler.events.typecheck',
    'CheckInterfaceConformance',
)

# ** constant: check_di_conformance_event_data
CHECK_DI_CONFORMANCE_EVENT_DATA = create_app_service_dependency_data(
    'compiler.events.typecheck',
    'CheckDIConformance',
)

# ** constant: check_utils_conformance_event_data
CHECK_UTILS_CONFORMANCE_EVENT_DATA = create_app_service_dependency_data(
    'compiler.events.typecheck',
    'CheckUtilsConformance',
)

# ** constant: check_context_conformance_event_data
CHECK_CONTEXT_CONFORMANCE_EVENT_DATA = create_app_service_dependency_data(
    'compiler.events.typecheck',
    'CheckContextsConformance',
)

# ** constant: check_blueprints_conformance_event_data
CHECK_BLUEPRINTS_CONFORMANCE_EVENT_DATA = create_app_service_dependency_data(
    'compiler.events.typecheck',
    'CheckBlueprintsConformance',
)

# ** constant: check_repos_conformance_event_data
CHECK_REPOS_CONFORMANCE_EVENT_DATA = create_app_service_dependency_data(
    'compiler.events.typecheck',
    'CheckReposConformance',
)

# ** constant: emit_semantic_result_event_data
EMIT_SEMANTIC_RESULT_EVENT_DATA = create_app_service_dependency_data(
    'compiler.events.semantic',
    'EmitSemanticResult',
)

# ** constant: generate_code_event_data
GENERATE_CODE_EVENT_DATA = create_app_service_dependency_data(
    'compiler.events.codegen',
    'GenerateCode',
)

# ** constant: optimize_code_event_data
OPTIMIZE_CODE_EVENT_DATA = create_app_service_dependency_data(
    'compiler.events.codegen',
    'OptimizeCode',
)

# ** constant: emit_codegen_result_event_data
EMIT_CODEGEN_RESULT_EVENT_DATA = create_app_service_dependency_data(
    'compiler.events.codegen',
    'EmitCodegenResult',
)

# ** constant: load_from_ast_event_data
LOAD_FROM_AST_EVENT_DATA = create_app_service_dependency_data(
    'compiler.events.codegen',
    'LoadFromAST',
)

# ** constant: compiler_session_data
COMPILER_SESSION_DATA = create_default_app_session_data(
    'Tiferet Dialect Compiler',
    description='Component-agnostic compiler session. The component type arrives as request data.',
)

# ** constant: compiler_cli_session_data
COMPILER_CLI_SESSION_DATA = create_default_app_session_data(
    'Compiler CLI',
    description='Component-agnostic compiler CLI. The component type arrives as request data.',
)

# *** constants (groups)

# ** constant: compiler_default_services
COMPILER_DEFAULT_SERVICES = {
    TOKEN_SERVICE_ID: TOKEN_SERVICE_DATA,
    GRAMMAR_SERVICE_ID: GRAMMAR_SERVICE_DATA,
    PRODUCTION_SERVICE_ID: PRODUCTION_SERVICE_DATA,
    LEXER_SERVICE_ID: LEXER_SERVICE_DATA,
    PARSER_SERVICE_ID: PARSER_SERVICE_DATA,
    CODEGEN_SERVICE_ID: CODEGEN_SERVICE_DATA,
    OPTIMIZER_SERVICE_ID: OPTIMIZER_SERVICE_DATA,
    PERFORM_LEXICAL_ANALYSIS_EVENT_ID: PERFORM_LEXICAL_ANALYSIS_EVENT_DATA,
    EMIT_SCAN_RESULT_EVENT_ID: EMIT_SCAN_RESULT_EVENT_DATA,
    PERFORM_SYNTACTIC_ANALYSIS_EVENT_ID: PERFORM_SYNTACTIC_ANALYSIS_EVENT_DATA,
    EMIT_PARSE_RESULT_EVENT_ID: EMIT_PARSE_RESULT_EVENT_DATA,
    PERFORM_SEMANTIC_ANALYSIS_EVENT_ID: PERFORM_SEMANTIC_ANALYSIS_EVENT_DATA,
    CHECK_COMMON_CONFORMANCE_EVENT_ID: CHECK_COMMON_CONFORMANCE_EVENT_DATA,
    CHECK_EVENT_CONFORMANCE_EVENT_ID: CHECK_EVENT_CONFORMANCE_EVENT_DATA,
    CHECK_ASSET_CONFORMANCE_EVENT_ID: CHECK_ASSET_CONFORMANCE_EVENT_DATA,
    CHECK_DOMAIN_CONFORMANCE_EVENT_ID: CHECK_DOMAIN_CONFORMANCE_EVENT_DATA,
    CHECK_MAPPER_CONFORMANCE_EVENT_ID: CHECK_MAPPER_CONFORMANCE_EVENT_DATA,
    CHECK_INTERFACE_CONFORMANCE_EVENT_ID: CHECK_INTERFACE_CONFORMANCE_EVENT_DATA,
    CHECK_DI_CONFORMANCE_EVENT_ID: CHECK_DI_CONFORMANCE_EVENT_DATA,
    CHECK_UTILS_CONFORMANCE_EVENT_ID: CHECK_UTILS_CONFORMANCE_EVENT_DATA,
    CHECK_CONTEXT_CONFORMANCE_EVENT_ID: CHECK_CONTEXT_CONFORMANCE_EVENT_DATA,
    CHECK_BLUEPRINTS_CONFORMANCE_EVENT_ID: CHECK_BLUEPRINTS_CONFORMANCE_EVENT_DATA,
    CHECK_REPOS_CONFORMANCE_EVENT_ID: CHECK_REPOS_CONFORMANCE_EVENT_DATA,
    EMIT_SEMANTIC_RESULT_EVENT_ID: EMIT_SEMANTIC_RESULT_EVENT_DATA,
    GENERATE_CODE_EVENT_ID: GENERATE_CODE_EVENT_DATA,
    OPTIMIZE_CODE_EVENT_ID: OPTIMIZE_CODE_EVENT_DATA,
    EMIT_CODEGEN_RESULT_EVENT_ID: EMIT_CODEGEN_RESULT_EVENT_DATA,
    LOAD_FROM_AST_EVENT_ID: LOAD_FROM_AST_EVENT_DATA,
}

# ** constant: compiler_default_app_sessions
COMPILER_DEFAULT_APP_SESSIONS = {
    COMPILER_SESSION_ID: COMPILER_SESSION_DATA,
    COMPILER_CLI_SESSION_ID: COMPILER_CLI_SESSION_DATA,
}
