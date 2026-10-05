"""Compiler Provision Contexts"""

# *** imports

# ** core
from typing import Any, Callable, Dict, Tuple

# ** infra
from tiferet.contexts.core import add_default_cache_items

# ** app
from ..domain.provision import ProvisionRegistration

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
