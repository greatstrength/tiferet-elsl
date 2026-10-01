"""Tiferet interfaces CLI."""

# *** imports

# ** app
from .core import Service

# *** interfaces

# ** interface: cli_service
class CliService(Service):
    '''
    Parse a command line without the caller knowing the parser.
    '''

    # * method: parse
    @abstractmethod
    def parse(self, argv):
        '''
        Parse one argument vector.

        :param argv: The argument vector.
        :type argv: list
        :return: The parsed arguments.
        :rtype: object
        '''

        # The implementation supplies the body.
        raise NotImplementedError('parse')
