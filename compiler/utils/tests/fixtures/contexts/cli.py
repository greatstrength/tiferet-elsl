"""Tiferet CLI contexts."""

# *** imports

# ** app
from .request import RequestContext
from .app import AppSessionContext

# *** contexts

# ** context: cli_request_context
class CliRequestContext(RequestContext):
    '''
    Convert a feature result for the command line without rebinding a domain type.
    '''

    # * method: handle_response
    def handle_response(self):
        '''
        Return the raw result.

        :return: None
        :rtype: None
        '''

        # The CLI printer owns the result.
        return None

# ** context: cli_session_context
class CliSessionContext(AppSessionContext):
    '''
    Extend the session hub with command-line concerns without rebinding a domain type.
    '''

    # * method: run
    def run(self, argv):
        '''
        Run one command.

        :param argv: The argument vector.
        :type argv: list
        :return: The argument vector.
        :rtype: list
        '''

        # The vector is the command.
        return argv
