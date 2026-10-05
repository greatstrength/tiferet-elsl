"""Compiler Provision Context Tests"""

# *** imports

# ** infra
import pytest
from pydantic import ValidationError
from tiferet.contexts.cache import CacheContext

# ** app
from ...assets.provision import COMPILER_DEFAULT_PROVISIONS
from ...domain.provision import Production, ProvisionRegistration, Specification
from ..provision import (
    COMPILER_PROVISION_CACHE_PREFIX,
    add_default_provisions,
)

# *** tests

# ** test: provision_prefix_is_closed_over
def test_provision_prefix_is_closed_over() -> None:
    '''
    Test that the provision factory closes over its prefix.
    '''

    # The tuple is the namespace the overlay will write.
    assert COMPILER_PROVISION_CACHE_PREFIX == ('compiler', 'provisions')

    # One factory call seeds the catalog. This test does not import build_cache.
    cache = add_default_provisions(COMPILER_DEFAULT_PROVISIONS)(lambda: CacheContext())()
    assert list(cache.get_by_prefix(*COMPILER_PROVISION_CACHE_PREFIX)) == list(COMPILER_DEFAULT_PROVISIONS)

# ** test: provisions_are_registrations_not_behaviors
def test_provisions_are_registrations_not_behaviors() -> None:
    '''
    Test that each seeded provision is a registration, not a behavior.
    '''

    # The stored value is validated. The asset dict is left without id.
    cache = add_default_provisions(COMPILER_DEFAULT_PROVISIONS)(lambda: CacheContext())()
    stored = cache.get_by_prefix(*COMPILER_PROVISION_CACHE_PREFIX)
    assert list(stored) == list(COMPILER_DEFAULT_PROVISIONS)
    for key, asset in COMPILER_DEFAULT_PROVISIONS.items():
        value = stored[key]
        assert isinstance(value, ProvisionRegistration)
        assert value.id == key
        assert value is not asset
        assert not isinstance(value, Specification)
        assert not isinstance(value, Production)
        assert 'id' not in asset
        assert value.kind == asset['kind']
        assert value.module_path == asset['module_path']
        assert value.class_name == asset['class_name']

# ** test: invalid_provision_row_raises
def test_invalid_provision_row_raises() -> None:
    '''
    Test that a bad provision row raises and returns no cache.
    '''

    # A kind outside the registration literal fails validation.
    bad = {
        'bad.row': {
            'kind': 'not-a-kind',
            'applies_to': 'member',
            'module_path': 'compiler.utils.core',
            'class_name': 'Missing',
            'parameters': {},
        },
    }
    returned = None
    with pytest.raises(ValidationError):
        returned = add_default_provisions(bad)(lambda: CacheContext())()

    # The seed is not a partial success.
    assert returned is None
