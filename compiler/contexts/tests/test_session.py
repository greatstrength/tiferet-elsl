"""Compiler Session Context Tests"""

# *** imports

# ** core
import inspect
import json
from pathlib import Path

# ** infra
import pytest
from tiferet.assets import TiferetError
from tiferet.contexts.app import AppSessionContext
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.core import BaseContext
from tiferet.domain import AppSession

# ** app
from .. import feature as feature_module
from .. import session as session_module
from ..feature import CompilerFeatureContext
from ..provision import COMPILER_PROVISION_CACHE_PREFIX
from ..session import (
    ASKED_METHODS,
    DIALECT_SERVICE_ID,
    UNKNOWN_COMPILER_STEP,
    CompilerAppSessionContext,
)

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

# ** constant: nine_methods
_NINE_METHODS = (
    'lexical_analysis',
    'syntactic_analysis',
    'conformance',
    'distillation',
    'scan',
    'parse',
    'semantic',
    'compile',
    'compile_from_ast',
)

# ** constant: forbidden_source
_FORBIDDEN_SOURCE = (
    'get_feature',
    'run_step',
    'feature.steps',
    'feature.yml',
    'COMPILER_DEFAULT_FEATURES',
)

# ** constant: lexical
_LEXICAL = 'perform_lexical_analysis_event'

# ** constant: syntactic
_SYNTACTIC = 'perform_syntactic_analysis_event'

# ** constant: analysis
_ANALYSIS = 'perform_semantic_analysis_event'

# ** constant: common
_COMMON = 'check_common_conformance_event'

# ** constant: codegen_tail
_CODEGEN_TAIL = (
    'generate_code_event',
    'optimize_code_event',
    'emit_codegen_result_event',
)

# ** constant: resolve_orders
_RESOLVE_ORDERS = (
    ('scan', {}, [
        _LEXICAL,
        'emit_scan_result_event',
    ]),
    ('parse', {}, [
        _LEXICAL,
        _SYNTACTIC,
        'emit_parse_result_event',
    ]),
    ('semantic', {'component': 'domain'}, [
        _LEXICAL,
        _SYNTACTIC,
        _ANALYSIS,
        _COMMON,
        'check_domain_conformance_event',
        'emit_semantic_result_event',
    ]),
    ('compile', {'component': 'utils'}, [
        _LEXICAL,
        _SYNTACTIC,
        _ANALYSIS,
        _COMMON,
        'check_utils_conformance_event',
        *_CODEGEN_TAIL,
    ]),
    ('compile-from-ast', {'component': 'assets'}, [
        'load_from_ast_event',
        _ANALYSIS,
        _COMMON,
        'check_asset_conformance_event',
        *_CODEGEN_TAIL,
    ]),
)

