"""Tiferet SQLite utility."""

# *** imports

# ** app
from ..interfaces.sqlite import SqliteService
from ..mappers.sqlite import Row

# *** utils

# ** util: sqlite_client
class SqliteClient(SqliteService):
    '''
    Hold a connection for the length of a with-block.
    '''

    # * method: __enter__ (context manager)
    def __enter__(self):
        '''
        Open the connection.

        :return: This client.
        :rtype: SqliteClient
        '''

        # The open connection is this client.
        return self

    # * method: __exit__ (context manager)
    def __exit__(self, exc_type, exc, tb):
        '''
        Close the connection.

        :param exc_type: The exception type, if any.
        :type exc_type: type
        :param exc: The exception instance, if any.
        :type exc: BaseException
        :param tb: The traceback, if any.
        :type tb: object
        :return: None
        :rtype: None
        '''

        # Closing is a no-op in this fixture.
        return None

    # * method: execute
    def execute(self, statement: str):
        '''
        Execute one statement.

        :param statement: The SQL statement.
        :type statement: str
        :return: The mapped row type.
        :rtype: Row
        '''

        # The statement names the row type.
        return statement
