"""Compiler Session Blueprint Tests"""

# *** imports

# ** core
import inspect
import json
from pathlib import Path

# ** infra
import pytest
from tiferet.assets import TiferetError
from tiferet.contexts.cache import CacheContext

# ** app
import compiler.blueprints as blueprints
import compiler.blueprints.core as core
import compiler.blueprints.session as session
from ..session import (
    UNKNOWN_COMPILER_STEP,
    build_compiler_session,
    get_feature,
)
from ...contexts.feature import CompilerFeatureContext

# *** constants

# ** constant: session_path
_SESSION_PATH = Path(session.__file__)

# *** tests

# ** test: package_exports_session_builder_only
def test_package_exports_session_builder_only() -> None:
    '''
    Test that the handler and the composer stay off the package export.
    '''

    # The public names are the cache builder and the session builder.
    assert blueprints.__all__ == [
        'build_cache',
        'build_compiler_session',
    ]
    assert not hasattr(blueprints, 'get_feature')
    assert not hasattr(blueprints, 'compose_get_dependency')

# ** test: known_step_constructs_by_identity
def test_known_step_constructs_by_identity() -> None:
    '''
    Test that a known step returns a new context closed over the pair.
    '''

    # Both constructor arguments are the objects the handler closed over.
    cache = CacheContext()
    dependency = lambda service_id: service_id
    handler = get_feature(cache=cache, get_dependency=dependency)
    first = handler('scan')
    second = handler('scan')
    assert isinstance(first, CompilerFeatureContext)
    assert isinstance(second, CompilerFeatureContext)
    assert first is not second
    assert first.cache is cache
    assert second.cache is cache
    assert first.get_dependency is dependency
    assert second.get_dependency is dependency

# ** test: unknown_step_raises_before_construction
def test_unknown_step_raises_before_construction(monkeypatch) -> None:
    '''
    Test that a catalog id fails before a context is constructed.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: object
    '''

    # Construction is a failure. The raise must happen first.
    constructed = []

    class Boom:
        def __init__(self, *args, **kwargs):
            constructed.append(kwargs)
            raise AssertionError('constructed')

    monkeypatch.setattr(session, 'CompilerFeatureContext', Boom)
    handler = get_feature(cache=CacheContext(), get_dependency=lambda service_id: None)
    for step in ('scan.module', 'compile.ast'):
        with pytest.raises(TiferetError) as exc:
            handler(step)
        payload = json.loads(str(exc.value))
        assert payload['error_code'] == UNKNOWN_COMPILER_STEP
        assert payload['step'] == step
        assert payload['message'] == f'Unknown compiler step: {step!r}.'
    assert constructed == []

# ** test: handler_source_does_not_copy_framework_lookup
def test_handler_source_does_not_copy_framework_lookup() -> None:
    '''
    Test that the handler does not read or bind a feature catalog.
    '''

    # The forbidden framework body stays out of the handler source.
    source = inspect.getsource(get_feature)
    assert 'FEATURE_CACHE_PREFIX' not in source
    assert 'get_feature_evt' not in source
    assert 'from_domain' not in source

# ** test: passed_dependency_is_closed_over
def test_passed_dependency_is_closed_over(monkeypatch) -> None:
    '''
    Test that a passed resolver is not replaced.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: object
    '''

    # A passed cache and resolver skip both builders and call this handler once.
    cache = CacheContext()
    dependency = lambda service_id: service_id
    calls = []
    real_get_feature = session.get_feature

    def fail_build_cache(*args, **kwargs):
        raise AssertionError('build_cache')

    def fail_compose(*args, **kwargs):
        raise AssertionError('compose_get_dependency')

    def spy_get_feature(passed_cache, passed_dependency):
        calls.append('get_feature')
        assert passed_cache is cache
        assert passed_dependency is dependency
        return real_get_feature(passed_cache, passed_dependency)

    monkeypatch.setattr(session, 'build_cache', fail_build_cache)
    monkeypatch.setattr(session, 'compose_get_dependency', fail_compose)
    monkeypatch.setattr(session, 'get_feature', spy_get_feature)
    context = build_compiler_session(cache=cache, get_dependency=dependency)
    assert calls == ['get_feature']
    assert context.cache is cache
    step = context.get_feature('scan')
    assert step.cache is cache
    assert step.get_dependency is dependency

# ** test: omitted_cache_calls_compiler_build_cache_once
def test_omitted_cache_calls_compiler_build_cache_once(monkeypatch) -> None:
    '''
    Test that an omitted cache is built once and then composed.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: object
    '''

    # The function body does not name the framework cache or feature lookup.
    source = _SESSION_PATH.read_text(encoding='utf-8')
    assert 'tiferet.blueprints.core.build_cache' not in source
    assert 'tiferet.blueprints.core.get_feature' not in source
    assert 'from .core import build_cache' in source

    # The omitted path calls the compiler builder once and composes from that return.
    seeded = core.build_cache()
    calls = []
    real_compose = session.compose_get_dependency
    real_get_feature = session.get_feature

    def spy_build_cache():
        calls.append('build_cache')
        return seeded

    def spy_compose(passed_cache):
        calls.append(('compose', passed_cache))
        return real_compose(passed_cache)

    def spy_get_feature(passed_cache, passed_dependency):
        calls.append('get_feature')
        assert passed_cache is seeded
        return real_get_feature(passed_cache, passed_dependency)

    monkeypatch.setattr(core, 'build_cache', spy_build_cache)
    monkeypatch.setattr(session, 'build_cache', spy_build_cache)
    monkeypatch.setattr(session, 'compose_get_dependency', spy_compose)
    monkeypatch.setattr(session, 'get_feature', spy_get_feature)
    monkeypatch.setattr(
        'tiferet.blueprints.core.build_cache',
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError('tiferet build_cache')),
    )
    monkeypatch.setattr(
        'tiferet.blueprints.core.get_feature',
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError('tiferet get_feature')),
    )
    context = build_compiler_session()
    assert calls[0] == 'build_cache'
    assert calls[1][0] == 'compose'
    assert calls[1][1] is seeded
    assert calls[2] == 'get_feature'
    assert calls.count('build_cache') == 1
    assert calls.count('get_feature') == 1
    assert context.cache is seeded
