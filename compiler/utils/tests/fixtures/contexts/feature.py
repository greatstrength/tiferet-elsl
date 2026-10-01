"""Tiferet feature contexts."""

# *** imports

# ** app
from .core import BaseContext
from ..domain.feature import Feature
from ..events.feature import CompileFeature

# *** contexts

# ** context: feature_context
class FeatureContext(BaseContext):
    '''
    Run one feature's steps through the injected resolver.
    '''

    # * attribute: domain_type
    domain_type = Feature

    # * method: resolve_step_event
    def resolve_step_event(self, step):
        '''
        Resolve the event for one step.

        :param step: The feature step.
        :type step: object
        :return: The compile event.
        :rtype: object
        '''

        # The imported event names the compile boundary.
        return CompileFeature
