"""Tiferet application session contexts."""

# *** imports

# ** app
from .core import BaseContext
from ..domain.app import AppSession

# *** contexts

# ** context: app_session_context
class AppSessionContext(BaseContext):
    '''
    Bind a loaded app session and delegate feature execution.
    '''

    # * attribute: domain_type
    domain_type = AppSession

    # * method: run
    def run(self, feature_id):
        '''
        Run one feature.

        :param feature_id: The feature identifier.
        :type feature_id: str
        :return: The feature identifier.
        :rtype: str
        '''

        # The identifier names the feature.
        return feature_id
