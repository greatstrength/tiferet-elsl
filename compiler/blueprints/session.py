"""Compiler Session Blueprints"""

# *** imports

# ** core
from typing import Any, Callable

# ** infra
from tiferet.assets import TiferetError
from tiferet.blueprints.core import (
    build_app_service_container,
    build_service_resolver,
)
from tiferet.contexts.cache import CacheContext

# ** app
from .core import build_cache
from ..contexts.feature import (
    ASKED_STEPS,
    CompilerFeatureContext,
)
from ..contexts.session import CompilerAppSessionContext

# *** constants

# ** constant: unknown_compiler_step
UNKNOWN_COMPILER_STEP = 'UNKNOWN_COMPILER_STEP'

# *** blueprints

# ** blueprint: get_feature
def get_feature(cache: CacheContext, get_dependency: Callable) -> Callable:
    '''
    Return a handler that constructs a step context for one asked step.

    A known step is constructed here. An unknown step fails before that
    construction. This is not the framework feature lookup.

    :param cache: The cache closed over by the handler.
    :type cache: CacheContext
    :param get_dependency: The resolver closed over by the handler.
    :type get_dependency: Callable
    :return: A handler of one asked step.
    :rtype: Callable
    '''

    # Close over the pair. Each call constructs a new context.
    def handler(step: str) -> CompilerFeatureContext:

        # An unknown string fails before the context is constructed.
        if step not in ASKED_STEPS:
            TiferetError.raise_error(
                UNKNOWN_COMPILER_STEP,
                message=f'Unknown compiler step: {step!r}.',
                step=step,
            )

        # Both objects are the ones this closure closed over.
        return CompilerFeatureContext(
            cache=cache,
            get_dependency=get_dependency,
        )

    # Return the handler. Do not cache the context.
    return handler

# ** blueprint: compose_get_dependency
def compose_get_dependency(cache: CacheContext) -> Callable:
    '''
    Build a resolver closure that takes one service id.

    This is not the creation interface. A caller that already has a
    resolver does not call this function.

    :param cache: The cache the container is built from.
    :type cache: CacheContext
    :return: A callable of one service id.
    :rtype: Callable
    '''

    # Build the container from the cache only. Do not pass a session.
    container = build_app_service_container(cache)
    resolver = build_service_resolver(container)

    # The closure takes one service id and no flags.
    def get_dependency(service_id: str) -> Any:
        return resolver.get_dependency(service_id)

    # Return the closure. Do not export it.
    return get_dependency

# ** blueprint: build_compiler_session
def build_compiler_session(cache: CacheContext = None,
        get_dependency: Callable = None) -> CompilerAppSessionContext:
    '''
    Resolve the cache and the resolver, then pass the step handler.

    An omitted cache is built once. A passed resolver is closed over and
    is not replaced.

    :param cache: An existing cache, or None to build one.
    :type cache: CacheContext
    :param get_dependency: An existing resolver, or None to compose one.
    :type get_dependency: Callable
    :return: The compiler session context.
    :rtype: CompilerAppSessionContext
    '''

    # Use the passed cache. Build one only when it was omitted.
    resolved = cache if cache is not None else build_cache()

    # Use the passed resolver. Compose one only when it was omitted.
    dependency = get_dependency if get_dependency is not None else compose_get_dependency(resolved)

    # Pass the handler. Do not store the resolver on the session.
    return CompilerAppSessionContext(
        cache=resolved,
        get_feature=get_feature(resolved, dependency),
    )
