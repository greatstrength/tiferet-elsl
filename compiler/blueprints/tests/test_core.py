"""Compiler Cache Seed Blueprint Tests"""

# *** imports

# ** core
import ast
import importlib
from pathlib import Path

# ** infra
from tiferet.assets.app import CORE_DEFAULT_SERVICES
from tiferet.assets.error import CORE_DEFAULT_ERRORS
from tiferet.contexts.app import (
    APP_SERVICE_CACHE_PREFIX,
    APP_SESSION_CACHE_PREFIX,
)
from tiferet.contexts.error import ERROR_CACHE_PREFIX
from tiferet.domain import (
    AppServiceDependency,
    AppSession,
    CliCommand,
    Error,
    Feature,
    LoggingSettings,
)

# ** app
import compiler
from ...assets.app import (
    COMPILER_DEFAULT_APP_SESSIONS,
    COMPILER_DEFAULT_SERVICES,
)
from ...assets.cli import COMPILER_DEFAULT_COMMANDS
from ...assets.error import COMPILER_DEFAULT_ERRORS
from ...assets.feature import COMPILER_DEFAULT_FEATURES
from ...assets.grammar import COMPILER_DEFAULT_GRAMMARS
from ...contexts.catalog import COMPILER_GRAMMAR_CACHE_PREFIX
from .. import __all__ as blueprint_all
from ..core import build_cache

# *** constants

# ** constant: blueprints_dir
_BLUEPRINTS_DIR = Path(__file__).resolve().parent.parent

# ** constant: new_modules
_NEW_MODULES = (
    _BLUEPRINTS_DIR / 'core.py',
    _BLUEPRINTS_DIR / '__init__.py',
    _BLUEPRINTS_DIR.parent / 'contexts' / 'catalog.py',
    _BLUEPRINTS_DIR.parent / 'contexts' / 'provision.py',
    _BLUEPRINTS_DIR.parent / 'contexts' / '__init__.py',
)

# ** constant: deleted_yaml_names
_DELETED_YAML_NAMES = (
    'errors.yml',
    'tokens.yml',
    'grammars.yml',
    'productions.yml',
    'config.yml',
    'feature.yml',
    'cli.yml',
)

# ** constant: forbidden_blueprint_names
_FORBIDDEN_BLUEPRINT_NAMES = (
    'ProvisionRegistration',
    'AppServiceDependency',
    'AppSession',
    'CliCommand',
    'model=',
    'id_field=',
    'importlib',
    'TIFERET_DIALECT_ID',
    'tiferet.blueprints.admin',
    'get_app_session',
    'compose_session_context',
    'COMPILER_DEFAULT_CONSTANTS',
    'COMPILER_DEFAULT_LOGGING_SETTINGS',
)

# *** tests

# ** test: blueprint_exports_cache_and_session
def test_blueprint_exports_cache_and_session() -> None:
    '''
    Test that __all__ is build_cache and build_compiler_session.
    '''

    # The public names are the two builders. There is no App or CLI alias.
    assert blueprint_all == [
        'build_cache',
        'build_compiler_session',
    ]
    assert not hasattr(compiler, 'build_cache')
    assert not hasattr(compiler.blueprints, 'App')
    assert not hasattr(compiler.blueprints, 'CLI')

