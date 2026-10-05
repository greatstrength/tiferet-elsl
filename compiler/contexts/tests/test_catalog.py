"""Compiler Catalog Context Tests"""

# *** imports

# ** core
import ast
from pathlib import Path

# ** infra
from tiferet.contexts.cache import CacheContext

# ** app
from ...assets.grammar import COMPILER_DEFAULT_GRAMMARS
from ...assets.production import COMPILER_DEFAULT_PRODUCTIONS
from ...assets.token import COMPILER_DEFAULT_TOKENS
from ..catalog import (
    COMPILER_GRAMMAR_CACHE_PREFIX,
    COMPILER_PRODUCTION_CACHE_PREFIX,
    COMPILER_TOKEN_CACHE_PREFIX,
    add_default_grammars,
    add_default_productions,
    add_default_tokens,
)

# *** constants

# ** constant: contexts_dir
_CONTEXTS_DIR = Path(__file__).resolve().parent.parent

# *** tests

# ** test: dialect_prefixes_are_closed_over
def test_dialect_prefixes_are_closed_over() -> None:
    '''
    Test that each dialect factory closes over its own prefix.
    '''

    # The tuples are singular constants with plural segments.
    assert COMPILER_GRAMMAR_CACHE_PREFIX == ('compiler', 'grammars')
    assert COMPILER_TOKEN_CACHE_PREFIX == ('compiler', 'tokens')
    assert COMPILER_PRODUCTION_CACHE_PREFIX == ('compiler', 'productions')

    # Calling one factory does not require the blueprint.
    grammars = add_default_grammars(COMPILER_DEFAULT_GRAMMARS)(lambda: CacheContext())()
    tokens = add_default_tokens(COMPILER_DEFAULT_TOKENS)(lambda: CacheContext())()
    productions = add_default_productions(COMPILER_DEFAULT_PRODUCTIONS)(lambda: CacheContext())()
    assert list(grammars.get_by_prefix(*COMPILER_GRAMMAR_CACHE_PREFIX)) == list(COMPILER_DEFAULT_GRAMMARS)
    assert list(tokens.get_by_prefix(*COMPILER_TOKEN_CACHE_PREFIX)) == list(COMPILER_DEFAULT_TOKENS)
    assert list(productions.get_by_prefix(*COMPILER_PRODUCTION_CACHE_PREFIX)) == list(COMPILER_DEFAULT_PRODUCTIONS)

# ** test: dialect_bodies_are_stored_by_identity
def test_dialect_bodies_are_stored_by_identity() -> None:
    '''
    Test that dialect bodies are cached unchanged, in items order.
    '''

    # Grammar keys are ids. The body is the catalog object.
    grammars = add_default_grammars(COMPILER_DEFAULT_GRAMMARS)(lambda: CacheContext())()
    stored_grammars = grammars.get_by_prefix(*COMPILER_GRAMMAR_CACHE_PREFIX)
    assert list(stored_grammars) == list(COMPILER_DEFAULT_GRAMMARS)
    for key, body in COMPILER_DEFAULT_GRAMMARS.items():
        assert stored_grammars[key] is body
        assert 'id' not in body

    # Token keys are names. TRUE stays a string key.
    tokens = add_default_tokens(COMPILER_DEFAULT_TOKENS)(lambda: CacheContext())()
    stored_tokens = tokens.get_by_prefix(*COMPILER_TOKEN_CACHE_PREFIX)
    assert list(stored_tokens) == list(COMPILER_DEFAULT_TOKENS)
    assert 'TRUE' in stored_tokens
    assert isinstance(next(key for key in stored_tokens if key == 'TRUE'), str)
    for key, body in COMPILER_DEFAULT_TOKENS.items():
        assert stored_tokens[key] is body
        assert 'name' not in body

    # Production keys are names. The body is not copied.
    productions = add_default_productions(COMPILER_DEFAULT_PRODUCTIONS)(lambda: CacheContext())()
    stored_productions = productions.get_by_prefix(*COMPILER_PRODUCTION_CACHE_PREFIX)
    assert list(stored_productions) == list(COMPILER_DEFAULT_PRODUCTIONS)
    for key, body in COMPILER_DEFAULT_PRODUCTIONS.items():
        assert stored_productions[key] is body
        assert 'name' not in body

# ** test: catalog_module_does_not_name_provision_registration
def test_catalog_module_does_not_name_provision_registration() -> None:
    '''
    Test that the dialect module does not import a provision model.
    '''

    # The catalog module has no provision registration name and no domain import.
    source = (_CONTEXTS_DIR / 'catalog.py').read_text(encoding='utf-8')
    assert 'ProvisionRegistration' not in source
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.module != 'domain.provision'
            assert 'domain' not in (node.module or '').split('.')

    # The package marker does not import catalog or provision.
    init_tree = ast.parse((_CONTEXTS_DIR / '__init__.py').read_text(encoding='utf-8'))
    imported = []
    for node in ast.walk(init_tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or '')
            imported.extend(alias.name for alias in node.names)
    assert 'catalog' not in imported
    assert 'provision' not in imported
