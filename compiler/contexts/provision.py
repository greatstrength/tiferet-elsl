"""Compiler Provision Contexts"""

# *** imports

# ** core
from pathlib import Path
from typing import Any, Callable, Dict, Tuple

# ** infra
from tiferet.contexts.core import add_default_cache_items

# ** app
from ..domain.provision import ProvisionRegistration
from ..repos.provision import ProvisionConfigRepository

# *** constants

# ** constant: compiler_provision_cache_prefix
COMPILER_PROVISION_CACHE_PREFIX: Tuple[str, ...] = ('compiler', 'provisions')

# *** functions

# ** function: add_default_provisions
def add_default_provisions(provisions: Dict[str, Any]) -> Callable:
    '''
    Pre-seed a cache with validated provision registrations.

    The stored value names a provision. It does not construct the behavior.

    :param provisions: A mapping of provision id to registration data.
    :type provisions: Dict[str, Any]
    :return: A decorator that wraps a cache-builder callable.
    :rtype: Callable
    '''

    # Validate each row as a registration and seed it under the provision prefix.
    return add_default_cache_items(
        provisions,
        COMPILER_PROVISION_CACHE_PREFIX,
        model=ProvisionRegistration,
        id_field='id',
    )

# ** function: apply_provision_overlay
def apply_provision_overlay(cache, provision_config: str = None) -> None:
    '''
    Replace or add provision registrations from a consumer file.

    An absent path writes nothing. A present row replaces the same id in
    place. The stored value stays a registration, not a behavior instance.

    :param cache: The cache whose provision namespace is updated.
    :type cache: Any
    :param provision_config: Path to a consumer file, or None.
    :type provision_config: str
    :return: None
    :rtype: None
    '''

    # None and an empty path are absence. Do not construct a repository.
    if not provision_config:
        return

    # A missing path is not FILE_NOT_FOUND. Do not load it.
    if not Path(provision_config).exists():
        return

    # A present path is loaded, including a bad extension.
    repository = ProvisionConfigRepository(provision_config)
    for registration in repository.list():
        cache.set(
            registration.id,
            registration,
            *COMPILER_PROVISION_CACHE_PREFIX,
        )
