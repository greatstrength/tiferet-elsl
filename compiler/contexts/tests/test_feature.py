"""Compiler Feature Context Tests"""

# *** imports

# ** core
import ast
import inspect
import json
from pathlib import Path

# ** infra
import pytest
from tiferet.assets import TiferetError
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.core import BaseContext
from tiferet.contexts.feature import FeatureContext
from tiferet.domain.feature import Feature

# ** app
from ..feature import CompilerFeatureContext

# *** constants

# ** constant: contexts_dir
_CONTEXTS_DIR = Path(__file__).resolve().parent.parent

# ** constant: forbidden_source
_FORBIDDEN_SOURCE = (
    'run_step',
    '_run_conformance',
    '_run_codegen',
    'ASKED_STEPS',
    'ASKED_STEP_UNKNOWN',
    'COMPONENT_REQUIRED',
    'DIALECT_SERVICE_ID',
    'COMPILER_PROVISION_CACHE_PREFIX',
    'COMPILER_DEFAULT_FEATURES',
    'perform_lexical_analysis_event',
    'perform_syntactic_analysis_event',
    'perform_semantic_analysis_event',
    'check_common_conformance_event',
    '_conformance_event',
    'emit_scan_result_event',
    'emit_parse_result_event',
    'emit_semantic_result_event',
    'emit_codegen_result_event',
    'generate_code_event',
    'optimize_code_event',
    'load_from_ast_event',
    'get_feature',
    'feature.steps',
    'feature.yml',
    'fetch_next',
    'CORE_DEFAULT_FEATURES',
    'FEATURE_CACHE_PREFIX',
    'execute_asked_step',
    'execute_step',
    'model_dump',
    'build_cache',
    'apply_provision_overlay',
    'DomainEvent.handle',
)

# ** constant: forbidden_imports
_FORBIDDEN_IMPORTS = (
    'compiler.events',
    'compiler.utils',
    'compiler.assets',
    'compiler.blueprints',
    'compiler.mappers',
    'compiler.domain',
    'tiferet.di',
    'tiferet.blueprints',
    'tiferet.domain',
    'tiferet_ly',
    'yaml',
    'RequestContext',
)

# *** functions

# ** function: _event
def _event(service_id, executed, result):
    '''
    Return an object whose execute records kwargs and a sentinel.

    :param service_id: The service id being resolved.
    :type service_id: str
    :param executed: The list that records execute calls.
    :type executed: list
    :param result: The object execute returns.
    :type result: object
    :return: The fake event.
    :rtype: object
    '''

    # Record the kwargs copy so a later mutation cannot hide the handoff.
    def execute(**kwargs):
        executed.append((service_id, dict(kwargs)))
        return result

    return type('Event', (), {'execute': staticmethod(execute)})()

# ** function: _resolver
def _resolver(results=None, fail=None, none_ids=()):
    '''
    Return a resolver that records ids and does not build an event class.

    :param results: Optional sentinels keyed by service id.
    :type results: dict
    :param fail: Exception to raise on every resolve, or None.
    :type fail: Exception
    :param none_ids: Service ids that resolve to None.
    :type none_ids: tuple
    :return: The recording resolver.
    :rtype: object
    '''

    # Distinct sentinels make identity checks possible.
    resolved = []
    executed = []
    stored = dict(results or {})
    blocked = set(none_ids)

    def get_dependency(service_id):
        resolved.append(service_id)
        if fail is not None:
            raise fail
        if service_id in blocked:
            return None
        if service_id not in stored:
            stored[service_id] = object()
        return _event(service_id, executed, stored[service_id])

    get_dependency.resolved = resolved
    get_dependency.executed = executed
    get_dependency.results = stored
    return get_dependency

# ** function: _context
def _context(resolver=None, cache=None):
    '''
    Build a context around a fresh cache and resolver.

    :param resolver: The injected resolver. A recording resolver is the default.
    :type resolver: object
    :param cache: The cache to store. A fresh cache is the default.
    :type cache: CacheContext
    :return: The context, cache, and resolver.
    :rtype: tuple
    '''

    # The default resolver records every id. Tests replace it to force a failure.
    cache = cache if cache is not None else CacheContext()
    resolver = resolver if resolver is not None else _resolver()
    return CompilerFeatureContext(cache, resolver), cache, resolver