# ** test: build_cache_source_wraps_and_stacks
def test_build_cache_source_wraps_and_stacks() -> None:
    '''
    Test that the blueprint body wraps the framework builder.
    '''

    # The only framework blueprint import is the renamed cache builder.
    source = (_BLUEPRINTS_DIR / 'core.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    blueprint_imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith('tiferet.blueprints'):
            blueprint_imports.append((node.module, tuple((alias.name, alias.asname) for alias in node.names)))
    assert blueprint_imports == [
        (
            'tiferet.blueprints.core',
            (
                (
                    'build_cache',
                    'build_tiferet_cache',
                ),
            ),
        ),
    ]

    # Source order is the stated stack. Each argument is that catalog.
    func = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == 'build_cache'
    )
    expected = (
        ('add_default_cli_commands', 'cli', 'COMPILER_DEFAULT_COMMANDS'),
        ('add_default_features', 'feature', 'COMPILER_DEFAULT_FEATURES'),
        ('add_default_app_sessions', 'app', 'COMPILER_DEFAULT_APP_SESSIONS'),
        ('add_default_app_services', 'app', 'COMPILER_DEFAULT_SERVICES'),
        ('add_default_provisions', 'provision', 'COMPILER_DEFAULT_PROVISIONS'),
        ('add_default_productions', 'production', 'COMPILER_DEFAULT_PRODUCTIONS'),
        ('add_default_tokens', 'token', 'COMPILER_DEFAULT_TOKENS'),
        ('add_default_grammars', 'grammar', 'COMPILER_DEFAULT_GRAMMARS'),
        ('add_default_errors', 'error', 'COMPILER_DEFAULT_ERRORS'),
    )
    assert len(func.decorator_list) == len(expected)
    for deco, (name, group, catalog) in zip(func.decorator_list, expected):
        assert deco.func.id == name
        assert deco.args[0].value.value.id == 'a'
        assert deco.args[0].value.attr == group
        assert deco.args[0].attr == catalog

    # The body returns the wrap. It does not construct a cache or call set.
    returned = func.body[-1]
    assert isinstance(returned, ast.Return)
    assert returned.value.func.id == 'build_tiferet_cache'
    assert returned.value.keywords[0].arg == 'cache'
    assert returned.value.keywords[0].value.id == 'cache'
    for node in ast.walk(func):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id != 'CacheContext'
        if isinstance(node, ast.Attribute):
            assert node.attr != 'set'

    # The blueprint does not name models, fields, or deleted files.
    for name in _FORBIDDEN_BLUEPRINT_NAMES:
        assert name not in source
    assert 'Feature' not in source
    for path in _NEW_MODULES:
        module_source = path.read_text(encoding='utf-8')
        for filename in _DELETED_YAML_NAMES:
            assert filename not in module_source

# ** test: build_cache_keeps_framework_and_compiler_errors
def test_build_cache_keeps_framework_and_compiler_errors() -> None:
    '''
    Test that compiler errors join the framework error namespace.
    '''

    # Both catalogs are present, and neither replaces the other.
    cache = build_cache()
    app_error = cache.get('APP_ERROR', *ERROR_CACHE_PREFIX)
    assert isinstance(app_error, Error)
    assert app_error.id == 'APP_ERROR'
    assert app_error.name == CORE_DEFAULT_ERRORS['APP_ERROR']['name']
    framework_ids = set(CORE_DEFAULT_ERRORS)
    compiler_ids = set(COMPILER_DEFAULT_ERRORS)
    assert framework_ids.isdisjoint(compiler_ids)
    assert 'TEXT_EXTRACTION_FAILED' in compiler_ids
    assert 'APP_ERROR' not in compiler_ids
    errors = cache.get_by_prefix(*ERROR_CACHE_PREFIX)
    for key in compiler_ids:
        error = errors[key]
        assert isinstance(error, Error)
        assert error.id == key
        assert error.error_code == key
        assert 'id' not in COMPILER_DEFAULT_ERRORS[key]

# ** test: build_cache_keeps_framework_and_compiler_services
def test_build_cache_keeps_framework_and_compiler_services() -> None:
    '''
    Test that compiler services join the framework service namespace.
    '''

    # The namespace is the union, and the two key sets do not overlap.
    cache = build_cache()
    services = cache.get_by_prefix(*APP_SERVICE_CACHE_PREFIX)
    framework_ids = set(CORE_DEFAULT_SERVICES)
    compiler_ids = set(COMPILER_DEFAULT_SERVICES)
    assert services
    assert framework_ids.isdisjoint(compiler_ids)
    assert set(services) == framework_ids | compiler_ids
    for key in compiler_ids:
        value = services[key]
        assert isinstance(value, AppServiceDependency)
        assert value.service_id == key
        assert 'service_id' not in COMPILER_DEFAULT_SERVICES[key]

# ** test: build_cache_keeps_framework_and_compiler_sessions
def test_build_cache_keeps_framework_and_compiler_sessions() -> None:
    '''
    Test that compiler sessions join the framework session namespace.
    '''

    # Admin sessions stay. Compiler sessions are added with the key as id.
    cache = build_cache()
    sessions = cache.get_by_prefix(*APP_SESSION_CACHE_PREFIX)
    assert sessions
    for key in (
        'admin',
        'admin_cli',
        'compiler',
        'compiler_cli',
    ):
        assert key in sessions
    for key in (
        'compiler',
        'compiler_cli',
    ):
        value = sessions[key]
        asset = COMPILER_DEFAULT_APP_SESSIONS[key]
        assert isinstance(value, AppSession)
        assert value.id == key
        assert 'id' not in asset
        assert 'constants' not in asset

