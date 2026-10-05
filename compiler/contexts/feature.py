"""Compiler Feature Contexts"""

# *** imports

# ** core
from typing import Any, Callable, Dict, Tuple

# ** infra
from tiferet.assets import TiferetError
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.feature import FeatureContext

# ** app
from .provision import COMPILER_PROVISION_CACHE_PREFIX

# *** constants

# ** constant: asked_steps
ASKED_STEPS: Tuple[str, ...] = (
    'scan',
    'parse',
    'semantic',
    'compile',
    'compile-from-ast',
)

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

# ** constant: asked_step_unknown_id
ASKED_STEP_UNKNOWN_ID: str = 'ASKED_STEP_UNKNOWN'

# ** constant: component_required_id
COMPONENT_REQUIRED_ID: str = 'COMPONENT_REQUIRED'

# ** constant: resolver_required_id
RESOLVER_REQUIRED_ID: str = 'RESOLVER_REQUIRED'

# ** constant: event_not_resolved_id
EVENT_NOT_RESOLVED_ID: str = 'EVENT_NOT_RESOLVED'

# ** constant: compiler_feature_lookup_refused_id
COMPILER_FEATURE_LOOKUP_REFUSED_ID: str = 'COMPILER_FEATURE_LOOKUP_REFUSED'

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

