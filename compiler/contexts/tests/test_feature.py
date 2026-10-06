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
from ..feature import (
    ASKED_STEPS,
    DIALECT_SERVICE_ID,
    CompilerFeatureContext,
)
from ..provision import COMPILER_PROVISION_CACHE_PREFIX

# *** constants

# ** constant: contexts_dir
_CONTEXTS_DIR = Path(__file__).resolve().parent.parent

# ** constant: forbidden_source
_FORBIDDEN_SOURCE = (
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

# ** function: _kwargs_for
def _kwargs_for(resolver, service_id):
    '''
    Return the kwargs recorded for one execute.

    :param resolver: The recording resolver.
    :type resolver: object
    :param service_id: The service id whose execute kwargs are needed.
    :type service_id: str
    :return: The recorded kwargs.
    :rtype: dict
    '''

    # One ask resolves each id once.
    return next(kwargs for sid, kwargs in resolver.executed if sid == service_id)

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

    # The public ask has no request parameter and no positional flags.
    run_step = inspect.signature(CompilerFeatureContext.run_step)
    assert list(run_step.parameters) == ['self', 'step', 'kwargs']
    assert 'request' not in run_step.parameters
    assert not any(
        parameter.kind == inspect.Parameter.VAR_POSITIONAL
        for parameter in run_step.parameters.values()
    )
    assert not hasattr(CompilerFeatureContext, 'execute_asked_step')

# ** test: asked_steps_and_dialect_ids
def test_asked_steps_and_dialect_ids() -> None:
    '''
    Test the five asked strings and the ten dialect service ids.
    '''

    # Catalog ids are not asks. The hyphen is the spelling.
    assert ASKED_STEPS == (
        'scan',
        'parse',
        'semantic',
        'compile',
        'compile-from-ast',
    )

    # contexts maps to the singular service id, not the class name.
    assert DIALECT_SERVICE_ID == {
        'assets': 'check_asset_conformance_event',
        'blueprints': 'check_blueprints_conformance_event',
        'contexts': 'check_context_conformance_event',
        'di': 'check_di_conformance_event',
        'domain': 'check_domain_conformance_event',
        'events': 'check_event_conformance_event',
        'interfaces': 'check_interface_conformance_event',
        'mappers': 'check_mapper_conformance_event',
        'repos': 'check_repos_conformance_event',
        'utils': 'check_utils_conformance_event',
    }

# ** test: each_component_resolves_one_dialect
def test_each_component_resolves_one_dialect() -> None:
    '''
    Test that each component string resolves only its dialect id.
    '''

    # The other nine ids stay unresolved, including the plural contexts name.
    for component, service_id in DIALECT_SERVICE_ID.items():
        resolver = _resolver()
        context, _, _ = _context(resolver=resolver)
        context.run_step('semantic', component=component, source_file='a.py')
        dialects = [
            sid for sid in resolver.resolved
            if sid != 'check_common_conformance_event' and sid.startswith('check_')
        ]
        assert dialects == [service_id]
        assert 'check_contexts_conformance_event' not in resolver.resolved

# ** test: scan_passes_lexical_return
def test_scan_passes_lexical_return() -> None:
    '''
    Test that scan resolves two ids and emits the lexical return.
    '''

    # A passed component is not a scan argument.
    context, cache, resolver = _context()
    result = context.run_step(
        'scan',
        source_file='a.py',
        component='domain',
        output='out.yml',
    )

    # Only the two scan ids run, in order.
    assert resolver.resolved == [
        'perform_lexical_analysis_event',
        'emit_scan_result_event',
    ]
    lexical = resolver.results['perform_lexical_analysis_event']
    emit = _kwargs_for(resolver, 'emit_scan_result_event')
    assert emit['tokens'] is lexical
    assert emit['source_file'] == 'a.py'
    assert emit['output'] == 'out.yml'
    assert 'component' not in emit
    assert 'cache' not in emit
    assert 'provision_prefix' not in emit
    assert result is resolver.results['emit_scan_result_event']
    assert result is not lexical
    assert context.cache is cache

# ** test: parse_passes_syntactic_return
def test_parse_passes_syntactic_return() -> None:
    '''
    Test that parse skips the scan emit and can return an empty string.
    '''

    # The empty emit sentinel must remain the return, not a replacement.
    resolver = _resolver(results={'emit_parse_result_event': ''})
    context, _, _ = _context(resolver=resolver)
    result = context.run_step(
        'parse',
        source_file='a.py',
        include_tokens=True,
        extract='name',
    )

    # Syntactic tokens are the lexical return. The emit ast is the syntactic return.
    assert resolver.resolved == [
        'perform_lexical_analysis_event',
        'perform_syntactic_analysis_event',
        'emit_parse_result_event',
    ]
    assert 'emit_scan_result_event' not in resolver.resolved
    lexical = resolver.results['perform_lexical_analysis_event']
    syntactic = resolver.results['perform_syntactic_analysis_event']
    assert _kwargs_for(resolver, 'perform_syntactic_analysis_event')['tokens'] is lexical
    emit = _kwargs_for(resolver, 'emit_parse_result_event')
    assert emit['ast'] is syntactic
    assert emit['tokens'] is lexical
    assert emit['include_tokens'] is True
    assert emit['extract'] == 'name'
    assert result == ''
    assert result is resolver.results['emit_parse_result_event']

# ** test: semantic_passes_analysis_returns
def test_semantic_passes_analysis_returns() -> None:
    '''
    Test that semantic hands the syntactic return forward and emits once.
    '''

    # A caller prefix must not replace the imported constant.
    context, cache, resolver = _context()
    result = context.run_step(
        'semantic',
        component='domain',
        source_file='a.py',
        provision_prefix=('not', 'the', 'prefix'),
        feature_id='semantic.module',
        request=object(),
        marker='x',
    )

    # Earlier emits do not run. Only the domain dialect is resolved.
    assert resolver.resolved == [
        'perform_lexical_analysis_event',
        'perform_syntactic_analysis_event',
        'perform_semantic_analysis_event',
        'check_common_conformance_event',
        'check_domain_conformance_event',
        'emit_semantic_result_event',
    ]
    assert 'emit_scan_result_event' not in resolver.resolved
    assert 'emit_parse_result_event' not in resolver.resolved
    syntactic = resolver.results['perform_syntactic_analysis_event']
    semantic = resolver.results['perform_semantic_analysis_event']
    common = resolver.results['check_common_conformance_event']
    dialect = resolver.results['check_domain_conformance_event']

    # Analysis and both checks see that ast, the cache, and the one prefix.
    analysis = _kwargs_for(resolver, 'perform_semantic_analysis_event')
    assert analysis['ast'] is syntactic
    assert analysis['cache'] is cache
    assert analysis['provision_prefix'] is COMPILER_PROVISION_CACHE_PREFIX
    assert 'source_file' not in analysis
    common_kwargs = _kwargs_for(resolver, 'check_common_conformance_event')
    assert common_kwargs['ast'] is syntactic
    assert common_kwargs['semantic'] is semantic
    assert common_kwargs['cache'] is cache
    assert common_kwargs['provision_prefix'] is COMPILER_PROVISION_CACHE_PREFIX
    dialect_kwargs = _kwargs_for(resolver, 'check_domain_conformance_event')
    assert dialect_kwargs['findings'] is common
    assert dialect_kwargs['ast'] is syntactic
    assert dialect_kwargs['cache'] is cache

    # The emit receives the syntactic return, not a dump, and no include_ast.
    emit = _kwargs_for(resolver, 'emit_semantic_result_event')
    assert emit['ast'] is syntactic
    assert emit['semantic'] is semantic
    assert emit['findings'] is dialect
    assert 'include_ast' not in emit
    assert 'feature_id' not in emit
    assert 'request' not in emit
    assert 'marker' not in emit
    assert 'step' not in emit
    assert result is resolver.results['emit_semantic_result_event']

# ** test: semantic_forwards_include_ast_when_supplied
def test_semantic_forwards_include_ast_when_supplied() -> None:
    '''
    Test that include_ast is forwarded only on the semantic emit.
    '''

    # The flag does not replace the syntactic object.
    context, _, resolver = _context()
    context.run_step('semantic', component='domain', include_ast=False, source_file='a.py')
    emit = _kwargs_for(resolver, 'emit_semantic_result_event')
    assert emit['include_ast'] is False
    assert emit['ast'] is resolver.results['perform_syntactic_analysis_event']

# ** test: compile_continues_after_findings
def test_compile_continues_after_findings() -> None:
    '''
    Test that compile skips earlier emits and still generates.
    '''

    # A non-empty findings sentinel must not skip the codegen tail.
    resolver = _resolver(results={'check_utils_conformance_event': ['kept']})
    context, _, _ = _context(resolver=resolver)
    result = context.run_step('compile', component='utils', source_file='a.py')

    # The three earlier emits stay unresolved.
    assert 'emit_scan_result_event' not in resolver.resolved
    assert 'emit_parse_result_event' not in resolver.resolved
    assert 'emit_semantic_result_event' not in resolver.resolved
    assert resolver.resolved == [
        'perform_lexical_analysis_event',
        'perform_syntactic_analysis_event',
        'perform_semantic_analysis_event',
        'check_common_conformance_event',
        'check_utils_conformance_event',
        'generate_code_event',
        'optimize_code_event',
        'emit_codegen_result_event',
    ]
    syntactic = resolver.results['perform_syntactic_analysis_event']
    generated = _kwargs_for(resolver, 'generate_code_event')
    assert generated['ast'] is syntactic
    assert generated['component'] == 'utils'
    assert generated['component'] != 'events'
    assert 'cache' not in generated
    optimized = _kwargs_for(resolver, 'optimize_code_event')
    assert 'O' not in optimized
    assert optimized['codegen'] is resolver.results['generate_code_event']
    emitted = _kwargs_for(resolver, 'emit_codegen_result_event')
    assert emitted['codegen'] is resolver.results['optimize_code_event']
    assert result is resolver.results['emit_codegen_result_event']

    # The asked component is passed through, including events.
    events = _resolver()
    events_context, _, _ = _context(resolver=events)
    events_context.run_step('compile', component='events', optimization='O1')
    assert _kwargs_for(events, 'generate_code_event')['component'] == 'events'
    assert _kwargs_for(events, 'optimize_code_event')['O'] == 'O1'
    assert 'optimization' not in _kwargs_for(events, 'optimize_code_event')

# ** test: compile_from_ast_uses_load_return
def test_compile_from_ast_uses_load_return() -> None:
    '''
    Test that compile-from-ast loads, then analyzes, and does not reparse.
    '''

    # The load return is the ast for analysis and for generate.
    context, _, resolver = _context()
    context.run_step('compile-from-ast', component='assets', source_file='saved.json')

    # No lexical event, no syntactic event, and no semantic emit.
    assert 'perform_lexical_analysis_event' not in resolver.resolved
    assert 'perform_syntactic_analysis_event' not in resolver.resolved
    assert 'emit_semantic_result_event' not in resolver.resolved
    assert resolver.resolved[0] == 'load_from_ast_event'
    loaded = resolver.results['load_from_ast_event']
    assert _kwargs_for(resolver, 'perform_semantic_analysis_event')['ast'] is loaded
    assert _kwargs_for(resolver, 'generate_code_event')['ast'] is loaded
    assert _kwargs_for(resolver, 'generate_code_event')['component'] == 'assets'
    assert _kwargs_for(resolver, 'check_common_conformance_event')['ast'] is loaded

# ** test: unknown_step_does_not_resolve
def test_unknown_step_does_not_resolve() -> None:
    '''
    Test that a miss raises before the resolver is called.
    '''

    # Catalog ids, a blank, and None are not asks. Do not translate them.
    context, _, resolver = _context()
    for step in ('compile.ast', 'scan.module', '', None, 'Scan', 'compile_from_ast'):
        with pytest.raises(TiferetError) as exc:
            context.run_step(step)
        assert exc.value.error_code == 'ASKED_STEP_UNKNOWN'
        assert exc.value.kwargs['step'] == step
        assert _payload(exc)['message'] == (
            f"Asked step '{step}' is not one of: "
            'scan, parse, semantic, compile, compile-from-ast.'
        )
    assert resolver.resolved == []

# ** test: component_required_does_not_resolve
def test_component_required_does_not_resolve() -> None:
    '''
    Test that a bad component fails before the resolver is called.
    '''

    # A missing key is reported as None. An empty string is not stripped.
    context, _, resolver = _context()
    cases = (
        ('semantic', {}, None),
        ('compile', {'component': ''}, ''),
        ('compile-from-ast', {'component': 'widget'}, 'widget'),
    )
    for step, kwargs, component in cases:
        with pytest.raises(TiferetError) as exc:
            context.run_step(step, **kwargs)
        assert exc.value.error_code == 'COMPONENT_REQUIRED'
        assert exc.value.kwargs['step'] == step
        assert exc.value.kwargs['component'] == component
        assert _payload(exc)['message'] == (
            f"Asked step '{step}' requires one of the ten component strings. "
            f'Got {component}.'
        )
    assert resolver.resolved == []

# ** test: scan_and_parse_do_not_require_component
def test_scan_and_parse_do_not_require_component() -> None:
    '''
    Test that scan and parse run when no component was passed.
    '''

    # A missing component is not an error on these two asks.
    context, _, resolver = _context()
    context.run_step('scan')
    context.run_step('parse')
    assert 'perform_lexical_analysis_event' in resolver.resolved

# ** test: missing_resolver_raises_before_resolve
def test_missing_resolver_raises_before_resolve() -> None:
    '''
    Test that a None resolver is refused before a resolve call.
    '''

    # Calling None would be a different error. This one is named.
    context = CompilerFeatureContext(CacheContext(), None)
    with pytest.raises(TiferetError) as exc:
        context.run_step('scan', source_file='a.py')
    assert exc.value.error_code == 'RESOLVER_REQUIRED'
    assert _payload(exc)['message'] == 'CompilerFeatureContext requires get_dependency.'

# ** test: failed_resolve_does_not_execute
def test_failed_resolve_does_not_execute() -> None:
    '''
    Test that a raising or empty resolve does not call execute.
    '''

    # A raised resolve names the id and does not call execute.
    raising = _resolver(fail=RuntimeError('missing'))
    context, _, _ = _context(resolver=raising)
    with pytest.raises(TiferetError) as exc:
        context.run_step('scan', source_file='a.py')
    assert exc.value.error_code == 'EVENT_NOT_RESOLVED'
    assert exc.value.kwargs['service_id'] == 'perform_lexical_analysis_event'
    assert exc.value.kwargs['step'] == 'scan'
    assert raising.executed == []
    assert _payload(exc)['message'] == (
        "Failed to resolve perform_lexical_analysis_event for asked step 'scan'."
    )

    # A None resolve is the same refusal, and that id's execute is not called.
    empty = _resolver(none_ids=('perform_lexical_analysis_event',))
    empty_context, _, _ = _context(resolver=empty)
    with pytest.raises(TiferetError) as exc:
        empty_context.run_step('parse', source_file='a.py')
    assert exc.value.error_code == 'EVENT_NOT_RESOLVED'
    assert exc.value.kwargs['service_id'] == 'perform_lexical_analysis_event'
    assert empty.executed == []

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

# ** test: module_source_refuses_feature_walk
def test_module_source_refuses_feature_walk() -> None:
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

    # The package marker does not import this module.
    init_tree = ast.parse((_CONTEXTS_DIR / '__init__.py').read_text(encoding='utf-8'))
    init_names = []
    for node in ast.walk(init_tree):
        if isinstance(node, ast.Import):
            init_names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            init_names.append(node.module or '')
            init_names.extend(alias.name for alias in node.names)
    assert 'feature' not in init_names
