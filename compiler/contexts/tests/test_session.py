"""Compiler Session Context Tests"""

# *** imports

# ** core
import inspect
from pathlib import Path

# ** infra
from tiferet.contexts.app import AppSessionContext
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.core import BaseContext
from tiferet.domain import AppSession

# ** app
from ..session import CompilerAppSessionContext

# *** constants

# ** constant: session_path
_SESSION_PATH = Path(__file__).resolve().parent.parent / 'session.py'

# ** constant: hub_handlers
_HUB_HANDLERS = (
    '_build_logger',
    '_execute_feature',
    '_create_request',
    '_raise_error',
    '_build_response',
)

# *** functions

# ** function: _recording_handler
def _recording_handler(calls, result=None):
    '''
    Return a handler that records the step and a run_step call.

    :param calls: The list that records handler and run_step calls.
    :type calls: list
    :param result: The object run_step returns.
    :type result: object
    :return: The recording handler.
    :rtype: object
    '''

    # Record the kwargs copy so a later mutation cannot hide the handoff.
    class Step:
        def run_step(self, step, **kwargs):
            calls.append(('run_step', step, dict(kwargs)))
            return result

    def get_feature(step):
        calls.append(('handler', step))
        return Step()

    return get_feature

# *** tests

# ** test: registry_omits_domain_type
def test_registry_omits_domain_type() -> None:
    '''
    Test that the session is not registered over AppSession.
    '''

    # The class body does not assign a domain type, so AppSession stays put.
    assert 'domain_type' not in CompilerAppSessionContext.__dict__
    assert BaseContext.for_domain(AppSession) is AppSessionContext

# ** test: stores_cache_and_handler_only
def test_stores_cache_and_handler_only() -> None:
    '''
    Test that the constructor stores the injected pair and nothing else.
    '''

    # Both constructor parameters are required.
    signature = inspect.signature(CompilerAppSessionContext.__init__)
    assert list(signature.parameters) == ['self', 'cache', 'get_feature']
    for name in ('cache', 'get_feature'):
        assert signature.parameters[name].default is inspect.Parameter.empty

    # Both objects are stored by identity. The domain stays unbound.
    cache = CacheContext()
    handler = lambda step: None
    session = CompilerAppSessionContext(cache=cache, get_feature=handler)
    assert session.cache is cache
    assert session.get_feature is handler
    assert session.domain is None

    # The resolver and the five hub handlers are not attributes.
    assert not hasattr(session, 'get_dependency')
    for name in _HUB_HANDLERS:
        assert not hasattr(session, name)

# ** test: run_calls_handler_then_run_step
def test_run_calls_handler_then_run_step() -> None:
    '''
    Test that run asks the handler and returns the run_step result.
    '''

    # The session source does not name the feature context class.
    source = _SESSION_PATH.read_text(encoding='utf-8')
    assert 'CompilerFeatureContext' not in source
    assert 'super(' not in inspect.getsource(CompilerAppSessionContext.run)
    assert 'super(' not in inspect.getsource(CompilerAppSessionContext.execute_feature)

    # run calls the handler with the asked step, then run_step with the same step.
    calls = []
    result = object()
    session = CompilerAppSessionContext(
        cache=CacheContext(),
        get_feature=_recording_handler(calls, result=result),
    )
    assert session.run('scan', source_file='a.py') is result
    assert calls == [
        ('handler', 'scan'),
        ('run_step', 'scan', {'source_file': 'a.py'}),
    ]

# ** test: unknown_step_is_not_the_session_raise
def test_unknown_step_is_not_the_session_raise() -> None:
    '''
    Test that a catalog id is passed to the handler and not rejected here.
    '''

    # The session does not raise the handler's unknown-step error.
    calls = []
    session = CompilerAppSessionContext(
        cache=CacheContext(),
        get_feature=_recording_handler(calls, result='kept'),
    )
    assert session.run('scan.module') == 'kept'
    assert calls[0] == ('handler', 'scan.module')
    assert 'UNKNOWN_COMPILER_STEP' not in _SESSION_PATH.read_text(encoding='utf-8')
