"""Compiler Provision Context Tests"""

# *** imports

# ** core
import inspect
from pathlib import Path

# ** infra
import pytest
from pydantic import ValidationError
from tiferet.contexts.cache import CacheContext

# ** app
from ...assets.provision import COMPILER_DEFAULT_PROVISIONS
from ...domain.provision import Production, ProvisionRegistration, Specification
from .. import provision as provision_context
from ..provision import (
    COMPILER_PROVISION_CACHE_PREFIX,
    add_default_provisions,
    apply_provision_overlay,
)

# *** functions

# ** function: _seeded_cache
def _seeded_cache() -> CacheContext:
    '''
    Seed the default provisions and one unrelated namespace.

    :return: The seeded cache.
    :rtype: CacheContext
    '''

    # The errors namespace must stay untouched by a provision overlay.
    cache = add_default_provisions(COMPILER_DEFAULT_PROVISIONS)(lambda: CacheContext())()
    cache.set('APP_ERROR', {'id': 'APP_ERROR'}, 'app', 'errors')
    return cache

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

# ** test: absent_overlay_writes_nothing
def test_absent_overlay_writes_nothing(
        tmp_path: Path,
        monkeypatch,
    ) -> None:
    '''
    Test that None, an empty path, and a missing path do not load.

    :param tmp_path: Temporary directory for a path that is not created.
    :type tmp_path: Path
    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: object
    '''

    # A constructed repository would mean the absent path was loaded.
    cache = _seeded_cache()
    before = cache.get('common.import_group', *COMPILER_PROVISION_CACHE_PREFIX)
    errors = cache.get('APP_ERROR', 'app', 'errors')

    def _boom(*args, **kwargs):
        '''
        Fail if the overlay constructs a repository.

        :param args: Constructor arguments.
        :param kwargs: Constructor keyword arguments.
        :return: Never returns.
        '''

        raise AssertionError('repository constructed')

    monkeypatch.setattr(provision_context, 'ProvisionConfigRepository', _boom)
    apply_provision_overlay(None)
    apply_provision_overlay(cache, '')
    apply_provision_overlay(cache, str(tmp_path / 'missing.yml'))

    # The seeded registration and the other prefix are the same objects.
    assert cache.get('common.import_group', *COMPILER_PROVISION_CACHE_PREFIX) is before
    assert cache.get('APP_ERROR', 'app', 'errors') is errors

# ** test: present_row_replaces_and_unknown_id_is_added
def test_present_row_replaces_and_unknown_id_is_added(tmp_path: Path) -> None:
    '''
    Test that a present row replaces its id and an unknown id is added.

    :param tmp_path: Temporary directory for the overlay file.
    :type tmp_path: Path
    '''

    # One seeded id is replaced. Another seeded id is omitted. A new id is added.
    cache = _seeded_cache()
    kept = cache.get('common.section_class_name', *COMPILER_PROVISION_CACHE_PREFIX)
    errors = cache.get('APP_ERROR', 'app', 'errors')
    path = tmp_path / 'overlay.yml'
    path.write_text(
        'errors:\n'
        '  OTHER: {}\n'
        'provisions:\n'
        '  common.import_group:\n'
        '    kind: specification\n'
        '    applies_to: member\n'
        "    module_path: compiler.utils.core\n"
        '    class_name: ImportGroupSpecification\n'
        '    parameters: {}\n'
        '  consumer.added:\n'
        '    kind: production\n'
        '    applies_to: import\n'
        "    module_path: compiler.utils.semantic\n"
        '    class_name: ImportProduction\n'
        '    parameters: {}\n',
        encoding='utf-8',
    )
    apply_provision_overlay(cache, str(path))
    replaced = cache.get('common.import_group', *COMPILER_PROVISION_CACHE_PREFIX)
    added = cache.get('consumer.added', *COMPILER_PROVISION_CACHE_PREFIX)

    # The replacement is the registration. The omitted seed and other prefix stay.
    assert isinstance(replaced, ProvisionRegistration)
    assert not isinstance(replaced, Specification)
    assert not isinstance(replaced, Production)
    assert replaced.applies_to == 'member'
    assert isinstance(added, ProvisionRegistration)
    assert added.id == 'consumer.added'
    assert cache.get('common.section_class_name', *COMPILER_PROVISION_CACHE_PREFIX) is kept
    assert cache.get('APP_ERROR', 'app', 'errors') is errors

# ** test: overlay_does_not_assign_prefix_or_build_cache
def test_overlay_does_not_assign_prefix_or_build_cache() -> None:
    '''
    Test that the overlay uses the existing prefix and does not seed a cache.
    '''

    # The function does not assign the prefix RFP-005 already defined.
    source = inspect.getsource(apply_provision_overlay)
    assert 'COMPILER_PROVISION_CACHE_PREFIX =' not in source
    assert 'build_cache' not in source
    module_source = Path(inspect.getfile(apply_provision_overlay)).read_text(
        encoding='utf-8',
    )
    assert module_source.count('COMPILER_PROVISION_CACHE_PREFIX:') == 1