# ** function: _payload
def _payload(exc):
    '''
    Read the structured error payload.

    :param exc: The pytest exception info.
    :type exc: object
    :return: The decoded error payload.
    :rtype: dict
    '''

    # The message lives in the exception text, not a second attribute.
    return json.loads(str(exc.value))

# *** tests

# ** test: registry_omits_domain_type
def test_registry_omits_domain_type() -> None:
    '''
    Test that the context is not registered and stores the injected pair.
    '''

    # The class body does not assign a domain type, so Feature stays put.
    assert issubclass(CompilerFeatureContext, FeatureContext)
    assert 'domain_type' not in CompilerFeatureContext.__dict__
    assert BaseContext.for_domain(Feature) is FeatureContext

    # Both constructor parameters are required, and neither is replaced.
    signature = inspect.signature(CompilerFeatureContext.__init__)
    assert list(signature.parameters) == ['self', 'cache', 'get_dependency']
    for name in ('cache', 'get_dependency'):
        assert signature.parameters[name].default is inspect.Parameter.empty
    cache = CacheContext()
    resolver = _resolver()
    context = CompilerFeatureContext(cache, resolver)
    assert context.domain is None
    assert context.cache is cache
    assert context.get_dependency is resolver

    # The step runner and its helpers are gone.
    for name in ('run_step', 'execute_asked_step', '_resolve_and_execute', '_run_conformance', '_run_codegen'):
        assert not hasattr(CompilerFeatureContext, name)

# ** test: resolve_and_execute_signature
def test_resolve_and_execute_signature() -> None:
    '''
    Test that the execution method takes a service id and event kwargs only.
    '''

    # No step parameter, no request, and no positional flags.
    signature = inspect.signature(CompilerFeatureContext.resolve_and_execute)
    assert list(signature.parameters) == ['self', 'service_id', 'event_kwargs']
    assert signature.parameters['event_kwargs'].kind == inspect.Parameter.VAR_KEYWORD
    assert 'step' not in signature.parameters
    assert not any(
        parameter.kind == inspect.Parameter.VAR_POSITIONAL
        for parameter in signature.parameters.values()
    )

# ** test: resolve_and_execute_calls_execute
def test_resolve_and_execute_calls_execute() -> None:
    '''
    Test that one id is resolved with no flags and its execute result returned.
    '''

    # The resolver sees the id only. Execute sees the kwargs only.
    context, _, resolver = _context()
    result = context.resolve_and_execute('perform_lexical_analysis_event', source_file='a.py')
    assert resolver.resolved == ['perform_lexical_analysis_event']
    assert resolver.executed == [
        ('perform_lexical_analysis_event', {'source_file': 'a.py'}),
    ]
    assert result is resolver.results['perform_lexical_analysis_event']

    # The id is not branched on. Any id is resolved the same way.
    context.resolve_and_execute('any_service_event')
    assert resolver.resolved[-1] == 'any_service_event'
    assert resolver.executed[-1] == ('any_service_event', {})

# ** test: missing_resolver_raises_before_resolve
def test_missing_resolver_raises_before_resolve() -> None:
    '''
    Test that a None resolver is refused before a resolve call.
    '''

    # Calling None would be a different error. This one is named.
    context = CompilerFeatureContext(CacheContext(), None)
    with pytest.raises(TiferetError) as exc:
        context.resolve_and_execute('perform_lexical_analysis_event', source_file='a.py')
    assert exc.value.error_code == 'RESOLVER_REQUIRED'
    assert _payload(exc)['message'] == 'CompilerFeatureContext requires get_dependency.'