# ** test: build_cache_keeps_framework_logging
def test_build_cache_keeps_framework_logging() -> None:
    '''
    Test that the wrap seeds logging and this package adds none.
    '''

    # The logging namespace is the framework default, not an empty compiler catalog.
    cache = build_cache()
    assert cache.get_by_prefix('logging')
    assert isinstance(cache.get('default', 'logging'), LoggingSettings)

# ** test: build_cache_seeds_features
def test_build_cache_seeds_features() -> None:
    '''
    Test that feature keys are the compiler catalog, validated as features.
    '''

    # Order is the catalog order. Steps keep parameters and do not gain params.
    cache = build_cache()
    features = cache.get_by_prefix('app', 'features')
    assert list(features) == list(COMPILER_DEFAULT_FEATURES)
    generate = []
    optimize = []
    for key, feature in features.items():
        assert isinstance(feature, Feature)
        assert feature.id == key
        for step in feature.steps:
            assert 'params' not in type(step).model_fields
            assert 'params' not in step.model_dump()
            if step.name == 'Generate Code':
                generate.append(step)
            if step.name == 'Optimize Code':
                optimize.append(step)
    assert generate
    assert optimize
    assert all(step.parameters for step in generate)
    assert all(step.parameters for step in optimize)

# ** test: build_cache_seeds_commands
def test_build_cache_seeds_commands() -> None:
    '''
    Test that command keys are the compiler catalog, with derived ids.
    '''

    # The model derives id. The cache key is already that join.
    cache = build_cache()
    commands = cache.get_by_prefix('cli', 'commands')
    assert list(commands) == list(COMPILER_DEFAULT_COMMANDS)
    for key, command in commands.items():
        assert isinstance(command, CliCommand)
        assert command.id == key

# ** test: root_cache_does_not_override_seeds
def test_root_cache_does_not_override_seeds() -> None:
    '''
    Test that the optional cache dict stays in the root namespace.
    '''

    # A root entry does not replace a seeded grammar or error.
    cache = build_cache(cache={'kept': 1})
    assert cache.get('kept') == 1
    assert cache.get_by_prefix(*COMPILER_GRAMMAR_CACHE_PREFIX)
    for key, body in COMPILER_DEFAULT_GRAMMARS.items():
        assert cache.get(key, *COMPILER_GRAMMAR_CACHE_PREFIX) is body
    assert isinstance(cache.get('APP_ERROR', *ERROR_CACHE_PREFIX), Error)
    assert cache.get('APP_ERROR', *ERROR_CACHE_PREFIX).id == 'APP_ERROR'
    assert isinstance(cache.get('TEXT_EXTRACTION_FAILED', *ERROR_CACHE_PREFIX), Error)
    assert cache.get('TEXT_EXTRACTION_FAILED', *ERROR_CACHE_PREFIX).id == 'TEXT_EXTRACTION_FAILED'

    # A root key of the same name does not replace the seeded error.
    overridden = build_cache(cache={'TEXT_EXTRACTION_FAILED': 'root'})
    assert overridden.get('TEXT_EXTRACTION_FAILED') == 'root'
    seeded = overridden.get('TEXT_EXTRACTION_FAILED', *ERROR_CACHE_PREFIX)
    assert isinstance(seeded, Error)
    assert seeded.id == 'TEXT_EXTRACTION_FAILED'

# ** test: build_cache_does_not_open_or_import
def test_build_cache_does_not_open_or_import(monkeypatch) -> None:
    '''
    Test that seeding does not open a file or import a provision class.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: object
    '''

    # Fail closed if the seed reaches for a file or a behavior module.
    def fail_open(*args, **kwargs):
        raise AssertionError('open')

    def fail_import(*args, **kwargs):
        raise AssertionError('import_module')

    monkeypatch.setattr('builtins.open', fail_open)
    monkeypatch.setattr(importlib, 'import_module', fail_import)

    # The seed still returns the compiler error.
    cache = build_cache()
    assert isinstance(cache.get('TEXT_EXTRACTION_FAILED', *ERROR_CACHE_PREFIX), Error)
