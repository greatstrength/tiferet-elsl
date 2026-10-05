"""Compiler Core Blueprints"""

# *** imports

# ** core
from typing import Any, Dict

# ** infra
from tiferet.blueprints.core import build_cache as build_tiferet_cache
from tiferet.contexts.app import (
    add_default_app_services,
    add_default_app_sessions,
)
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.cli import add_default_cli_commands
from tiferet.contexts.error import add_default_errors
from tiferet.contexts.feature import add_default_features

# ** app
from .. import assets as a
from ..contexts.catalog import (
    add_default_grammars,
    add_default_productions,
    add_default_tokens,
)
from ..contexts.provision import add_default_provisions

# *** blueprints

# ** blueprint: build_cache
@add_default_cli_commands(a.cli.COMPILER_DEFAULT_COMMANDS)
@add_default_features(a.feature.COMPILER_DEFAULT_FEATURES)
@add_default_app_sessions(a.app.COMPILER_DEFAULT_APP_SESSIONS)
@add_default_app_services(a.app.COMPILER_DEFAULT_SERVICES)
@add_default_provisions(a.provision.COMPILER_DEFAULT_PROVISIONS)
@add_default_productions(a.production.COMPILER_DEFAULT_PRODUCTIONS)
@add_default_tokens(a.token.COMPILER_DEFAULT_TOKENS)
@add_default_grammars(a.grammar.COMPILER_DEFAULT_GRAMMARS)
@add_default_errors(a.error.COMPILER_DEFAULT_ERRORS)
def build_cache(cache: Dict[str, Any] = None) -> CacheContext:
    '''
    Build the compiler cache as the framework cache plus this package's catalogs.

    The wrap seeds framework errors, services, constants, sessions, and logging.
    Stacked decorators then seed the compiler catalogs. This function does not.

    :param cache: An optional initial cache dictionary for the root namespace.
    :type cache: Dict[str, Any]
    :return: The pre-seeded cache context.
    :rtype: CacheContext
    '''

    # Delegate to the framework cache builder. Stacked decorators seed after that return.
    return build_tiferet_cache(cache=cache)