# ** constant: unknown_steps
_UNKNOWN_STEPS = (
    'compile.ast',
    'scan.module',
    '',
    None,
    'Scan',
    'compile_from_ast',
    'compile/ast',
    'module',
    'ast',
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
def _resolver(results=None):
    '''
    Return a resolver that records ids and does not build an event class.

    :param results: Optional sentinels keyed by service id.
    :type results: dict
    :return: The recording resolver.
    :rtype: object
    '''

    # Distinct sentinels make identity checks possible.
    resolved = []
    executed = []
    stored = dict(results or {})

    def get_dependency(service_id):
        resolved.append(service_id)
        if service_id not in stored:
            stored[service_id] = object()
        return _event(service_id, executed, stored[service_id])

    get_dependency.resolved = resolved
    get_dependency.executed = executed
    get_dependency.results = stored
    return get_dependency

# ** function: _session
def _session(resolver=None, cache=None):
    '''
    Build a session around a fresh cache and a recording resolver.

    :param resolver: The injected resolver. A recording resolver is the default.
    :type resolver: object
    :param cache: The cache to store. A fresh cache is the default.
    :type cache: CacheContext
    :return: The session, cache, and resolver.
    :rtype: tuple
    '''

    # The default resolver records every id.
    cache = cache if cache is not None else CacheContext()
    resolver = resolver if resolver is not None else _resolver()
    session = CompilerAppSessionContext(cache=cache, get_dependency=resolver)
    return session, cache, resolver

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

# ** function: _forbid
def _forbid(session, *names):
    '''
    Replace session methods with stubs that raise when called.

    :param session: The session whose instance attributes are replaced.
    :type session: CompilerAppSessionContext
    :param names: The method names that must not be called.
    :type names: tuple
    :return: The list that records forbidden calls.
    :rtype: list
    '''

    # An instance attribute shadows the method for this session only.
    called = []
    for name in names:
        def stub(*args, _name=name, **kwargs):
            called.append(_name)
            raise AssertionError(f'{_name} called')
        setattr(session, name, stub)
    return called

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
    Test that the session is not registered over AppSession.
    '''

    # The class body does not assign a domain type, so AppSession stays put.
    assert 'domain_type' not in CompilerAppSessionContext.__dict__
    assert BaseContext.for_domain(AppSession) is AppSessionContext
    session, _, _ = _session()
    assert session.domain is None

# ** test: defines_nine_methods
def test_defines_nine_methods() -> None:
    '''
    Test that the session defines the nine workflow methods and no run_step.
    '''

    # Each name is defined on this class, not inherited.
    for name in _NINE_METHODS:
        assert name in CompilerAppSessionContext.__dict__
        assert callable(CompilerAppSessionContext.__dict__[name])

    # The old step runner is gone from the session and the feature context.
    session, _, _ = _session()
    assert 'run_step' not in dir(session)
    assert 'run_step' not in dir(session.feature)

# ** test: constructor_builds_one_feature
def test_constructor_builds_one_feature() -> None:
    '''
    Test that the constructor builds one feature context and stores no resolver.
    '''

    # Both constructor parameters are required.
    signature = inspect.signature(CompilerAppSessionContext.__init__)
    assert list(signature.parameters) == ['self', 'cache', 'get_dependency']
    for name in ('cache', 'get_dependency'):
        assert signature.parameters[name].default is inspect.Parameter.empty

    # The feature context holds that cache and that callable.
    cache = CacheContext()
    resolver = _resolver()
    session = CompilerAppSessionContext(cache=cache, get_dependency=resolver)
    assert session.cache is cache
    assert type(session.feature) is CompilerFeatureContext
    assert session.feature.cache is cache
    assert session.feature.get_dependency is resolver

    # The session stores neither the handler nor the resolver, nor hub handlers.
    assert 'get_dependency' not in vars(session)
    assert not hasattr(session, 'get_dependency')
    assert not hasattr(session, 'get_feature')
    for name in _HUB_HANDLERS:
        assert not hasattr(session, name)

    # Two runs share the one feature object.
    feature = session.feature
    session.run('scan', source_file='a.py')
    assert session.feature is feature
    session.run('parse', source_file='a.py')
    assert session.feature is feature

# ** test: asked_methods_and_dialect_ids
def test_asked_methods_and_dialect_ids() -> None:
    '''
    Test the five asked strings and the ten dialect service ids.
    '''

    # The hyphen is the asked spelling. The method name uses an underscore.
    assert list(ASKED_METHODS.items()) == [
        ('scan', 'scan'),
        ('parse', 'parse'),
        ('semantic', 'semantic'),
        ('compile', 'compile'),
        ('compile-from-ast', 'compile_from_ast'),
    ]

    # contexts maps to the singular service id, not the class name.
    assert list(DIALECT_SERVICE_ID.items()) == [
        ('assets', 'check_asset_conformance_event'),
        ('blueprints', 'check_blueprints_conformance_event'),
        ('contexts', 'check_context_conformance_event'),
        ('di', 'check_di_conformance_event'),
        ('domain', 'check_domain_conformance_event'),
        ('events', 'check_event_conformance_event'),
        ('interfaces', 'check_interface_conformance_event'),
        ('mappers', 'check_mapper_conformance_event'),
        ('repos', 'check_repos_conformance_event'),
        ('utils', 'check_utils_conformance_event'),
    ]

# ** test: asked_methods_map
def test_asked_methods_map() -> None:
    '''
    Test that the one map is the dispatch table and no step tuple remains.
    '''

    # Each value names a method on the session.
    for method in ASKED_METHODS.values():
        assert method in CompilerAppSessionContext.__dict__

    # No second tuple exists on either module or either class.
    assert not hasattr(session_module, 'ASKED_STEPS')
    assert not hasattr(feature_module, 'ASKED_STEPS')
    assert not hasattr(CompilerAppSessionContext, 'ASKED_STEPS')
    assert not hasattr(CompilerFeatureContext, 'ASKED_STEPS')

    # The old unknown-step constant is withdrawn.
    assert not hasattr(feature_module, 'ASKED_STEP_UNKNOWN_ID')
    assert not hasattr(session_module, 'ASKED_STEP_UNKNOWN_ID')

# ** test: run_returns_dispatch
def test_run_returns_dispatch() -> None:
    '''
    Test that run returns the mapped method result for each asked string.
    '''

    # A stub per method returns a distinct sentinel and records its kwargs.
    for step, method in ASKED_METHODS.items():
        session, _, resolver = _session()
        sentinel = object()
        calls = []

        def stub(**kwargs):
            calls.append(dict(kwargs))
            return sentinel

        setattr(session, method, stub)
        assert session.run(step, component='domain', source_file='a.py') is sentinel
        assert session.execute_feature(step, source_file='b.py') is sentinel
        assert calls == [
            {'component': 'domain', 'source_file': 'a.py'},
            {'source_file': 'b.py'},
        ]
        assert resolver.resolved == []

# ** test: no_super_in_run_or_dispatch
def test_no_super_in_run_or_dispatch() -> None:
    '''
    Test that run and execute_feature do not call the hub implementation.
    '''

    # Neither source calls super, and run delegates to execute_feature.
    run_source = inspect.getsource(CompilerAppSessionContext.run)
    dispatch_source = inspect.getsource(CompilerAppSessionContext.execute_feature)
    assert 'super(' not in run_source
    assert 'super(' not in dispatch_source
    assert 'self.execute_feature(step, **kwargs)' in run_source
    assert 'ASKED_METHODS' in dispatch_source
    assert 'self.feature.execute_feature' not in dispatch_source

    # Neither takes a feature id, a request, or positional flags.
    for method in (CompilerAppSessionContext.run, CompilerAppSessionContext.execute_feature):
        assert list(inspect.signature(method).parameters) == ['self', 'step', 'kwargs']

# ** test: resolve_order_per_step
@pytest.mark.parametrize('step, kwargs, expected', _RESOLVE_ORDERS)
def test_resolve_order_per_step(step, kwargs, expected) -> None:
    '''
    Test that each asked string resolves the same ids, in order, as before.

    :param step: The asked string.
    :type step: str
    :param kwargs: The caller keys for that ask.
    :type kwargs: dict
    :param expected: The ordered service ids.
    :type expected: list
    '''

    # The recorded resolve list is the sequence, with no extra or repeated id.
    session, _, resolver = _session()
    session.run(step, source_file='a.py', **kwargs)
    assert resolver.resolved == expected

# ** test: each_component_resolves_one_dialect
def test_each_component_resolves_one_dialect() -> None:
    '''
    Test that each component string resolves only its dialect id.
    '''

    # The other nine ids stay unresolved, including the plural contexts name.
    for component, service_id in DIALECT_SERVICE_ID.items():
        session, _, resolver = _session()
        session.run('semantic', component=component, source_file='a.py')
        dialects = [
            sid for sid in resolver.resolved
            if sid != _COMMON and sid.startswith('check_')
        ]
        assert dialects == [service_id]
        assert 'check_contexts_conformance_event' not in resolver.resolved

# ** test: scan_hands_lexical_return
def test_scan_hands_lexical_return() -> None:
    '''
    Test that scan emits the lexical return and does not forward component.
    '''

    # A passed component is not a scan argument.
    session, _, resolver = _session()
    result = session.run(
        'scan',
        source_file='a.py',
        component='domain',
        output='out.yml',
    )

    # The emit tokens are the lexical return. The return is the emit return.
    lexical = resolver.results[_LEXICAL]
    assert _kwargs_for(resolver, _LEXICAL) == {'source_file': 'a.py'}
    emit = _kwargs_for(resolver, 'emit_scan_result_event')
    assert emit['tokens'] is lexical
    assert emit['source_file'] == 'a.py'
    assert emit['output'] == 'out.yml'
    assert 'component' not in emit
    assert 'cache' not in emit
    assert 'provision_prefix' not in emit
    assert result is resolver.results['emit_scan_result_event']
    assert result is not lexical

    # An empty emit return is still the return.
    empty_session, _, _ = _session(resolver=_resolver(results={'emit_scan_result_event': ''}))
    assert empty_session.run('scan') == ''

# ** test: parse_hands_syntactic_return
def test_parse_hands_syntactic_return() -> None:
    '''
    Test that parse hands the lexical and syntactic returns forward by identity.
    '''

    # The empty emit sentinel must remain the return, not a replacement.
    resolver = _resolver(results={'emit_parse_result_event': ''})
    session, _, _ = _session(resolver=resolver)
    result = session.run(
        'parse',
        source_file='a.py',
        include_tokens=True,
        extract='name',
    )

    # Syntactic tokens are the lexical return. The emit ast is the syntactic return.
    lexical = resolver.results[_LEXICAL]
    syntactic = resolver.results[_SYNTACTIC]
    assert _kwargs_for(resolver, _SYNTACTIC)['tokens'] is lexical
    emit = _kwargs_for(resolver, 'emit_parse_result_event')
    assert emit['ast'] is syntactic
    assert emit['tokens'] is lexical
    assert emit['include_tokens'] is True
    assert emit['extract'] == 'name'
    assert result == ''
    assert result is resolver.results['emit_parse_result_event']

    # Tokens are not passed to the emit unless include_tokens was supplied.
    plain_session, _, plain = _session()
    plain_session.run('parse', source_file='a.py')
    assert 'tokens' not in _kwargs_for(plain, 'emit_parse_result_event')

# ** test: parse_skips_scan_emit
def test_parse_skips_scan_emit() -> None:
    '''
    Test that parse does not resolve the scan emit or call scan.
    '''

    # A replaced scan raises if it is called.
    session, _, resolver = _session()
    called = _forbid(session, 'scan')
    session.run('parse', include_tokens=True)
    assert called == []
    assert 'emit_scan_result_event' not in resolver.resolved

# ** test: parse_skips_scan
def test_parse_skips_scan() -> None:
    '''
    Test that parse calls the two analysis parts and not scan or semantic.
    '''

    # Every later or sibling method raises if it is called.
    session, _, resolver = _session()
    called = _forbid(session, 'scan', 'semantic', 'compile', 'compile_from_ast')
    session.run('parse', source_file='a.py')
    assert called == []
    assert resolver.resolved[:2] == [_LEXICAL, _SYNTACTIC]

# ** test: syntactic_analysis_requires_tokens
def test_syntactic_analysis_requires_tokens() -> None:
    '''
    Test that a missing tokens argument is a TypeError, not a second lex.
    '''

    # Calling the part without tokens fails before any resolve.
    session, _, resolver = _session()
    called = _forbid(session, 'lexical_analysis')
    with pytest.raises(TypeError):
        session.syntactic_analysis(source_file='a.py')
    assert called == []
    assert resolver.resolved == []

    # A given tokens object is passed by identity.
    tokens = object()
    session.syntactic_analysis(tokens, source_file='a.py')
    assert resolver.resolved == [_SYNTACTIC]
    assert _kwargs_for(resolver, _SYNTACTIC)['tokens'] is tokens

# ** test: semantic_skips_earlier_emits
def test_semantic_skips_earlier_emits() -> None:
    '''
    Test that semantic hands the syntactic return forward and emits once.
    '''

    # A caller prefix must not replace the imported constant.
    session, cache, resolver = _session()
    result = session.run(
        'semantic',
        component='domain',
        source_file='a.py',
        provision_prefix=('not', 'the', 'prefix'),
        feature_id='semantic.module',
        request=object(),
        marker='x',
    )

    # Earlier emits do not run. Only the domain dialect is resolved.
    assert 'emit_scan_result_event' not in resolver.resolved
    assert 'emit_parse_result_event' not in resolver.resolved
    syntactic = resolver.results[_SYNTACTIC]
    analyzed = resolver.results[_ANALYSIS]
    common = resolver.results[_COMMON]
    dialect = resolver.results['check_domain_conformance_event']

    # Analysis and both checks see that ast, the cache, and the one prefix.
    analysis = _kwargs_for(resolver, _ANALYSIS)
    assert analysis['ast'] is syntactic
    assert analysis['cache'] is cache
    assert analysis['provision_prefix'] is COMPILER_PROVISION_CACHE_PREFIX
    assert 'source_file' not in analysis
    common_kwargs = _kwargs_for(resolver, _COMMON)
    assert common_kwargs['ast'] is syntactic
    assert common_kwargs['semantic'] is analyzed
    assert common_kwargs['cache'] is cache
    assert common_kwargs['provision_prefix'] is COMPILER_PROVISION_CACHE_PREFIX
    dialect_kwargs = _kwargs_for(resolver, 'check_domain_conformance_event')
    assert dialect_kwargs['findings'] is common
    assert dialect_kwargs['ast'] is syntactic
    assert dialect_kwargs['semantic'] is analyzed
    assert dialect_kwargs['cache'] is cache
    assert dialect_kwargs['provision_prefix'] is COMPILER_PROVISION_CACHE_PREFIX

    # The emit receives the syntactic return, not a dump, and no include_ast.
    emit = _kwargs_for(resolver, 'emit_semantic_result_event')
    assert emit['ast'] is syntactic
    assert emit['semantic'] is analyzed
    assert emit['findings'] is dialect
    for absent in ('include_ast', 'feature_id', 'request', 'marker', 'step', 'provision_prefix'):
        assert absent not in emit
    assert result is resolver.results['emit_semantic_result_event']

    # include_ast is forwarded only when supplied.
    flagged, _, flagged_resolver = _session()
    flagged.run('semantic', component='domain', include_ast=False, source_file='a.py')
    flagged_emit = _kwargs_for(flagged_resolver, 'emit_semantic_result_event')
    assert flagged_emit['include_ast'] is False
    assert flagged_emit['ast'] is flagged_resolver.results[_SYNTACTIC]

# ** test: semantic_skips_scan_and_parse
def test_semantic_skips_scan_and_parse() -> None:
    '''
    Test that semantic does not call scan, parse, or distillation.
    '''

    # The replaced methods raise if they are called.
    session, _, resolver = _session()
    called = _forbid(session, 'scan', 'parse', 'distillation', 'compile')
    session.run('semantic', component='domain', source_file='a.py')
    assert called == []
    assert resolver.resolved[-1] == 'emit_semantic_result_event'

# ** test: compile_continues_after_findings
def test_compile_continues_after_findings() -> None:
    '''
    Test that compile skips earlier emits and still distills.
    '''

    # A non-empty findings sentinel must not skip distillation.
    resolver = _resolver(results={'check_utils_conformance_event': ['kept']})
    session, _, _ = _session(resolver=resolver)
    result = session.run('compile', component='utils', source_file='a.py')

    # The three earlier emits stay unresolved. The codegen tail runs.
    for absent in ('emit_scan_result_event', 'emit_parse_result_event', 'emit_semantic_result_event'):
        assert absent not in resolver.resolved
    assert resolver.resolved[-3:] == list(_CODEGEN_TAIL)
    syntactic = resolver.results[_SYNTACTIC]
    generated = _kwargs_for(resolver, 'generate_code_event')
    assert generated == {'ast': syntactic, 'component': 'utils'}
    assert generated['ast'] is syntactic
    optimized = _kwargs_for(resolver, 'optimize_code_event')
    assert 'O' not in optimized
    assert optimized['codegen'] is resolver.results['generate_code_event']
    emitted = _kwargs_for(resolver, 'emit_codegen_result_event')
    assert emitted['codegen'] is resolver.results['optimize_code_event']
    assert emitted['source_file'] == 'a.py'
    assert result is resolver.results['emit_codegen_result_event']

    # The asked component is passed through, including events, and O only when asked.
    events_session, _, events = _session()
    events_session.run('compile', component='events', optimization='O1')
    assert _kwargs_for(events, 'generate_code_event')['component'] == 'events'
    assert _kwargs_for(events, 'optimize_code_event')['O'] == 'O1'
    assert 'optimization' not in _kwargs_for(events, 'optimize_code_event')

# ** test: compile_skips_semantic
def test_compile_skips_semantic() -> None:
    '''
    Test that compile calls distillation and not semantic, scan, or parse.
    '''

    # The replaced methods raise if they are called.
    session, _, _ = _session()
    called = _forbid(session, 'scan', 'parse', 'semantic')
    distilled = []
    sentinel = object()

    def distillation(ast, component, **kwargs):
        distilled.append((ast, component, dict(kwargs)))
        return sentinel

    session.distillation = distillation
    result = session.run('compile', component='utils', source_file='a.py')
    assert called == []
    assert result is sentinel
    assert len(distilled) == 1
    assert distilled[0][0] is session.feature.get_dependency.results[_SYNTACTIC]
    assert distilled[0][1] == 'utils'
    assert distilled[0][2] == {'source_file': 'a.py'}

# ** test: compile_from_ast_uses_load_return
def test_compile_from_ast_uses_load_return() -> None:
    '''
    Test that compile-from-ast loads, then analyzes, and does not reparse.
    '''

    # The load return is the ast for analysis and for generate.
    session, _, resolver = _session()
    result = session.run('compile-from-ast', component='assets', source_file='saved.json')

    # No lexical event, no syntactic event, and no semantic emit.
    assert resolver.resolved[0] == 'load_from_ast_event'
    for absent in (_LEXICAL, _SYNTACTIC, 'emit_semantic_result_event'):
        assert absent not in resolver.resolved
    loaded = resolver.results['load_from_ast_event']
    assert _kwargs_for(resolver, 'load_from_ast_event') == {'source_file': 'saved.json'}
    assert _kwargs_for(resolver, _ANALYSIS)['ast'] is loaded
    assert _kwargs_for(resolver, _COMMON)['ast'] is loaded
    assert _kwargs_for(resolver, 'generate_code_event')['ast'] is loaded
    assert _kwargs_for(resolver, 'generate_code_event')['component'] == 'assets'
    assert result is resolver.results['emit_codegen_result_event']

# ** test: compile_from_ast_skips_lex_and_compile
def test_compile_from_ast_skips_lex_and_compile() -> None:
    '''
    Test that compile-from-ast does not call the source analysis parts or compile.
    '''

    # The replaced methods raise if they are called.
    session, _, resolver = _session()
    called = _forbid(
        session,
        'lexical_analysis',
        'syntactic_analysis',
        'scan',
        'parse',
        'semantic',
        'compile',
    )
    session.run('compile-from-ast', component='assets')
    assert called == []
    assert resolver.resolved[-1] == 'emit_codegen_result_event'

# ** test: unknown_step_raises_before_resolve
@pytest.mark.parametrize('step', _UNKNOWN_STEPS)
def test_unknown_step_raises_before_resolve(step) -> None:
    '''
    Test that an unknown string raises from the session before any resolve.

    :param step: The unknown asked string.
    :type step: str
    '''

    # Catalog ids, a blank, and None are not asks. Do not translate them.
    session, _, resolver = _session()
    with pytest.raises(TiferetError) as exc:
        session.run(step)
    assert exc.value.error_code == UNKNOWN_COMPILER_STEP
    assert exc.value.error_code == 'UNKNOWN_COMPILER_STEP'
    assert exc.value.error_code != 'ASKED_STEP_UNKNOWN'
    assert exc.value.kwargs['step'] == step
    assert _payload(exc)['message'] == f'Unknown compiler step: {step!r}.'
    assert resolver.resolved == []

# ** test: component_required_before_resolve
def test_component_required_before_resolve() -> None:
    '''
    Test that a bad component fails before any resolve, and only where required.
    '''

    # A missing key is reported as None. An empty string is not stripped.
    cases = (
        ('semantic', {}, None),
        ('compile', {'component': ''}, ''),
        ('compile-from-ast', {'component': 'widget'}, 'widget'),
    )
    for step, kwargs, component in cases:
        session, _, resolver = _session()
        with pytest.raises(TiferetError) as exc:
            session.run(step, **kwargs)
        assert exc.value.error_code == 'COMPONENT_REQUIRED'
        assert exc.value.kwargs['step'] == step
        assert exc.value.kwargs['component'] == component
        assert _payload(exc)['message'] == (
            f"Asked step '{step}' requires one of the ten component strings. "
            f'Got {component}.'
        )
        assert resolver.resolved == []

    # A missing component is not an error on scan and parse.
    session, _, resolver = _session()
    session.run('scan')
    session.run('parse')
    assert _LEXICAL in resolver.resolved

# ** test: method_sources_include_parts
def test_method_sources_include_parts() -> None:
    '''
    Test that later methods name the earlier parts and not their event ids.
    '''

    # Read each method body as written.
    def source(name):
        return inspect.getsource(getattr(CompilerAppSessionContext, name))

    # parse includes the two analysis parts and not scan.
    parse = source('parse')
    assert 'lexical_analysis' in parse
    assert 'syntactic_analysis' in parse
    assert 'perform_lexical_analysis_event' not in parse
    assert 'self.scan' not in parse

    # semantic includes the parts and not the earlier asked steps.
    semantic = source('semantic')
    assert 'self.conformance' in semantic
    assert 'self.scan' not in semantic
    assert 'self.parse' not in semantic

    # compile includes distillation and not the codegen ids or semantic.
    compile_source = source('compile')
    assert 'distillation' in compile_source
    assert 'generate_code_event' not in compile_source
    assert 'emit_semantic_result_event' not in compile_source
    assert 'self.semantic' not in compile_source

    # compile_from_ast loads and does not include the source parts or compile.
    from_ast = source('compile_from_ast')
    assert 'load_from_ast_event' in from_ast
    assert 'lexical_analysis' not in from_ast
    assert 'self.compile' not in from_ast

    # syntactic_analysis does not include the lexical part.
    assert 'lexical_analysis' not in source('syntactic_analysis')

# ** test: session_source_forbidden_strings
def test_session_source_forbidden_strings() -> None:
    '''
    Test that the session source names the feature context and no catalog walk.
    '''

    # The forbidden names are absent from the module text.
    source = _SESSION_PATH.read_text(encoding='utf-8')
    for forbidden in _FORBIDDEN_SOURCE:
        assert forbidden not in source
    assert 'CompilerFeatureContext' in source
