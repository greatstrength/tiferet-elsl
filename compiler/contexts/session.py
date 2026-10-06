"""Compiler Session Contexts"""

# *** imports

# ** core
from typing import Any, Callable

# ** infra
from tiferet.contexts.app import AppSessionContext
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.core import BaseContext

# *** contexts

# ** context: compiler_app_session_context
class CompilerAppSessionContext(AppSessionContext):
    '''
    Hold the cache and the step handler for one compiler session.

    The session asks a step. It does not construct the step context, and
    it does not register over the app session domain type.
    '''

    # * attribute: cache
    cache: CacheContext

    # * attribute: get_feature
    get_feature: Callable

    # * init
    def __init__(self, cache: CacheContext, get_feature: Callable) -> None:
        '''
        Store the cache and the injected step handler.

        :param cache: The session cache. This context does not seed it.
        :type cache: CacheContext
        :param get_feature: The handler that returns a step context.
        :type get_feature: Callable
        '''

        # Initialize the base context. Do not call the hub constructor.
        BaseContext.__init__(self)

        # Store both arguments. Do not store a resolver.
        self.cache = cache
        self.get_feature = get_feature

    # * method: run
    def run(self, step: str, **kwargs) -> Any:
        '''
        Ask one step and return the feature result.

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
        Call the injected handler and ask it to run the step.

        :param step: The asked compiler step.
        :type step: str
        :param kwargs: Caller keys forwarded unpacked to the step.
        :type kwargs: dict
        :return: The step result, unwrapped.
        :rtype: Any
        '''

        # The handler owns an unknown step. This method does not check it.
        return self.get_feature(step).run_step(step, **kwargs)