# ** test: failed_resolve_does_not_execute
def test_failed_resolve_does_not_execute() -> None:
    '''
    Test that a raising or empty resolve does not call execute.
    '''

    # A raised resolve names the id only and does not call execute.
    raising = _resolver(fail=RuntimeError('missing'))
    context, _, _ = _context(resolver=raising)
    with pytest.raises(TiferetError) as exc:
        context.resolve_and_execute('perform_lexical_analysis_event', source_file='a.py')
    assert exc.value.error_code == 'EVENT_NOT_RESOLVED'
    assert exc.value.kwargs == {'service_id': 'perform_lexical_analysis_event'}
    assert 'step' not in exc.value.kwargs
    assert raising.executed == []
    assert _payload(exc)['message'] == 'Failed to resolve perform_lexical_analysis_event.'

    # A None resolve is the same refusal, and that id's execute is not called.
    empty = _resolver(none_ids=('perform_lexical_analysis_event',))
    empty_context, _, _ = _context(resolver=empty)
    with pytest.raises(TiferetError) as exc:
        empty_context.resolve_and_execute('perform_lexical_analysis_event', source_file='a.py')
    assert exc.value.error_code == 'EVENT_NOT_RESOLVED'
    assert exc.value.kwargs == {'service_id': 'perform_lexical_analysis_event'}
    assert empty.resolved == ['perform_lexical_analysis_event']
    assert empty.executed == []
    assert _payload(exc)['message'] == 'Failed to resolve perform_lexical_analysis_event.'

# ** test: inherited_lookup_refuses
def test_inherited_lookup_refuses(monkeypatch) -> None:
    '''
    Test that the four inherited lookups raise and do not delegate.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: object
    '''

    # A parent call would append here. The refusal must not.
    called = []

    def _boom(*args, **kwargs):
        '''
        Record a delegated parent call.

        :param args: Parent arguments.
        :type args: tuple
        :param kwargs: Parent keyword arguments.
        :type kwargs: dict
        :return: Never returns.
        :rtype: None
        '''

        called.append((args, kwargs))
        raise AssertionError('parent called')

    monkeypatch.setattr(FeatureContext, 'execute_feature', _boom)
    monkeypatch.setattr(FeatureContext, 'resolve_feature_steps', _boom)
    monkeypatch.setattr(FeatureContext, 'resolve_step_event', _boom)
    monkeypatch.setattr(FeatureContext, 'from_domain', _boom)
    context, _, resolver = _context()
    for method in (
        'execute_feature',
        'resolve_feature_steps',
        'resolve_step_event',
        'from_domain',
    ):
        with pytest.raises(TiferetError) as exc:
            getattr(context, method)()
        assert exc.value.error_code == 'COMPILER_FEATURE_LOOKUP_REFUSED'
        assert exc.value.kwargs['method'] == method
        assert _payload(exc)['message'] == (
            'CompilerFeatureContext does not resolve a feature. '
            f'Refused {method}.'
        )
    assert called == []
    assert resolver.resolved == []

# ** test: module_source_forbidden_strings
def test_module_source_forbidden_strings() -> None:
    '''
    Test that the module source does not name a feature walk or a forbidden import.
    '''

    # The forbidden names are absent from the module text.
    source = (_CONTEXTS_DIR / 'feature.py').read_text(encoding='utf-8')
    for forbidden in _FORBIDDEN_SOURCE:
        assert forbidden not in source

    # Import lines do not name the closed packages.
    tree = ast.parse(source)
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or '')
            imported.extend(alias.name for alias in node.names)
    for forbidden in _FORBIDDEN_IMPORTS:
        assert forbidden not in imported
        assert not any(name.startswith(forbidden + '.') for name in imported)

    # The feature context does not import the session.
    assert 'session' not in imported
    assert not any(name.endswith('.session') for name in imported)

    # The package marker imports neither context module.
    init_tree = ast.parse((_CONTEXTS_DIR / '__init__.py').read_text(encoding='utf-8'))
    init_names = []
    for node in ast.walk(init_tree):
        if isinstance(node, ast.Import):
            init_names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            init_names.append(node.module or '')
            init_names.extend(alias.name for alias in node.names)
    assert 'feature' not in init_names
    assert 'session' not in init_names
