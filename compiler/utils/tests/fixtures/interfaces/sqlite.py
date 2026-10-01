"""Tiferet interfaces SQLite."""

# *** imports

# ** app
from ..mappers.sqlite import Row
from .core import Service

# *** interfaces

# ** interface: sqlite_service
class SqliteService(Service):
    '''
    Run a statement without the caller holding the connection.
    '''

    # * method: execute
    @abstractmethod
    def execute(self, statement: str):
        '''
        Execute one statement.

        :param statement: The SQL statement.
        :type statement: str
        :return: The result rows.
        :rtype: list
        '''

        # The implementation supplies the body.
        raise NotImplementedError('execute')