# ** context: compiler_feature_context
class CompilerFeatureContext(FeatureContext):
    '''
    Run an asked compiler step by calling its events in code.

    The asked string is the program. A catalog row is not a branch, and
    this context does not register over the feature domain type.
    '''

    # * init
    def __init__(self, cache: CacheContext, get_dependency: Callable) -> None:
        '''
        Store the session cache and the injected resolver.

        :param cache: The session cache. This context does not seed it.
        :type cache: CacheContext
        :param get_dependency: The resolver for one service id.
        :type get_dependency: Callable
        '''

        # Store both arguments. Do not wrap the resolver.
        super().__init__(get_dependency=get_dependency, cache=cache)

    # * method: run_step
    def run_step(self, step: str, **kwargs) -> Any:
        '''
        Execute one asked step and return the last event result.

        :param step: One of scan, parse, semantic, compile, compile-from-ast.
        :type step: str
        :param kwargs: Caller keys forwarded only to the event that accepts them.
        :type kwargs: dict
        :return: The last event result for the asked step.
        :rtype: Any
        '''

        # An unknown string fails before any event is resolved.
        if step not in ASKED_STEPS:
            asked = ', '.join(ASKED_STEPS)
            TiferetError.raise_error(
                ASKED_STEP_UNKNOWN_ID,
                message=f"Asked step '{step}' is not one of: {asked}.",
                step=step,
            )

        # Semantic asks require one component string. Scan and parse do not.
        component = kwargs.get('component')
        if step in ('semantic', 'compile', 'compile-from-ast') and component not in DIALECT_SERVICE_ID:
            TiferetError.raise_error(
                COMPONENT_REQUIRED_ID,
                message=f"Asked step '{step}' requires one of the ten component strings. Got {component}.",
                step=step,
                component=component,
            )

        # Scan emits the lexical return and stops.
        if step == 'scan':
            tokens = self._resolve_and_execute(
                step,
                'perform_lexical_analysis_event',
                **_present_keys(kwargs, ('source_file',)),
            )
            return self._resolve_and_execute(
                step,
                'emit_scan_result_event',
                tokens=tokens,
                **_present_keys(kwargs, ('source_file', 'output', 'output_format')),
            )

        # A stored model is loaded. Source asks analyze without earlier emits.
        if step == 'compile-from-ast':
            ast = self._resolve_and_execute(
                step,
                'load_from_ast_event',
                **_present_keys(kwargs, ('source_file',)),
            )
        else:
            tokens = self._resolve_and_execute(
                step,
                'perform_lexical_analysis_event',
                **_present_keys(kwargs, ('source_file',)),
            )
            ast = self._resolve_and_execute(
                step,
                'perform_syntactic_analysis_event',
                tokens=tokens,
                **_present_keys(kwargs, ('source_file',)),
            )

        # Parse emits the syntactic return and stops.
        if step == 'parse':
            emit_kwargs = _present_keys(
                kwargs,
                ('source_file', 'output', 'output_format', 'include_tokens', 'extract'),
            )
            if 'include_tokens' in kwargs:
                emit_kwargs['tokens'] = tokens
            return self._resolve_and_execute(
                step,
                'emit_parse_result_event',
                ast=ast,
                **emit_kwargs,
            )

        # Analysis, common conformance, and one dialect share the same ast.
        semantic, findings = self._run_conformance(step, ast, component)

        # Only the semantic ask emits that result.
        if step == 'semantic':
            return self._resolve_and_execute(
                step,
                'emit_semantic_result_event',
                ast=ast,
                semantic=semantic,
                findings=findings,
                **_present_keys(kwargs, ('source_file', 'output', 'output_format', 'include_ast')),
            )

        # Compile continues into codegen. Findings do not stop it.
        return self._run_codegen(step, ast, component, kwargs)

    # * method: _resolve_and_execute
    def _resolve_and_execute(self, step: str, service_id: str, **event_kwargs) -> Any:
        '''
        Resolve one service id and call execute.

        :param step: The asked step, named if resolution fails.
        :type step: str
        :param service_id: The literal service id to resolve.
        :type service_id: str
        :param event_kwargs: Arguments for execute. Not resolution flags.
        :type event_kwargs: dict
        :return: The event result.
        :rtype: Any
        '''

        # A missing resolver is refused before the call.
        if self.get_dependency is None:
            TiferetError.raise_error(
                RESOLVER_REQUIRED_ID,
                message='CompilerFeatureContext requires get_dependency.',
            )

        # Resolve this id with no flags, immediately before execute.
        try:
            event = self.get_dependency(service_id)
        except Exception:
            TiferetError.raise_error(
                EVENT_NOT_RESOLVED_ID,
                message=f"Failed to resolve {service_id} for asked step '{step}'.",
                service_id=service_id,
                step=step,
            )

        # A missing event is not an execute.
        if event is None:
            TiferetError.raise_error(
                EVENT_NOT_RESOLVED_ID,
                message=f"Failed to resolve {service_id} for asked step '{step}'.",
                service_id=service_id,
                step=step,
            )

        # Call execute. Do not construct the event.
        return event.execute(**event_kwargs)

    # * method: _run_conformance
    def _run_conformance(self, step: str, ast: Any, component: str) -> Tuple[Any, Any]:
        '''
        Run semantic analysis, common conformance, and one dialect check.

        :param step: The asked step, named if resolution fails.
        :type step: str
        :param ast: The syntactic or loaded declaration.
        :type ast: Any
        :param component: One of the ten component strings.
        :type component: str
        :return: The semantic result and the dialect findings.
        :rtype: tuple
        '''

        # Analysis and both checks see the same cache and the one prefix.
        semantic = self._resolve_and_execute(
            step,
            'perform_semantic_analysis_event',
            ast=ast,
            cache=self.cache,
            provision_prefix=COMPILER_PROVISION_CACHE_PREFIX,
        )
        common = self._resolve_and_execute(
            step,
            'check_common_conformance_event',
            ast=ast,
            semantic=semantic,
            cache=self.cache,
            provision_prefix=COMPILER_PROVISION_CACHE_PREFIX,
        )
        findings = self._resolve_and_execute(
            step,
            DIALECT_SERVICE_ID[component],
            ast=ast,
            semantic=semantic,
            findings=common,
            cache=self.cache,
            provision_prefix=COMPILER_PROVISION_CACHE_PREFIX,
        )

        # Findings do not choose the next event.
        return semantic, findings

    # * method: _run_codegen
    def _run_codegen(self,
                     step: str,
                     ast: Any,
                     component: str,
                     kwargs: dict) -> Any:
        '''
        Generate, optimize, and emit from the analysis declaration.

        :param step: The asked step, named if resolution fails.
        :type step: str
        :param ast: The syntactic or loaded declaration.
        :type ast: Any
        :param component: The asked component string.
        :type component: str
        :param kwargs: Caller keys. Only a supplied optimization is forwarded.
        :type kwargs: dict
        :return: The codegen emit result.
        :rtype: Any
        '''

        # Generate from the analysis declaration, not an emit payload.
        generated = self._resolve_and_execute(
            step,
            'generate_code_event',
            ast=ast,
            component=component,
        )

        # Pass a level only when the caller supplied optimization.
        optimize_kwargs = {'codegen': generated}
        if 'optimization' in kwargs:
            optimize_kwargs['O'] = kwargs['optimization']
        optimized = self._resolve_and_execute(
            step,
            'optimize_code_event',
            **optimize_kwargs,
        )

        # The optimizer return is what the emit keeps.
        return self._resolve_and_execute(
            step,
            'emit_codegen_result_event',
            codegen=optimized,
            **_present_keys(kwargs, ('source_file', 'output', 'output_format')),
        )

    # * method: execute_feature
    def execute_feature(self, request: Any = None, *flags, **kwargs) -> None:
        '''
        Refuse the inherited feature walk.

        :param request: Ignored. This context has no request.
        :type request: Any
        :param flags: Ignored execution flags.
        :type flags: tuple
        :param kwargs: Ignored keyword arguments.
        :type kwargs: dict
        :return: Never returns.
        :rtype: None
        '''

        # The ask is run_step. Do not delegate.
        self._refuse_lookup('execute_feature')

    # * method: resolve_feature_steps
    def resolve_feature_steps(self, request: Any = None, *execution_flags) -> None:
        '''
        Refuse to walk configured steps.

        :param request: Ignored.
        :type request: Any
        :param execution_flags: Ignored execution flags.
        :type execution_flags: tuple
        :return: Never returns.
        :rtype: None
        '''

        # The sequences are code in run_step.
        self._refuse_lookup('resolve_feature_steps')

    # * method: resolve_step_event
    def resolve_step_event(self, step: Any = None, feature_flags: Any = None) -> None:
        '''
        Refuse to resolve an event from a configured step.

        :param step: Ignored configured step.
        :type step: Any
        :param feature_flags: Ignored flags.
        :type feature_flags: Any
        :return: Never returns.
        :rtype: None
        '''

        # Resolution is a literal service id, not a configured step.
        self._refuse_lookup('resolve_step_event')

    # * method: from_domain
    @classmethod
    def from_domain(cls, domain_obj: Any = None, **kwargs) -> None:
        '''
        Refuse registry construction.

        :param domain_obj: Ignored. This context is not bound that way.
        :type domain_obj: Any
        :param kwargs: Ignored constructor arguments.
        :type kwargs: dict
        :return: Never returns.
        :rtype: None
        '''

        # Construction is the constructor, not a domain binding.
        cls._refuse_lookup('from_domain')

    # * method: _refuse_lookup (static)
    @staticmethod
    def _refuse_lookup(method: str) -> None:
        '''
        Raise the lookup refusal for one inherited method.

        :param method: The refused method name.
        :type method: str
        :return: Never returns.
        :rtype: None
        '''

        # Name the method. Do not delegate to the inherited implementation.
        TiferetError.raise_error(
            COMPILER_FEATURE_LOOKUP_REFUSED_ID,
            message=f'CompilerFeatureContext does not resolve a feature. Refused {method}.',
            method=method,
        )
