"""Compiler Session Blueprint Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
from tiferet.contexts.cache import CacheContext

# ** app
import compiler.blueprints as blueprints
import compiler.blueprints.core as core
import compiler.blueprints.session as session
from ..session import build_compiler_session

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

# ** test: get_feature_absent
def test_get_feature_absent() -> None:
    '''
    Test that the step handler and its unknown-step error left the blueprint.
    '''

    # The handler, the error constant, and the feature context are not here.
    assert not hasattr(session, 'get_feature')
    assert not hasattr(session, 'UNKNOWN_COMPILER_STEP')
    assert not hasattr(session, 'ASKED_STEPS')
    assert not hasattr(session, 'TiferetError')
    source = _SESSION_PATH.read_text(encoding='utf-8')
    assert 'CompilerFeatureContext' not in source
    assert 'UNKNOWN_COMPILER_STEP' not in source
    assert 'get_feature' not in source

# ** test: passed_pair_reaches_feature
def test_passed_pair_reaches_feature(monkeypatch) -> None:
    '''
    Test that a passed cache and resolver reach the session feature context.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: object
    '''

    # A passed cache and resolver skip both builders.
    cache = CacheContext()
    dependency = lambda service_id: service_id

    def fail_build_cache(*args, **kwargs):
        raise AssertionError('build_cache')

    def fail_compose(*args, **kwargs):
        raise AssertionError('compose_get_dependency')

    monkeypatch.setattr(session, 'build_cache', fail_build_cache)
    monkeypatch.setattr(session, 'compose_get_dependency', fail_compose)
    context = build_compiler_session(cache=cache, get_dependency=dependency)

    # The session holds the cache. Its feature context holds the pair.
    assert context.cache is cache
    assert context.feature.cache is cache
    assert context.feature.get_dependency is dependency
    assert not hasattr(context, 'get_feature')
    assert 'get_dependency' not in vars(context)

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
    composed = []
    real_compose = session.compose_get_dependency

    def spy_build_cache():
        calls.append('build_cache')
        return seeded

    def spy_compose(passed_cache):
        calls.append(('compose', passed_cache))
        composed.append(real_compose(passed_cache))
        return composed[-1]

    monkeypatch.setattr(core, 'build_cache', spy_build_cache)
    monkeypatch.setattr(session, 'build_cache', spy_build_cache)
    monkeypatch.setattr(session, 'compose_get_dependency', spy_compose)
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
    assert len(calls) == 2
    assert calls.count('build_cache') == 1
    assert context.cache is seeded
    assert context.feature.cache is seeded
    assert context.feature.get_dependency is composed[0]
