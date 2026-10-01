"""Tiferet file utility."""

# *** imports

# ** app
from ..interfaces.file import FileService

# *** constants

# ** constant: file_not_found_id
FILE_NOT_FOUND_ID = 'FILE_NOT_FOUND'

# *** utils

# ** util: file_loader
class FileLoader(FileService):
    '''
    Open a file stream and close it when the caller leaves the block.
    '''

    # * method: __enter__ (context manager)
    def __enter__(self):
        '''
        Open the stream.

        :return: This loader.
        :rtype: FileLoader
        '''

        # The open stream is this loader.
        return self

    # * method: __exit__ (context manager)
    def __exit__(self, exc_type, exc, tb):
        '''
        Close the stream.

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

    # * method: verify_file (static)
    @staticmethod
    def verify_file(path):
        '''
        Verify a path exists.

        :param path: The file path.
        :type path: str
        :return: The path.
        :rtype: str
        '''

        # The path is already the answer.
        return path
