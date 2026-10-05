"""Compiler Default Application Catalog Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
from tiferet.assets.core import (
    create_app_service_dependency_data,
    create_default_app_session_data,
)
from tiferet.domain.app import AppServiceDependency, AppSession

# ** app
from ..app import COMPILER_DEFAULT_APP_SESSIONS, COMPILER_DEFAULT_SERVICES

# *** constants

# ** constant: assets_dir
_ASSETS_DIR = Path(__file__).resolve().parent.parent

# ** constant: catalog_modules
_CATALOG_MODULES = (
    'app.py',
    'feature.py',
    'cli.py',
)

# ** constant: forbidden_imports
_FORBIDDEN_IMPORTS = (
    'tiferet_ly',
    'yaml',
    'tiferet.domain',
    'tiferet.mappers',
    'tiferet.contexts',
    'tiferet.blueprints',
    'compiler.domain',
    'compiler.events',
    'compiler.mappers',
    'compiler.utils',
    'compiler.contexts',
    'compiler.blueprints',
    'compiler.interfaces',
    'compiler.cli',
    'from .app',
    'from .feature',
    'from .cli',
    'import app',
    'import feature',
    'import cli',
)

# ** constant: deleted_yaml_names
_DELETED_YAML_NAMES = (
    'config.yml',
    'feature.yml',
    'cli.yml',
    'errors.yml',
    'tokens.yml',
    'grammars.yml',
    'productions.yml',
)

# ** constant: service_rows
_SERVICE_ROWS = (
    (
        'token_service',
        'tiferet_ly.repos.token',
        'TokenConfigRepository',
    ),
    (
        'grammar_service',
        'tiferet_ly.repos.grammar',
        'GrammarConfigRepository',
    ),
    (
        'production_service',
        'tiferet_ly.repos.production',
        'ProductionConfigRepository',
    ),
    (
        'lexer_service',
        'compiler.utils.lexer',
        'TiferetLexer',
    ),
    (
        'parser_service',
        'compiler.utils.parser',
        'TiferetParser',
    ),
    (
        'codegen_service',
        'compiler.utils.codegen',
        'TiferetGenerator',
    ),
    (
        'optimizer_service',
        'compiler.utils.optimizer',
        'YamlAnchorOptimizer',
    ),
    (
        'perform_lexical_analysis_event',
        'compiler.events.lexer',
        'PerformLexicalAnalysis',
    ),
    (
        'emit_scan_result_event',
        'compiler.events.lexer',
        'EmitScanResult',
    ),
    (
        'perform_syntactic_analysis_event',
        'compiler.events.parser',
        'PerformSyntacticAnalysis',
    ),
    (
        'emit_parse_result_event',
        'compiler.events.parser',
        'EmitParseResult',
    ),
    (
        'perform_semantic_analysis_event',
        'compiler.events.semantic',
        'PerformSemanticAnalysis',
    ),
    (
        'check_common_conformance_event',
        'compiler.events.typecheck',
        'CheckCommonConformance',
    ),
    (
        'check_event_conformance_event',
        'compiler.events.typecheck',
        'CheckEventConformance',
    ),
    (
        'check_asset_conformance_event',
        'compiler.events.typecheck',
        'CheckAssetConformance',
    ),
    (
        'check_domain_conformance_event',
        'compiler.events.typecheck',
        'CheckDomainConformance',
    ),
    (
        'check_mapper_conformance_event',
        'compiler.events.typecheck',
        'CheckMapperConformance',
    ),
    (
        'check_interface_conformance_event',
        'compiler.events.typecheck',
        'CheckInterfaceConformance',
    ),
    (
        'check_di_conformance_event',
        'compiler.events.typecheck',
        'CheckDIConformance',
    ),
    (
        'check_utils_conformance_event',
        'compiler.events.typecheck',
        'CheckUtilsConformance',
    ),
    (
        'check_context_conformance_event',
        'compiler.events.typecheck',
        'CheckContextsConformance',
    ),
    (
        'check_blueprints_conformance_event',
        'compiler.events.typecheck',
        'CheckBlueprintsConformance',
    ),
    (
        'check_repos_conformance_event',
        'compiler.events.typecheck',
        'CheckReposConformance',
    ),
    (
        'emit_semantic_result_event',
        'compiler.events.semantic',
        'EmitSemanticResult',
    ),
    (
        'generate_code_event',
        'compiler.events.codegen',
        'GenerateCode',
    ),
    (
        'optimize_code_event',
        'compiler.events.codegen',
        'OptimizeCode',
    ),
    (
        'emit_codegen_result_event',
        'compiler.events.codegen',
        'EmitCodegenResult',
    ),
    (
        'load_from_ast_event',
        'compiler.events.codegen',
        'LoadFromAST',
    ),
)

# ** constant: session_rows
_SESSION_ROWS = (
    (
        'compiler',
        'Tiferet Dialect Compiler',
        'Component-agnostic compiler session. The component type arrives as request data.',
    ),
    (
        'compiler_cli',
        'Compiler CLI',
        'Component-agnostic compiler CLI. The component type arrives as request data.',
    ),
)

# *** tests

# ** test: compiler_default_services_match_declared_rows
def test_compiler_default_services_match_declared_rows() -> None:
    '''
    Test that the service catalog has the twenty-eight declared rows.
    '''

    # Insertion order is the declared order, not a sorted order.
    assert list(COMPILER_DEFAULT_SERVICES) == [key for key, _path, _name in _SERVICE_ROWS]

    # Each value is the factory shape. The key is not copied into the value.
    for key, module_path, class_name in _SERVICE_ROWS:
        value = COMPILER_DEFAULT_SERVICES[key]
        assert 'id' not in value
        assert 'service_id' not in value
        assert value['parameters'] == {}
        assert set(value) == {'module_path', 'class_name', 'parameters'}
        assert value == create_app_service_dependency_data(
            module_path,
            class_name,
        )

        # Reinjecting the key validates as an app service dependency.
        dependency = AppServiceDependency.model_validate({
            **value,
            'service_id': key,
        })
        assert dependency.service_id == key
        assert dependency.module_path == module_path
        assert dependency.class_name == class_name
        assert dependency.parameters == {}

# ** test: compiler_default_app_sessions_match_declared_rows
def test_compiler_default_app_sessions_match_declared_rows() -> None:
    '''
    Test that the session catalog carries name and description only.
    '''

    # The two sessions stay in document order.
    assert list(COMPILER_DEFAULT_APP_SESSIONS) == [key for key, _name, _text in _SESSION_ROWS]

    # Path blocks are not fields of the default session.
    for key, name, description in _SESSION_ROWS:
        value = COMPILER_DEFAULT_APP_SESSIONS[key]
        assert set(value) == {'name', 'description'}
        assert 'id' not in value
        assert 'const' not in value
        assert 'constants' not in value
        assert value == create_default_app_session_data(
            name,
            description=description,
        )

        # The model defaults constants. The catalog did not carry them.
        session = AppSession.model_validate({
            **value,
            'id': key,
        })
        assert session.id == key
        assert session.name == name
        assert session.description == description
        assert session.constants == {}

# ** test: catalog_modules_do_not_name_forbidden_imports
def test_catalog_modules_do_not_name_forbidden_imports() -> None:
    '''
    Test that the three catalogs do not import forbidden modules or name deleted YAML.
    '''

    # Logging is not a compiler catalog. The deleted YAML files are not a second source.
    assert not (_ASSETS_DIR / 'logging.py').exists()
    for name in _DELETED_YAML_NAMES:
        assert not (_ASSETS_DIR / name).exists()

    # Import lines stay inside the permitted set. Importing the modules reads no file.
    for name in _CATALOG_MODULES:
        source = (_ASSETS_DIR / name).read_text(encoding='utf-8')
        assert 'open(' not in source
        import_lines = [
            line.strip()
            for line in source.splitlines()
            if line.strip().startswith(('import ', 'from '))
        ]
        for line in import_lines:
            for forbidden in _FORBIDDEN_IMPORTS:
                assert forbidden not in line
        for yaml_name in _DELETED_YAML_NAMES:
            assert yaml_name not in source
