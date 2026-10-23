"""Compiler Session Contexts"""

# *** imports

# ** core
from typing import Any, Callable, Dict, Tuple

# ** infra
from tiferet.assets import TiferetError
from tiferet.contexts.app import AppSessionContext
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.core import BaseContext

# ** app
from .feature import CompilerFeatureContext
from .provision import COMPILER_PROVISION_CACHE_PREFIX

# *** constants

# ** constant: asked_methods
ASKED_METHODS: Dict[str, str] = {
    'scan': 'scan',
    'parse': 'parse',
    'semantic': 'semantic',
    'compile': 'compile',
    'compile-from-ast': 'compile_from_ast',
}

# ** constant: dialect_service_id
DIALECT_SERVICE_ID: Dict[str, str] = {
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

# ** constant: unknown_compiler_step
UNKNOWN_COMPILER_STEP: str = 'UNKNOWN_COMPILER_STEP'

# ** constant: component_required_id
COMPONENT_REQUIRED_ID: str = 'COMPONENT_REQUIRED'

# *** functions

# ** function: _present_keys
def _present_keys(kwargs: dict, names: Tuple[str, ...]) -> dict:
    '''
    Copy caller keys that were actually supplied.

    Absent keys stay omitted. This helper does not invent a default.

    :param kwargs: The caller keyword arguments.
    :type kwargs: dict
    :param names: Keys that may be forwarded.
    :type names: tuple
    :return: The supplied keys.
    :rtype: dict
    '''

    # Keep only keys the caller passed. Do not case-fold or strip.
    return {
        name: kwargs[name]
        for name in names
        if name in kwargs
    }

# *** contexts

# ** context: compiler_app_session_context
class CompilerAppSessionContext(AppSessionContext):
    '''
    Own the five compiler pipelines as methods that include each other.

    A later method calls the earlier analysis part and passes its return
    as an argument. The session does not register over the app session
    domain type.
    '''

    # * attribute: cache
    cache: CacheContext

    # * attribute: feature
    feature: CompilerFeatureContext

    # * init
    def __init__(self, cache: CacheContext, get_dependency: Callable) -> None:
        '''
        Store the cache and build the one feature context for this session.

        :param cache: The session cache. This context does not seed it.
        :type cache: CacheContext
        :param get_dependency: The resolver handed to the feature context.
        :type get_dependency: Callable
        '''

        # Initialize the base context. Do not call the hub constructor.
        BaseContext.__init__(self)

        # Store the cache. The feature context holds the resolver.
        self.cache = cache
        self.feature = CompilerFeatureContext(
            cache=cache,
            get_dependency=get_dependency,
        )

    # * method: run
    def run(self, step: str, **kwargs) -> Any:
        '''
        Ask one step and return its result.

        :param step: The asked compiler step.
        :type step: str
        :param kwargs: Caller keys forwarded to the step.
        :type kwargs: dict
        :return: The step result.
        :rtype: Any
        '''

        # Delegate to this session. Do not call the hub run.
        return self.execute_feature(step, **kwargs)

    # * method: execute_feature
    def execute_feature(self, step: str, **kwargs) -> Any:
        '''
        Dispatch the asked string to its method and return that result.

        :param step: One of the five asked strings.
        :type step: str
        :param kwargs: Caller keys forwarded unpacked to the method.
        :type kwargs: dict
        :return: The method result, unwrapped.
        :rtype: Any
        '''

        # An unknown string fails before any event is resolved.
        if step not in ASKED_METHODS:
            TiferetError.raise_error(
                UNKNOWN_COMPILER_STEP,
                message=f'Unknown compiler step: {step!r}.',
                step=step,
            )

        # Call the mapped method and return its result.
        return getattr(self, ASKED_METHODS[step])(**kwargs)

    # * method: lexical_analysis
    def lexical_analysis(self, **kwargs) -> Any:
        '''
        Run lexical analysis and return the tokens. This part does not emit.

        :param kwargs: Caller keys. Only a supplied source_file is forwarded.
        :type kwargs: dict
        :return: The lexical analysis result.
        :rtype: Any
        '''

        # Resolve the lexer event and return its result.
        return self.feature.resolve_and_execute(
            'perform_lexical_analysis_event',
            **_present_keys(kwargs, ('source_file',)),
        )

    # * method: syntactic_analysis
    def syntactic_analysis(self, tokens: Any, **kwargs) -> Any:
        '''
        Run syntactic analysis on the given tokens. This part does not emit.

        :param tokens: The tokens to analyze, passed as given.
        :type tokens: Any
        :param kwargs: Caller keys. Only a supplied source_file is forwarded.
        :type kwargs: dict
        :return: The syntactic analysis result.
        :rtype: Any
        '''

        # The parser event receives the tokens argument, not an emit payload.
        return self.feature.resolve_and_execute(
            'perform_syntactic_analysis_event',
            tokens=tokens,
            **_present_keys(kwargs, ('source_file',)),
        )

    # * method: conformance
    def conformance(self, ast: Any, component: str) -> Tuple[Any, Any]:
        '''
        Run semantic analysis, common conformance, and one dialect check.

        :param ast: The syntactic or loaded declaration.
        :type ast: Any
        :param component: One of the ten component strings.
        :type component: str
        :return: The semantic analysis result and the dialect findings.
        :rtype: tuple
        '''

        # Semantic analysis receives the ast, the cache, and the one prefix.
        analyzed = self.feature.resolve_and_execute(
            'perform_semantic_analysis_event',
            ast=ast,
            cache=self.cache,
            provision_prefix=COMPILER_PROVISION_CACHE_PREFIX,
        )

        # Common conformance receives that ast and the analysis return.
        common = self.feature.resolve_and_execute(
            'check_common_conformance_event',
            ast=ast,
            semantic=analyzed,
            cache=self.cache,
            provision_prefix=COMPILER_PROVISION_CACHE_PREFIX,
        )

        # One dialect receives the common return as findings.
        findings = self.feature.resolve_and_execute(
            DIALECT_SERVICE_ID[component],
            ast=ast,
            semantic=analyzed,
            findings=common,
            cache=self.cache,
            provision_prefix=COMPILER_PROVISION_CACHE_PREFIX,
        )

        # Findings do not choose the next event.
        return analyzed, findings

    # * method: distillation
    def distillation(self, ast: Any, component: str, **kwargs) -> Any:
        '''
        Generate, optimize, and emit code from the analysis declaration.

        :param ast: The syntactic or loaded declaration.
        :type ast: Any
        :param component: The asked component string.
        :type component: str
        :param kwargs: Caller keys. Only supplied keys are forwarded.
        :type kwargs: dict
        :return: The codegen emit result.
        :rtype: Any
        '''

        # Generate from the analysis declaration, not an emit payload.
        generated = self.feature.resolve_and_execute(
            'generate_code_event',
            ast=ast,
            component=component,
        )

        # Pass a level only when the caller supplied optimization.
        optimize_kwargs = {'codegen': generated}
        if 'optimization' in kwargs:
            optimize_kwargs['O'] = kwargs['optimization']
        optimized = self.feature.resolve_and_execute(
            'optimize_code_event',
            **optimize_kwargs,
        )

        # The optimizer return is what the emit keeps.
        return self.feature.resolve_and_execute(
            'emit_codegen_result_event',
            codegen=optimized,
            **_present_keys(kwargs, ('source_file', 'output', 'output_format')),
        )

    # * method: scan
    def scan(self, **kwargs) -> Any:
        '''
        Tokenize, then emit that return and stop.

        :param kwargs: Caller keys. Only supplied keys are forwarded.
        :type kwargs: dict
        :return: The scan emit result.
        :rtype: Any
        '''

        # The lexical part returns the object the emit receives.
        tokens = self.lexical_analysis(**kwargs)

        # Emit that return. Do not replace it.
        return self.feature.resolve_and_execute(
            'emit_scan_result_event',
            tokens=tokens,
            **_present_keys(kwargs, ('source_file', 'output', 'output_format')),
        )

    # * method: parse
    def parse(self, **kwargs) -> Any:
        '''
        Tokenize and parse, then emit the syntactic return and stop.

        :param kwargs: Caller keys. Only supplied keys are forwarded.
        :type kwargs: dict
        :return: The parse emit result.
        :rtype: Any
        '''

        # Include the two analysis parts. Do not run the scan emit.
        tokens = self.lexical_analysis(**kwargs)
        ast = self.syntactic_analysis(tokens, **_present_keys(kwargs, ('source_file',)))

        # Emit the syntactic return. Pass tokens only when they were asked for.
        emit_kwargs = _present_keys(
            kwargs,
            ('source_file', 'output', 'output_format', 'include_tokens', 'extract'),
        )
        if 'include_tokens' in kwargs:
            emit_kwargs['tokens'] = tokens
        return self.feature.resolve_and_execute(
            'emit_parse_result_event',
            ast=ast,
            **emit_kwargs,
        )

    # * method: semantic
    def semantic(self, **kwargs) -> Any:
        '''
        Analyze and check one component, then emit that result.

        :param kwargs: Caller keys. A component string is required.
        :type kwargs: dict
        :return: The semantic emit result.
        :rtype: Any
        '''

        # A missing or unknown component fails before any event is resolved.
        component = kwargs.get('component')
        self._require_component('semantic', component)

        # Include the analysis parts. Do not run an earlier emit.
        tokens = self.lexical_analysis(**kwargs)
        ast = self.syntactic_analysis(tokens, **_present_keys(kwargs, ('source_file',)))
        analyzed, findings = self.conformance(ast, component)

        # Emit the syntactic return with the analysis and the dialect findings.
        return self.feature.resolve_and_execute(
            'emit_semantic_result_event',
            ast=ast,
            semantic=analyzed,
            findings=findings,
            **_present_keys(kwargs, ('source_file', 'output', 'output_format', 'include_ast')),
        )

    # * method: compile
    def compile(self, **kwargs) -> Any:
        '''
        Analyze and check one component, then distill it.

        :param kwargs: Caller keys. A component string is required.
        :type kwargs: dict
        :return: The distillation result.
        :rtype: Any
        '''

        # A missing or unknown component fails before any event is resolved.
        component = kwargs.get('component')
        self._require_component('compile', component)

        # Include the analysis parts. Findings do not skip distillation.
        tokens = self.lexical_analysis(**kwargs)
        ast = self.syntactic_analysis(tokens, **_present_keys(kwargs, ('source_file',)))
        self.conformance(ast, component)

        # Distill the syntactic return and return that result.
        return self.distillation(
            ast,
            component,
            **_present_keys(kwargs, ('optimization', 'source_file', 'output', 'output_format')),
        )

    # * method: compile_from_ast
    def compile_from_ast(self, **kwargs) -> Any:
        '''
        Load a stored model, check one component, then distill it.

        :param kwargs: Caller keys. A component string is required.
        :type kwargs: dict
        :return: The distillation result.
        :rtype: Any
        '''

        # A missing or unknown component fails before the load is resolved.
        component = kwargs.get('component')
        self._require_component('compile-from-ast', component)

        # The load return is the declaration for both later parts.
        ast = self.feature.resolve_and_execute(
            'load_from_ast_event',
            **_present_keys(kwargs, ('source_file',)),
        )

        # Check the loaded declaration. Findings do not skip distillation.
        self.conformance(ast, component)

        # Distill the loaded declaration and return that result.
        return self.distillation(
            ast,
            component,
            **_present_keys(kwargs, ('optimization', 'source_file', 'output', 'output_format')),
        )

    # * method: _require_component
    def _require_component(self, step: str, component: Any) -> None:
        '''
        Refuse a missing or unknown component string.

        :param step: The asked step, named in the error.
        :type step: str
        :param component: The caller component, or None when it was missing.
        :type component: Any
        :return: None.
        :rtype: None
        '''

        # A miss is reported as passed. Do not strip or case-fold.
        if component not in DIALECT_SERVICE_ID:
            TiferetError.raise_error(
                COMPONENT_REQUIRED_ID,
                message=f"Asked step '{step}' requires one of the ten component strings. Got {component}.",
                step=step,
                component=component,
            )
