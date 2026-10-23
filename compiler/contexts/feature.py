"""Compiler Feature Contexts"""

# *** imports

# ** core
from typing import Any, Callable

# ** infra
from tiferet.assets import TiferetError
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.feature import FeatureContext

# *** constants

# ** constant: resolver_required_id
RESOLVER_REQUIRED_ID: str = 'RESOLVER_REQUIRED'

# ** constant: event_not_resolved_id
EVENT_NOT_RESOLVED_ID: str = 'EVENT_NOT_RESOLVED'

# ** constant: compiler_feature_lookup_refused_id
COMPILER_FEATURE_LOOKUP_REFUSED_ID: str = 'COMPILER_FEATURE_LOOKUP_REFUSED'

# *** contexts

# ** context: compiler_feature_context
class CompilerFeatureContext(FeatureContext):
    '''
    Resolve one service id and execute it.

    This context does not own a sequence. The compiler session calls it
    once per event, and it does not register over the feature domain type.
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

    # * method: resolve_and_execute
    def resolve_and_execute(self, service_id: str, **event_kwargs) -> Any:
        '''
        Resolve one service id and call execute.

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
                message=f'Failed to resolve {service_id}.',
                service_id=service_id,
            )

        # A missing event is not an execute.
        if event is None:
            TiferetError.raise_error(
                EVENT_NOT_RESOLVED_ID,
                message=f'Failed to resolve {service_id}.',
                service_id=service_id,
            )

        # Call execute. Do not construct the event.
        return event.execute(**event_kwargs)

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

        # The session dispatches the ask. Do not delegate.
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

        # The sequences are methods on the compiler session.
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
