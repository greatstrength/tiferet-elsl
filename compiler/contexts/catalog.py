"""Compiler Catalog Contexts"""

# *** imports

# ** core
from typing import Any, Callable, Dict, Tuple

# ** infra
from tiferet.contexts.core import add_default_cache_items

# *** constants

# ** constant: compiler_grammar_cache_prefix
COMPILER_GRAMMAR_CACHE_PREFIX: Tuple[str, ...] = ('compiler', 'grammars')

# ** constant: compiler_token_cache_prefix
COMPILER_TOKEN_CACHE_PREFIX: Tuple[str, ...] = ('compiler', 'tokens')

# ** constant: compiler_production_cache_prefix
COMPILER_PRODUCTION_CACHE_PREFIX: Tuple[str, ...] = ('compiler', 'productions')

# *** functions

# ** function: add_default_grammars
def add_default_grammars(grammars: Dict[str, Any]) -> Callable:
    '''
    Pre-seed a cache with raw grammar catalog bodies.

    The group-dict key is the cache key. The body is stored unchanged.

    :param grammars: A mapping of grammar id to catalog body.
    :type grammars: Dict[str, Any]
    :return: A decorator that wraps a cache-builder callable.
    :rtype: Callable
    '''

    # Seed the raw grammar bodies under the compiler grammar prefix.
    return add_default_cache_items(grammars, COMPILER_GRAMMAR_CACHE_PREFIX)

# ** function: add_default_tokens
def add_default_tokens(tokens: Dict[str, Any]) -> Callable:
    '''
    Pre-seed a cache with raw token catalog bodies.

    The group-dict key is the cache key. The body is stored unchanged.

    :param tokens: A mapping of token name to catalog body.
    :type tokens: Dict[str, Any]
    :return: A decorator that wraps a cache-builder callable.
    :rtype: Callable
    '''

    # Seed the raw token bodies under the compiler token prefix.
    return add_default_cache_items(tokens, COMPILER_TOKEN_CACHE_PREFIX)

# ** function: add_default_productions
def add_default_productions(productions: Dict[str, Any]) -> Callable:
    '''
    Pre-seed a cache with raw production catalog bodies.

    The group-dict key is the cache key. The body is stored unchanged.

    :param productions: A mapping of production name to catalog body.
    :type productions: Dict[str, Any]
    :return: A decorator that wraps a cache-builder callable.
    :rtype: Callable
    '''

    # Seed the raw production bodies under the compiler production prefix.
    return add_default_cache_items(productions, COMPILER_PRODUCTION_CACHE_PREFIX)
